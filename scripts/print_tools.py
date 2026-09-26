#!/usr/bin/env python3
"""Export and verify an OpenSCAD print project (skill openscad-print-project).

Project settings and project-specific checks live in print_project.py in the project root;
this script stays identical to the skill copy.

  build   export print parts, multicolour pieces and assembly bodies into build/
  check   build, then run every check; the STL folders and the report stay untouched
  export  check, then replace the STL folders, asm/ and the report with the verified exports

Dependencies: OpenSCAD on PATH, scripts/requirements.txt.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.metadata
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace

import manifold3d as md
import numpy as np
import trimesh

import holes


def find_root():
    for base in (Path(__file__).resolve().parents[1], Path.cwd()):
        if (base / "print_project.py").exists():
            return base
    sys.exit("print_project.py not found: expected in the project root (parent of scripts/) or the working directory")


ROOT = find_root()
sys.path.insert(0, str(ROOT))
import print_project as P  # noqa: E402

BUILD = ROOT / "build"
SOURCE = ROOT / P.SOURCE
# name -> (quantity in the full build, material, body count); quantity 0 = optional test print
PARTS = P.PARTS
# assembly body -> OpenSCAD call in installed position
ASSEMBLY = getattr(P, "ASSEMBLY", {})
# part -> inlay names; the model needs branches <part>_base and <part>_<inlay> in print orientation
COLOR_PARTS = getattr(P, "COLOR_PARTS", {})
COLOR_PIECES = [f"{name}_{piece}" for name, inlays in COLOR_PARTS.items() for piece in ("base", *inlays)]
NON_PRINT_BRANCHES = set(getattr(P, "NON_PRINT_BRANCHES", ("assembly", "exploded", "metrics", "none")))
STL_DIR = ROOT / getattr(P, "STL_DIR", "stl")
COLOR_DIR = ROOT / getattr(P, "COLOR_DIR", "stl/multicolour")
ASM_DIR = ROOT / getattr(P, "ASM_DIR", "asm")
REPORT = ROOT / getattr(P, "REPORT", "docs/verification.json")
ENVELOPE = getattr(P, "PRINTER", {}).get("envelope_mm", (256, 256, 256))
INLAY_MAX_DEPTH = getattr(P, "INLAY_MAX_DEPTH", 1.0)
# round features of two bodies that share an axis within tolerance_mm are coaxial, up to near_miss_mm off axis a failure;
# allowed: body pairs with intentional offsets (e.g. a shaft resting eccentrically in a larger bore)
ALIGNMENT = dict(dict(tolerance_mm=0.2, near_miss_mm=2.0, allowed=()), **getattr(P, "ALIGNMENT", {}))
OVERLAP_MM3 = 0.01


def save(name, data):
    path = BUILD / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def scad(args):
    executable = shutil.which("openscad")
    if not executable:
        raise RuntimeError("OpenSCAD not found on PATH")
    result = subprocess.run([executable, "--hardwarnings", *args], capture_output=True, text=True, cwd=BUILD)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def manifold(mesh):
    solid = md.Manifold(md.Mesh(np.asarray(mesh.vertices, dtype=np.float32),
                               np.asarray(mesh.faces, dtype=np.uint32)))
    if solid.status() != md.Error.NoError:
        raise ValueError(f"Invalid manifold: {solid.status()}")
    return solid


def mesh_info(mesh):
    return {
        "size_mm": mesh.extents.round(4).tolist(),
        "bounds_mm": mesh.bounds.round(4).tolist(),
        "volume_mm3": round(float(mesh.volume), 4),
        "triangles": len(mesh.faces),
        "watertight": bool(mesh.is_watertight),
        "consistent_winding": bool(mesh.is_winding_consistent),
        "degenerate_faces": int(np.sum(mesh.area_faces < 1e-9)),
        "components": len(mesh.split(only_watertight=False)),
    }


def valid_mesh(info):
    return (info["watertight"] and info["consistent_winding"]
            and info["degenerate_faces"] == 0 and info["volume_mm3"] > 0)


def export_one(job):
    group, name, code = job
    folder = BUILD / group
    folder.mkdir(parents=True, exist_ok=True)
    src = SOURCE
    if code:
        src = folder / f"{name}.scad"
        src.write_text(f"include <{SOURCE.as_posix()}>\n{code}\n")
    path = folder / f"{name}.stl"
    # CGAL now and then yields a degenerate triangle that does not reproduce, hence a second CGAL attempt
    for backend in ("Manifold", "CGAL", "CGAL"):
        log = scad([f"--backend={backend}", "--export-format", "binstl", "-D",
                    f'part="{"none" if code else name}"', "-o", str(path), str(src)])
        (folder / f"{name}-{backend}.log").write_text(log)
        mesh = trimesh.load_mesh(path)
        info = mesh_info(mesh)
        if valid_mesh(info):
            manifold(mesh)
            break
    if not valid_mesh(info):
        raise ValueError(f"Invalid export {name}: {info}")
    info["backend"] = backend
    info["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    if group == "assembly":
        # evaluated tree before booleans: holes are still cylinders with a diameter (check_alignment)
        scad(["-D", 'part="none"', "-o", str(folder / f"{name}.csg"), str(src)])
    if group == "print":
        qty, material, components = PARTS[name]
        assert info["components"] == components, (name, "Wrong body count", info)
        assert abs(mesh.bounds[0, 2]) < 0.002, (name, "Not on print bed")
        assert np.all(mesh.extents <= ENVELOPE), (name, f"Exceeds the build volume {ENVELOPE}")
        info.update(quantity=qty, material=material)
    if group == "color" and name.endswith("_base"):
        # the base carries the bed contact; inlays may sit on a face higher up (their union with the base is checked)
        assert abs(mesh.bounds[0, 2]) < 0.002, (name, "Not on print bed")
    return group, name, info


def check_part_manifest():
    names = set(re.findall(r'part\s*==\s*"(\w+)"', SOURCE.read_text())) - NON_PRINT_BRANCHES
    assert set(COLOR_PIECES) <= names, f"Multicolour branches missing: {sorted(set(COLOR_PIECES) - names)}"
    names -= set(COLOR_PIECES)
    assert names == set(PARTS), f"PARTS differs from {P.SOURCE}: {sorted(names ^ set(PARTS))}"


def build(only=None):
    jobs = [("print", name, None) for name in PARTS]
    jobs += [("assembly", name, code) for name, code in ASSEMBLY.items()]
    jobs += [("color", name, None) for name in COLOR_PIECES]
    if only:
        unknown = set(only) - {name for _, name, _ in jobs}
        assert not unknown, f"Unknown names for --only: {sorted(unknown)}"
        jobs = [job for job in jobs if job[1] in only]
    results = {"print": {}, "assembly": {}, "color": {}}
    with ThreadPoolExecutor(max_workers=getattr(P, "WORKERS", 4)) as pool:
        for group, name, info in pool.map(export_one, jobs):
            results[group][name] = info
            print(f"Export {group}/{name}: closed, {info['backend']}", flush=True)
    save("meshes.json", results)
    return results


def get_metrics():
    """part="metrics" echoes METRICS_TAG followed by a list of [key, value] pairs."""
    tag = getattr(P, "METRICS_TAG", None)
    if not tag:
        return {}
    path = BUILD / "metrics.echo"
    scad(["-D", 'part="metrics"', "-o", str(path), str(SOURCE)])
    line = next(line for line in path.read_text().splitlines() if f'"{tag}", ' in line)
    text = line.split(f'"{tag}", ', 1)[1]
    # OpenSCAD literals Python does not know (outside the key strings)
    parts = re.split(r'("[^"]*")', text)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"\btrue\b", "True", parts[i])
        parts[i] = re.sub(r"\bfalse\b", "False", parts[i])
        parts[i] = re.sub(r"\bundef\b", "None", parts[i])
    return dict(ast.literal_eval("".join(parts)))


def check_collisions(solids):
    allowed = {frozenset(pair) for pair in getattr(P, "ALLOWED_OVERLAPS", ())}
    collisions = []
    for a, b in itertools.combinations(solids, 2):
        if frozenset((a, b)) in allowed:
            continue
        cut = solids[a] ^ solids[b]
        volume = cut.volume()
        if volume > OVERLAP_MM3:
            collisions.append(dict(a=a, b=b, volume_mm3=round(volume, 4), bounds=list(cut.bounding_box())))
    save("collisions.json", collisions)
    assert not collisions, f"Unexpected intersections: {collisions}"
    return collisions


def check_alignment():
    """Round features (cylinders from the CSG dumps) of different bodies, one of them a hole, nearly sharing an axis."""
    bodies = {name: holes.load(BUILD / "assembly" / f"{name}.csg") for name in ASSEMBLY}
    result = holes.align(bodies, ALIGNMENT["tolerance_mm"], ALIGNMENT["near_miss_mm"], ALIGNMENT["allowed"])
    save("alignment.json", dict(result, features=bodies))
    assert not result["misaligned"], \
        f"Round features off axis by {ALIGNMENT['tolerance_mm']}-{ALIGNMENT['near_miss_mm']} mm: {result['misaligned'][:5]}"
    return result, bodies


def union(solids, names):
    return md.Manifold.batch_boolean([solids[n] for n in names], md.OpType.Add)


def solid(solids, names):
    """One body by name or the union of a list of names."""
    return solids[names] if isinstance(names, str) else union(solids, names)


def names_list(names):
    return [names] if isinstance(names, str) else list(names)


def cylinder(start, axis, length, radius, segments=48):
    """Manifold cylinder from `start` along any `axis` direction."""
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    helper = np.array([1.0, 0, 0]) if abs(axis[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(helper, axis)
    u /= np.linalg.norm(u)
    frame = np.column_stack([u, np.cross(axis, u), axis, np.asarray(start, float)])
    return md.Manifold.cylinder(length, radius, radius, segments).transform(frame)


def sweep(solids, moving, fixed, direction, length, step):
    """Move the union of `moving` along `direction` in steps; returns (colliding steps, first distance, max volume)."""
    moving, fixed = solid(solids, moving), solid(solids, fixed)
    unit = np.asarray(direction, float) / np.linalg.norm(direction)
    maximum, first, count = 0, None, 0
    for distance in np.arange(0, length + step / 2, step):
        volume = (moving.translate((unit * distance).tolist()) ^ fixed).volume()
        if volume > OVERLAP_MM3:
            count += 1
            first = float(distance) if first is None else first
            maximum = max(maximum, volume)
    return count, first, maximum


def contacts(solids, items, probe=0.05, min_mm3=0.1):
    """(body, support, direction): moved `probe` mm towards its support, the body must intersect it (it rests, not floats)."""
    rows = {}
    for body, support, direction in items:
        unit = np.asarray(direction, float) / np.linalg.norm(direction)
        volume = (solid(solids, body).translate((unit * probe).tolist()) ^ solid(solids, support)).volume()
        key = f"{body}@{support}"
        key = key if key not in rows else f"{key}{list(np.round(unit, 3))}"
        rows[key] = round(volume, 4)
    failed = {key: volume for key, volume in rows.items() if volume <= min_mm3}
    assert not failed, f"Bodies do not rest on their support ({probe} mm probe, volume <= {min_mm3} mm3): {failed}"
    return rows


def stops(solids, items, step=0.25):
    """(name, moving, fixed, direction, limit): the moving bodies must hit the fixed ones within `limit` mm."""
    rows = []
    for name, moving, fixed, direction, limit in items:
        _, first, _ = sweep(solids, names_list(moving), names_list(fixed), direction, limit, step)
        rows.append(dict(name=name, first_contact_mm=first, limit_mm=limit))
    failed = [row for row in rows if row["first_contact_mm"] is None]
    assert not failed, f"No stop within the limit: {failed}"
    return rows


def paths(solids, items):
    """(name, moving, fixed, direction, length, step) or (name, moving, fixed, [(direction, length, step), ...]):
    the moving bodies travel the segments one after another without intersecting the fixed ones."""
    rows = []
    for name, moving, fixed, *spec in items:
        segments = spec[0] if len(spec) == 1 else [tuple(spec)]
        mover, still = solid(solids, moving), solid(solids, fixed)
        offset, travelled, blocked, maximum = np.zeros(3), 0.0, [], 0.0
        for direction, length, step in segments:
            unit = np.asarray(direction, float) / np.linalg.norm(direction)
            for distance in np.arange(0, length + step / 2, step):
                volume = (mover.translate((offset + unit * distance).tolist()) ^ still).volume()
                if volume > OVERLAP_MM3:
                    blocked.append(round(travelled + float(distance), 3))
                    maximum = max(maximum, volume)
            offset, travelled = offset + unit * length, travelled + length
        rows.append(dict(name=name, length_mm=travelled, collisions=len(blocked),
                         first_mm=blocked[0] if blocked else None, max_volume_mm3=round(maximum, 4)))
    failed = [row for row in rows if row["collisions"]]
    assert not failed, f"Assembly path obstructed: {failed}"
    return rows


def insert_probes(solids, items):
    """(body, entry, axis, depth, hole_d, wall[, floor]): pocket from `entry` along `axis` into the material -
    core open, the datasheet wall around it and (unless floor=False) a ring below the pocket floor are material."""
    rows = []
    for body, entry, axis, depth, hole, wall, *floor in items:
        target, axis, entry = solids[body], np.asarray(axis, float) / np.linalg.norm(axis), np.asarray(entry, float)
        start, length = entry + axis * 0.2, depth - 0.5
        core = cylinder(start, axis, length, 0.375 * hole)
        ring = cylinder(start, axis, length, hole / 2 + wall) - cylinder(start, axis, length, hole / 2 + 0.3)
        row = dict(body=body, at=entry.round(2).tolist(), empty_mm3=round((core ^ target).volume(), 4),
                   ring_fill=round((ring ^ target).volume() / ring.volume(), 3))
        if not floor or floor[0]:
            # a ring, not a disc: screws may pass through the pocket floor
            base = entry + axis * (depth + 0.2)
            bottom = cylinder(base, axis, 0.4, hole / 2 + wall) - cylinder(base, axis, 0.4, 0.45 * hole)
            row["floor_fill"] = round((bottom ^ target).volume() / bottom.volume(), 3)
        rows.append(row)
    failed = [row for row in rows if row["empty_mm3"] >= 0.01 or row["ring_fill"] <= 0.95 or row.get("floor_fill", 1) <= 0.95]
    assert not failed, f"Insert pocket closed, without wall or without floor: {failed}"
    return rows


def clearances(solids, items):
    """(a, b, min_mm): the smallest distance between the bodies (names or name lists) is at least min_mm."""
    rows = []
    for a, b, minimum in items:
        search = minimum + 1.0
        gap = solid(solids, a).min_gap(solid(solids, b), search)
        rows.append(dict(a=a, b=b, gap_mm=round(gap, 3), min_mm=minimum, capped=gap >= search))
    failed = [row for row in rows if row["gap_mm"] < row["min_mm"] - 1e-6]
    assert not failed, f"Clearance too small: {failed}"
    return rows


def check_color_parts():
    """Base and inlays do not overlap, together they are the single-colour part, each inlay spans only a few layers."""
    report = {}
    for name, inlays in COLOR_PARTS.items():
        full = manifold(trimesh.load_mesh(BUILD / "print" / f"{name}.stl"))
        meshes = {piece: trimesh.load_mesh(BUILD / "color" / f"{name}_{piece}.stl") for piece in ("base", *inlays)}
        solids = {piece: manifold(mesh) for piece, mesh in meshes.items()}
        overlap = sum((solids[a] ^ solids[b]).volume() for a, b in itertools.combinations(solids, 2))
        joined = solids["base"]
        for piece in inlays:
            joined = joined + solids[piece]
        delta = (full - joined).volume() + (joined - full).volume()
        assert overlap <= OVERLAP_MM3, f"{name}: multicolour pieces overlap by {overlap:.3f} mm3"
        assert delta <= max(0.5, full.volume() * 1e-5), f"{name}: pieces differ from the single-colour part by {delta:.3f} mm3"
        info = dict(overlap_mm3=round(overlap, 4), union_delta_mm3=round(delta, 4))
        for piece in inlays:
            # colour changes cost time and filament per layer: an inlay spans only a few layers, on the bed
            # (logo on the visible face) or higher up (e.g. raised text on an inner face)
            mesh = meshes[piece]
            z0, z1 = float(mesh.bounds[0, 2]), float(mesh.bounds[1, 2])
            assert mesh.volume > 1 and z1 - z0 <= INLAY_MAX_DEPTH, \
                f"{name}_{piece}: inlay missing or spanning more than {INLAY_MAX_DEPTH} mm of layers (z {z0:.2f}-{z1:.2f})"
            info[piece] = dict(mm3=round(float(mesh.volume), 2), depth_mm=round(z1 - z0, 3), z_mm=[round(z0, 3), round(z1, 3)],
                               bodies=len(mesh.split(only_watertight=False)))
        report[name] = info
    return report


def label(folder, name):
    try:
        prefix = folder.relative_to(STL_DIR).as_posix()
    except ValueError:
        prefix = folder.relative_to(ROOT).as_posix()
    return name if prefix == "." else f"{prefix}/{name}"


def check_committed_stls():
    folders = [(STL_DIR, "print", list(PARTS))]
    if COLOR_PIECES:
        folders.append((COLOR_DIR, "color", COLOR_PIECES))
    differences = {}
    for folder, group, names in folders:
        actual = {p.stem for p in folder.glob("*.stl")}
        assert actual == set(names), f"Missing/stale STL names in {folder.relative_to(ROOT)}: {sorted(actual ^ set(names))}"
        for name in names:
            old = trimesh.load_mesh(folder / f"{name}.stl")
            new = trimesh.load_mesh(BUILD / group / f"{name}.stl")
            assert valid_mesh(mesh_info(old)), f"Invalid committed STL: {folder.relative_to(ROOT)}/{name}"
            a, b = manifold(old), manifold(new)
            delta = (a - b).volume() + (b - a).volume()
            assert delta <= max(0.01, new.volume * 1e-7), f"Stale STL: {folder.relative_to(ROOT)}/{name}, delta={delta}"
            differences[label(folder, name) if group == "color" else name] = round(delta, 6)
    return differences


def replace_folder(folder, group, names, keep=()):
    """Copy the freshly exported meshes over and drop orphans; meshes from other sources are named in keep."""
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copy2(BUILD / group / f"{name}.stl", folder / f"{name}.stl")
    for path in folder.glob("*.stl"):
        if path.stem not in names and path.stem not in keep:
            print(f"Removing orphan {path.relative_to(ROOT)}", flush=True)
            path.unlink()


def software():
    versions = {}
    for name in ("numpy", "trimesh", "manifold3d", "scipy", "rtree", "networkx"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    return versions


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("build", "check", "export"))
    parser.add_argument("--only", help="build only: comma-separated part/body names for quick iteration")
    parser.add_argument("--strict", action="store_true", help="also fail on open items (e.g. unmeasured hardware)")
    args = parser.parse_args()
    if args.only and args.command != "build":
        parser.error("--only only works with build")
    BUILD.mkdir(exist_ok=True)
    (BUILD / "verification.json").unlink(missing_ok=True)
    check_part_manifest()
    results = build(args.only.split(",") if args.only else None)
    if args.command == "build":
        return
    meshes = {n: trimesh.load_mesh(BUILD / "assembly" / f"{n}.stl") for n in ASSEMBLY}
    solids = {n: manifold(mesh) for n, mesh in meshes.items()}
    metrics = get_metrics()
    collisions = check_collisions(solids)
    alignment, features = check_alignment()
    bound = lambda function: lambda *args, **kwargs: function(solids, *args, **kwargs)
    ctx = SimpleNamespace(root=ROOT, build=BUILD, metrics=metrics, meshes=meshes, solids=solids, holes=features,
                          save=save, manifold=manifold, union=lambda names: union(solids, names), cylinder=cylinder,
                          sweep=bound(sweep), contacts=bound(contacts), stops=bound(stops), paths=bound(paths),
                          insert_probes=bound(insert_probes), clearances=bound(clearances),
                          summary=[f"{sum(alignment['coaxial_pairs'].values())} coaxial feature pairs"], open_items=[])
    project = P.checks(ctx) if hasattr(P, "checks") else {}
    colors = check_color_parts()
    if args.command == "export":
        replace_folder(STL_DIR, "print", list(PARTS))
        if COLOR_PIECES:
            replace_folder(COLOR_DIR, "color", COLOR_PIECES)
        # asm/ also holds vendor meshes that this tool does not export (ASM_KEEP), everything else is pruned
        replace_folder(ASM_DIR, "assembly", list(ASSEMBLY), keep=getattr(P, "ASM_KEEP", ()))
    consistency = check_committed_stls()
    for name, info in results["print"].items():
        info["committed_sha256"] = hashlib.sha256((STL_DIR / f"{name}.stl").read_bytes()).hexdigest()
    pairs = len(solids) * (len(solids) - 1) // 2
    report = dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(), software=software(),
                  print_parts=len(PARTS), print_quantity=sum(q for q, _, _ in PARTS.values()),
                  print_meshes=results["print"], color_meshes=results["color"], color_parts=colors,
                  assembly_bodies=len(solids), assembly_pairs=pairs, metrics=metrics, intersections=collisions,
                  alignment=alignment,
                  **project, stl_difference_mm3=consistency, open_measurements=ctx.open_items,
                  limitations=getattr(P, "LIMITATIONS", ["Hardware envelopes, not detailed vendor CAD",
                                                         "Sampled motion, no continuous swept-volume proof",
                                                         "No flexible deformation, physical fit, strength or thermal validation"]))
    save("verification.json", report)
    if args.command == "export":
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BUILD / "verification.json", REPORT)
    for item in ctx.open_items:
        print(f"OPEN: {item}")
    print("PASS: " + ", ".join([f"{len(PARTS)} print meshes", f"{len(COLOR_PARTS)} multicolour parts",
                                *ctx.summary, f"{pairs} pairs"]))
    if args.strict and ctx.open_items:
        raise AssertionError("Open items (see OPEN lines)")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, RuntimeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
