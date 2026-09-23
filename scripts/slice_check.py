#!/usr/bin/env python3
"""Diagnostic Bambu Studio slicing and the multi-plate project 3MF (skill openscad-print-project).

1. Slices every print STL on its own with the installed system profiles (PRINTER, PROCESS, FILAMENTS in
   print_project.py): no supports, default infill, solid for FULL_INFILL parts and FULL_INFILL_MATERIALS.
2. Builds PROJECT_3MF: every part of the full build on the fixed PLATES, each plate centred; multicolour
   parts as one object per copy with their inlay filaments, parts at the left edge and the prime tower
   to their right (CENTRE_PLATES: parts centred, tower behind or in front of them). Every plate is sliced (layout, instances, effective settings); multicolour plates also prove the inlays print.
3. Optional TEST_PLATES (e.g. fit tests; entries are part names or (name, count), one copy by default) become TEST_3MF
   the same way, with TEST_PROCESS overriding PROCESS (e.g. fewer walls and less infill: same geometry, less material).
   TEST_FILAMENT = slot prints every test part single-colour from that filament slot (no inlays, no prime tower).

Generated G-code and 3MF files under build/ are diagnostics, NOT print releases.
Writes build/slicer-diagnostic/summary.json and SLICER_SUMMARY (default docs/slicer-summary.json).
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from print_tools import BUILD, COLOR_DIR, COLOR_PARTS, P, PARTS, ROOT, STL_DIR

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--app", type=Path, default=Path("/Applications/BambuStudio.app"), help="macOS app bundle")
parser.add_argument("--exe", type=Path, help="Bambu Studio executable (overrides --app, e.g. on Linux)")
parser.add_argument("--profiles", type=Path, help="BBL system profile folder (overrides --app)")
args = parser.parse_args()
executable = args.exe or args.app / "Contents/MacOS/BambuStudio"
profile_root = args.profiles or args.app / "Contents/Resources/profiles/BBL"
out = BUILD / "slicer-diagnostic"
profiles = out / "profiles"
profiles.mkdir(parents=True, exist_ok=True)
files = {path.stem: path for path in profile_root.rglob("*.json")}

PRINTER = dict(machine="Bambu Lab H2S 0.4 nozzle", process="0.20mm Standard @BBL H2S",
               bed="Textured PEI Plate") | getattr(P, "PRINTER", {})
# PROCESS["settings"]: further Bambu process keys for every part, e.g. {"infill_direction": "0"} (first-layer lines
# along x, parallel to a long bed face; Bambu alternates solid layers by 90 degrees from there)
PROCESS = dict(wall_loops=4, top_shell_layers=5, bottom_shell_layers=5, infill=25,
               pattern="gyroid") | getattr(P, "PROCESS", {})
FULL_INFILL = set(getattr(P, "FULL_INFILL", ()))
FULL_INFILL_MATERIALS = set(getattr(P, "FULL_INFILL_MATERIALS", ("TPU",)))
# Filament slots of the project 3MF, 1-based in list order; inlay slots name their inlay or a tuple of inlays sharing the slot
FILAMENTS = getattr(P, "FILAMENTS", None) or [dict(material=m, profile=f"Generic {m} @BBL H2S")
                                              for m in sorted({m for _, m, _ in PARTS.values()})]
PLATES = getattr(P, "PLATES", None) or [(name, [name]) for name in PARTS if PARTS[name][0] > 0]
# Multicolour plates (by title) whose parts stay in the middle of the bed, prime tower behind or in front of them
# instead of parts at the left edge and the tower beside them
CENTRE_PLATES = set(getattr(P, "CENTRE_PLATES", ()))
assert CENTRE_PLATES <= {title for title, _ in PLATES}, f"CENTRE_PLATES names unknown plates: {sorted(CENTRE_PLATES - {t for t, _ in PLATES})}"
# Print pauses (e.g. to embed magnets or lay mesh): part -> print_z of the first layer printed after the pause.
# A pause stops its whole plate, so give such parts their own plate.
PAUSES = getattr(P, "PAUSES", {})
PROJECT_3MF = ROOT / getattr(P, "PROJECT_3MF", f"{STL_DIR.relative_to(ROOT).as_posix()}/{ROOT.name}_all_parts.3mf")
# Test prints (fit tests, samples) as their own project: plates of part names or (name, count), one copy by default
TEST_PLATES = getattr(P, "TEST_PLATES", [])
TEST_PROCESS = PROCESS | getattr(P, "TEST_PROCESS", {})
TEST_FILAMENT = getattr(P, "TEST_FILAMENT", None)
TEST_3MF = ROOT / getattr(P, "TEST_3MF", f"{STL_DIR.relative_to(ROOT).as_posix()}/{ROOT.name}_test_prints.3mf")
SUMMARY = ROOT / getattr(P, "SLICER_SUMMARY", "docs/slicer-summary.json")
INLAY_FILAMENT = {inlay: i for i, f in enumerate(FILAMENTS, 1)
                  for inlay in ((f["inlay"],) if isinstance(f.get("inlay"), str) else f.get("inlay", ()))}
DEFAULT_INFILL = int(PROCESS["infill"])


def base_filament(material):
    return next(i for i, f in enumerate(FILAMENTS, 1) if f["material"] == material and not f.get("inlay"))


def resolve(name, parents=()):
    if name in parents:
        raise ValueError(f"Circular profile inheritance: {parents}, {name}")
    if name not in files:
        raise ValueError(f"Bambu profile not found: {name!r} (see {profile_root})")
    data = json.loads(files[name].read_text())
    result = {}
    if data.get("inherits"):
        result.update(resolve(data["inherits"], (*parents, name)))
    for include in data.get("include", []):
        result.update(resolve(include, (*parents, name)))
    result.update(data)
    result.pop("inherits", None)
    result.pop("include", None)
    return result


def infill(name, material):
    return 100 if material in FULL_INFILL_MATERIALS or name in FULL_INFILL else DEFAULT_INFILL


def pattern(density):
    # Bambu serializes Rectilinear as "zig-zag" ("rectilinear" maps to cubic); gyroid is refused at 100 %
    return "zig-zag" if density == 100 else PROCESS["pattern"]


for material in {m for _, m, _ in PARTS.values()}:
    base_filament(material)                       # every material needs a plain slot
for name, inlays in COLOR_PARTS.items():
    assert all(inlay in INLAY_FILAMENT for inlay in inlays), f"{name}: no FILAMENTS slot for {inlays}"
    assert infill(name, PARTS[name][1]) == DEFAULT_INFILL, f"{name}: multicolour parts with own infill are not supported yet"

machine = resolve(PRINTER["machine"])
machine["curr_bed_type"] = PRINTER["bed"]
(profiles / "machine.json").write_text(json.dumps(machine, indent=2))


def write_process(name, settings, density):
    process = resolve(PRINTER["process"])
    process.update(wall_loops=str(settings["wall_loops"]), sparse_infill_density=f"{density}%", enable_support="0",
                   top_shell_layers=str(settings["top_shell_layers"]),
                   bottom_shell_layers=str(settings["bottom_shell_layers"]), sparse_infill_pattern=pattern(density))
    process.update({key: str(value) for key, value in settings.get("settings", {}).items()})
    (profiles / name).write_text(json.dumps(process, indent=2))


for density in {infill(n, m) for n, (_, m, _) in PARTS.items()} | {DEFAULT_INFILL}:
    write_process(f"process-{density}.json", PROCESS, density)
if TEST_PLATES:
    write_process("process-test.json", TEST_PROCESS, int(TEST_PROCESS["infill"]))
for slot, filament in enumerate(FILAMENTS, 1):
    profile = resolve(filament["profile"])
    if filament.get("colour"):
        profile["filament_colour"] = [filament["colour"]]
    (profiles / f"filament-{slot}.json").write_text(json.dumps(profile, indent=2))


def run(name):
    quantity, material, _ = PARTS[name]
    folder = out / name
    folder.mkdir(exist_ok=True)
    source = STL_DIR / f"{name}.stl"
    # never read a result of an earlier run
    for stale in (folder / "result.json", folder / f"{name}-DIAGNOSTIC.3mf"):
        stale.unlink(missing_ok=True)
    command = [str(executable), "--datadir", str(folder / "config"), "--debug", "2",
               "--load-settings", f"{profiles / 'machine.json'};{profiles / f'process-{infill(name, material)}.json'}",
               "--load-filaments", str(profiles / f"filament-{base_filament(material)}.json"),
               "--orient", "0", "--arrange", "1", "--slice", "0",
               # --outputdir must be absolute, otherwise the CLI exits with 243
               "--export-3mf", f"{name}-DIAGNOSTIC.3mf", "--outputdir", str(folder), str(source)]
    result = subprocess.run(command, capture_output=True, text=True, cwd=folder)
    log = result.stdout + result.stderr
    (folder / "cli.log").write_text(log)
    report_path = folder / "result.json"
    data = json.loads(report_path.read_text()) if report_path.exists() else {}
    plates = data.get("sliced_plates", [])
    plate = plates[0] if plates else {}
    passed = result.returncode == 0 and data.get("return_code") == 0 and len(plates) == 1
    settings = {}
    if passed:
        with zipfile.ZipFile(folder / f"{name}-DIAGNOSTIC.3mf") as archive:
            settings = json.loads(archive.read("Metadata/project_settings.config"))
    row = dict(part=name, quantity=quantity, material=material, passed=passed,
               source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
               exit_code=result.returncode, result_code=data.get("return_code"),
               warnings=plate.get("warning_message"),
               hours=round(plate.get("total_predication", 0) / 3600, 3),
               grams=round(sum(f["total_used_g"] for f in plate.get("filaments", [])), 3),
               wall_loops=data.get("wall_loops"), infill_percent=data.get("sparse_infill_density"),
               layer_height=data.get("layer_height"),
               effective_settings={key: settings.get(key) for key in
                                   ("sparse_infill_pattern", "enable_support", "curr_bed_type",
                                    "top_shell_layers", "bottom_shell_layers")},
               start_gcode_diagnostic="Invalid T command" in log)
    print(f"Slice {name}: {'PASS' if passed else 'FAIL'}", flush=True)
    return row


def transform(text):
    matrix = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]
    if text:
        v = [float(x) for x in text.split()]
        matrix = [[v[0], v[3], v[6], v[9]], [v[1], v[4], v[7], v[10]], [v[2], v[5], v[8], v[11]]]
    return matrix


def attribute(tag, key):
    match = re.search(rf'\b{key}="([^"]+)"', tag)
    return match.group(1) if match else None


def plate_counts(group, full_build):
    """Plate entries are part names or (name, count); names take the PARTS quantity in the full build, else one copy."""
    return dict((entry, PARTS[entry][0] if full_build else 1) if isinstance(entry, str) else tuple(entry) for entry in group)


def build_project_3mf(plate_list=None, target=None, folder_name="project-3mf", full_build=True, process_file=None, mono=None):
    """Every part of the full build (no test prints) as one Bambu Studio project on the fixed PLATES; with
    full_build=False any plate list (test prints) into its own target file, optionally with its own process profile;
    mono = filament slot prints every part single-colour from its plain STL."""
    colour_parts = {} if mono else COLOR_PARTS
    target = target or PROJECT_3MF
    process_file = process_file or profiles / f"process-{DEFAULT_INFILL}.json"
    folder = out / folder_name
    folder.mkdir(exist_ok=True)
    resolved = [(title, plate_counts(group, full_build)) for title, group in (PLATES if plate_list is None else plate_list)]
    listed = [name for _, group in resolved for name in group]
    assert set(listed) <= set(PARTS), f"Plates name unknown parts: {sorted(set(listed) - set(PARTS))}"
    if full_build:
        wanted = [name for name in PARTS if PARTS[name][0] > 0]
        assert sorted(listed) == sorted(wanted), f"PLATES does not match PARTS: {sorted(set(listed) ^ set(wanted))}"
    plates, assembled = [], 0
    for title, group in resolved:
        objects = []
        for name, quantity in group.items():
            material = PARTS[name][1]
            if name in colour_parts:
                # Base and inlays as one object with several parts: all parts of one copy share one assemble_index,
                # each copy gets its own (a shared index merges every copy into one object)
                indices = list(range(assembled + 1, assembled + quantity + 1))
                assembled += quantity
                for piece, filament in (("base", base_filament(material)),
                                        *((inlay, INLAY_FILAMENT[inlay]) for inlay in COLOR_PARTS[name])):
                    objects.append(dict(path=str(COLOR_DIR / f"{name}_{piece}.stl"), count=quantity,
                                        filaments=[filament] * quantity, assemble_index=indices))
                continue
            entry = dict(path=str(STL_DIR / f"{name}.stl"), count=quantity,
                         filaments=[mono or base_filament(material)] * quantity)
            density = infill(name, material)
            if density != DEFAULT_INFILL:
                entry["print_params"] = dict(sparse_infill_density=f"{density}%", sparse_infill_pattern=pattern(density))
            objects.append(entry)
        plates.append(dict(plate_name=title, need_arrange=True, objects=objects))
    (folder / "assemble.json").write_text(json.dumps(dict(plates=plates), indent=2, ensure_ascii=False))
    raw = folder / "raw.3mf"
    raw.unlink(missing_ok=True)
    command = [str(executable), "--datadir", str(folder / "config"), "--debug", "2",
               "--load-settings", f"{profiles / 'machine.json'};{process_file}",
               "--load-filaments", ";".join(str(profiles / f"filament-{slot}.json") for slot in range(1, len(FILAMENTS) + 1)),
               "--load-assemble-list", "assemble.json",
               "--export-3mf", raw.name, "--outputdir", str(folder)]
    result = subprocess.run(command, capture_output=True, text=True, cwd=folder)
    (folder / "cli.log").write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and raw.exists(), f"Project 3MF export failed; inspect {folder}"
    piece_names = "|".join(sorted({"base", *(inlay for inlays in COLOR_PARTS.values() for inlay in inlays)}))

    with zipfile.ZipFile(raw) as source:
        settings = source.read("Metadata/model_settings.config").decode()
        model = source.read("3D/3dmodel.model").decode()
        meshes = {}

        def vertices(path, object_id):
            text = meshes.setdefault(path, source.read(path.lstrip("/")).decode())
            body = re.search(rf'<object id="{object_id}".*?</object>', text, re.S).group(0)
            return [tuple(map(float, v)) for v in re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body)]

        items = {attribute(tag, "objectid"): tag for tag in re.findall(r"<item [^>]*>", model)}

        def bounds(object_id):
            body = re.search(rf'<object id="{object_id}".*?</object>', model, re.S).group(0)
            outer = transform(attribute(items[object_id], "transform"))
            low, high = [float("inf")] * 3, [float("-inf")] * 3
            for component in re.findall(r"<component [^>]*>", body):
                inner = transform(attribute(component, "transform"))
                matrix = [[sum(outer[r][k] * inner[k][c] for k in range(3)) + (outer[r][3] if c == 3 else 0)
                           for c in range(4)] for r in range(3)]
                for v in vertices(attribute(component, "p:path"), attribute(component, "objectid")):
                    for r in range(3):
                        p = matrix[r][0] * v[0] + matrix[r][1] * v[1] + matrix[r][2] * v[2] + matrix[r][3]
                        low[r], high[r] = min(low[r], p), max(high[r], p)
            return low, high

        plate_ids = [re.findall(r'<metadata key="object_id" value="(\d+)"', plate)
                     for plate in re.findall(r"<plate>(.*?)</plate>", settings, re.S)]
        names = {}
        for match in re.finditer(r'<object id="(\d+)">(.*?)</object>', settings, re.S):
            body = match.group(2)
            parts = {}
            for part in re.findall(r"<part [^>]*>(.*?)</part>", body, re.S):
                extruder = re.search(r'key="extruder" value="(\d+)"', part) or re.search(r'key="extruder" value="(\d+)"', body)
                parts[re.sub(r"_\d+$", "", re.search(r'key="name" value="([^"]+)"', part).group(1))] = extruder.group(1)
            name = re.sub(rf"_({piece_names})$", "", next(iter(parts)))
            if name in colour_parts:
                expected = {f"{name}_base": str(base_filament(PARTS[name][1])),
                            **{f"{name}_{inlay}": str(INLAY_FILAMENT[inlay]) for inlay in COLOR_PARTS[name]}}
                assert parts == expected, f"Multicolour {name}: parts {parts}, expected {expected}"
            names[match.group(1)] = name
        # assembled objects are called assemble_N; give them the part name
        settings = re.sub(r'(<object id="(\d+)">\s*<metadata key="name" value=")assemble_\d+(")',
                          lambda m: m.group(1) + names[m.group(2)] + m.group(3), settings)
        assert len(plate_ids) == len(resolved), f"{target.name} has {len(plate_ids)} plates, expected {len(resolved)}"
        # Plate grid like Bambu Studio: columns from the square root of the plate count, 20 % gap
        width = max(float(p.split("x")[0]) for p in machine["printable_area"])
        depth = max(float(p.split("x")[1]) for p in machine["printable_area"])
        root = len(plate_ids) ** 0.5
        columns = round(root) + 1 if root > round(root) else round(root)
        project_settings = json.loads(source.read("Metadata/project_settings.config"))
        tower_width = float(project_settings["prime_tower_width"])
        tower_brim = float(project_settings["prime_tower_brim_width"])
        towers = {}
        shift, layout = {}, []
        for index, ((title, group), ids) in enumerate(zip(resolved, plate_ids)):
            got = sorted(names[i] for i in ids)
            assert got == sorted(n for n in group for _ in range(group[n])), f"Plate {title} holds {got}"
            origin = ((index % columns) * width * 1.2, -(index // columns) * depth * 1.2)
            boxes = [bounds(i) for i in ids]
            low = [min(b[0][r] for b in boxes) - origin[r] for r in range(2)]
            high = [max(b[1][r] for b in boxes) - origin[r] for r in range(2)]
            size = (high[0] - low[0], high[1] - low[1])
            assert size[0] <= width and size[1] <= depth, f"Plate {title} exceeds the bed"
            delta = (width / 2 - (low[0] + high[0]) / 2, depth / 2 - (low[1] + high[1]) / 2)
            entry = dict(plate=index + 1, name=title, parts=got, size_mm=[round(size[0], 1), round(size[1], 1)])
            if set(group) & set(colour_parts) and title in CENTRE_PLATES:
                # parts stay centred; tower in the strip behind them, else in front (depth about 40 mm, grows
                # with the purge volume; the slicer run itself reports a tower that still collides)
                x = width / 2 - tower_width / 2
                behind = depth / 2 + size[1] / 2 + 8 + tower_brim
                front = depth / 2 - size[1] / 2 - 8 - tower_brim - 40
                if behind + 40 + tower_brim <= depth - 5:
                    towers[index] = (x, behind)
                else:
                    assert front >= 5 + tower_brim, \
                        f"Plate {title}: no room for the prime tower in front of or behind the centred parts ({size[0]:.1f} x {size[1]:.1f} mm)"
                    towers[index] = (x, front)
                entry["prime_tower_xy"] = [round(v, 1) for v in towers[index]]
            elif set(group) & set(colour_parts):
                # Multicolour plate: parts to the left edge, prime tower right next to them. Wide plates first try
                # tighter margins, then put the parts to the front edge and the tower behind them (its depth grows
                # with the purge volume; the slicer run itself reports a tower that still collides)
                for tower_margin, tower_gap in ((10, 15), (5, 8)):
                    if tower_margin + size[0] + tower_gap + 2 * tower_brim + tower_width <= width - 5:
                        delta = (tower_margin - low[0], delta[1])
                        towers[index] = (tower_margin + size[0] + tower_gap + tower_brim, depth / 2 - 30)
                        break
                else:
                    delta = (tower_margin - low[0], tower_margin - low[1])
                    towers[index] = (tower_margin + tower_brim, tower_margin + size[1] + tower_gap + tower_brim)
                    assert towers[index][1] + 40 + tower_brim <= depth - 5, \
                        f"Plate {title}: no room for the prime tower ({size[0]:.1f} x {size[1]:.1f} mm on {width:.0f} x {depth:.0f})"
                entry["prime_tower_xy"] = [round(v, 1) for v in towers[index]]
            for i in ids:
                shift[i] = delta
            layout.append(entry)

        def moved(match):
            tag = match.group(0)
            values = attribute(tag, "transform").split()
            dx, dy = shift[attribute(tag, "objectid")]
            values[9], values[10] = f"{float(values[9]) + dx:.4f}", f"{float(values[10]) + dy:.4f}"
            return tag.replace(attribute(tag, "transform"), " ".join(values))

        model = re.sub(r"<item [^>]*>", moved, model)
        count = len(plate_ids)
        xs = (list(project_settings.get("wipe_tower_x", [])) + [f"{width / 2:.0f}"] * count)[:count]
        ys = (list(project_settings.get("wipe_tower_y", [])) + [f"{depth * 0.75:.0f}"] * count)[:count]
        for index, (x, y) in towers.items():
            xs[index], ys[index] = f"{x:.1f}", f"{y:.1f}"
        project_settings["wipe_tower_x"], project_settings["wipe_tower_y"] = xs, ys
        # Bambu Studio (GUI) resets every setting that is not named in different_settings_to_system to the system
        # preset when it opens a project: print, one entry per filament, printer. The CLI leaves them empty, so the
        # GUI dropped our walls, shells and infill and showed the default print (the slicer runs here kept them)
        wanted = [(PRINTER["process"], json.loads(process_file.read_text())),
                  *((f["profile"], json.loads((profiles / f"filament-{slot}.json").read_text()))
                    for slot, f in enumerate(FILAMENTS, 1)),
                  (PRINTER["machine"], machine)]
        project_settings["different_settings_to_system"] = [
            ";".join(sorted(key for key, value in own.items() if key not in ("name", "inherits") and resolve(system).get(key) != value))
            for system, own in wanted]
        assert len(project_settings["different_settings_to_system"]) == len(FILAMENTS) + 2
        pause_gcode = machine.get("machine_pause_gcode", "M400 U1")
        pause_gcode = (pause_gcode[0] if isinstance(pause_gcode, list) else pause_gcode).strip()
        pause_plates = {index: sorted({z for part in group for z in PAUSES.get(part, [])})
                        for index, (_, group) in enumerate(resolved) if any(part in PAUSES for part in group)}
        custom_name = "Metadata/custom_gcode_per_layer.xml"
        # written next to the diagnostics first; published to PROJECT_3MF only after every plate sliced
        candidate = folder / "project.3mf"
        with zipfile.ZipFile(candidate, "w", zipfile.ZIP_DEFLATED) as project:
            for item in source.infolist():
                if item.filename == custom_name:
                    continue
                data = (model.encode() if item.filename == "3D/3dmodel.model" else
                        settings.encode() if item.filename == "Metadata/model_settings.config" else
                        json.dumps(project_settings, indent=4).encode() if item.filename == "Metadata/project_settings.config" else
                        source.read(item.filename))
                project.writestr(item, data)
            if pause_plates:
                project.writestr(custom_name, custom_gcode_xml(pause_plates, pause_gcode))
    placed = sum(len(ids) for ids in plate_ids)
    own_infill = len([v for v in re.findall(r'sparse_infill_density" value="(\d+)%"', settings) if int(v) != DEFAULT_INFILL])
    expected_own = sum(count for _, group in resolved for n, count in group.items() if infill(n, PARTS[n][1]) != DEFAULT_INFILL)
    assert placed == sum(count for _, group in resolved for count in group.values()), f"{target.name} places {placed} parts"
    assert own_infill == expected_own, f"{target.name}: {own_infill} parts with own infill, expected {expected_own}"
    print(f"{target.name}: {placed} parts on {len(plate_ids)} plates, slicing every plate before publishing", flush=True)
    multicolour, pauses, plate_slices = {}, {}, {}
    for index, (title, group) in enumerate(resolved, 1):
        coloured = set(group) & set(colour_parts)
        plate_dir = folder / f"slice-plate-{index}"
        plate_dir.mkdir(exist_ok=True)
        for stale in (plate_dir / "result.json", plate_dir / "sliced.3mf"):
            stale.unlink(missing_ok=True)
        command = [str(executable), "--datadir", str(folder / "config"), "--debug", "2", "--slice", str(index),
                   "--export-3mf", "sliced.3mf", "--outputdir", str(plate_dir), str(candidate)]
        result = subprocess.run(command, capture_output=True, text=True, cwd=plate_dir)
        log = result.stdout + result.stderr
        (plate_dir / "cli.log").write_text(log)
        data = json.loads((plate_dir / "result.json").read_text()) if (plate_dir / "result.json").exists() else {}
        plate = (data.get("sliced_plates") or [{}])[0]
        grams = {f["id"]: round(f["total_used_g"], 2) for f in plate.get("filaments", [])}
        assert result.returncode == 0 and data.get("return_code") == 0 and "slicing result conflict" not in log, \
            f"Plate {title} does not slice; see {plate_dir}"
        if index - 1 in pause_plates:
            with zipfile.ZipFile(plate_dir / "sliced.3mf") as sliced:
                name = next(n for n in sliced.namelist() if re.fullmatch(r"Metadata/plate_\d+\.gcode", n))
                found = pause_heights(sliced.read(name).decode(errors="replace"), pause_gcode)
            wanted = pause_plates[index - 1]
            # Bambu emits the pause at the layer change: in the layer at the requested height, before it extrudes
            assert [z for z, _ in found] == wanted and not any(e for _, e in found), \
                f"Plate {title}: pauses {found} (layer, extruded before), wanted at the start of {wanted}"
            pauses[title] = dict(plate=index, pause_before_layer_mm=wanted)
            print(f"Slice pause plate {title}: PASS, pause before layer {wanted} mm", flush=True)
        plate_slices[title] = dict(plate=index, hours=round(plate.get("total_predication", 0) / 3600, 2),
                                   grams_by_filament=grams, warnings=plate.get("warning_message"))
        if not coloured:
            print(f"Slice plate {title}: PASS, filament use {grams} g", flush=True)
            continue
        needed = {base_filament(PARTS[part][1]) for part in group} | \
                 {INLAY_FILAMENT[inlay] for part in group if part in colour_parts for inlay in colour_parts[part]}
        assert all(grams.get(f, 0) > 0 for f in needed), f"Multicolour plate {title}: filament use {grams}, needs {sorted(needed)}"
        multicolour[title] = dict(plate=index, hours=round(plate.get("total_predication", 0) / 3600, 2),
                                  grams_by_filament=grams, warnings=plate.get("warning_message"))
        print(f"Slice multicolour plate {title}: PASS, filament use {grams} g", flush=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate, target)
    print(f"Project 3MF published -> {target.relative_to(ROOT)}", flush=True)
    return dict(file=str(target.relative_to(ROOT)), parts=placed, plates=len(plate_ids), layout=layout,
                total_hours_plates=round(sum(s["hours"] for s in plate_slices.values()), 1),
                total_grams_plates=round(sum(sum(s["grams_by_filament"].values()) for s in plate_slices.values()), 1),
                multicolour_parts=COLOR_PARTS, multicolour_slices=multicolour, pause_slices=pauses, plate_slices=plate_slices,
                own_infill_parts=own_infill, sha256=hashlib.sha256(target.read_bytes()).hexdigest())


def custom_gcode_xml(pause_plates, gcode):
    """Bambu project pauses: Metadata/custom_gcode_per_layer.xml, type 1 = pause print."""
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<custom_gcodes_per_layer>"]
    for index, heights in sorted(pause_plates.items()):
        lines += ["<plate>", f'<plate_info id="{index + 1}"/>']
        lines += [f'<layer top_z="{z:g}" type="1" extruder="1" color="" extra="" gcode="{gcode}"/>' for z in heights]
        lines += ['<mode value="MultiAsSingle"/>', "</plate>"]
    return "\n".join(lines + ["</custom_gcodes_per_layer>"]) + "\n"


def pause_heights(gcode_text, pause_gcode):
    """For every pause in sliced G-code: (Z_HEIGHT of the layer it sits in, whether that layer extruded before it)."""
    found, layer, extruded = [], None, False
    for line in gcode_text.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            layer, extruded = float(line.split(":")[1]), False
        elif line.strip() == pause_gcode and layer is not None:
            found.append((layer, extruded))
        elif re.match(r"G[123] .*E\d*\.?\d+", line) and not re.search(r"E-", line):
            extruded = True
    return found


def write_summary(summary):
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    (out / "summary.json").write_text(text)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(text)


solid = sorted(n for n in PARTS if infill(n, PARTS[n][1]) == 100)
with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(run, PARTS))
summary = dict(profile=f"{PRINTER['machine']} / {PRINTER['process']}, {PROCESS['wall_loops']} walls, "
                       f"{PROCESS['top_shell_layers']}/{PROCESS['bottom_shell_layers']} top/bottom, no supports; "
                       f"{DEFAULT_INFILL} % {PROCESS['pattern']}, 100 % zig-zag: {', '.join(solid) or 'none'}",
               parts=results, total_parts=sum(r["quantity"] for r in results),
               total_grams_individual_plates=round(sum(r["quantity"] * r["grams"] for r in results), 1),
               total_hours_individual_plates=round(sum(r["quantity"] * r["hours"] for r in results), 1),
               production_gcode=False)
write_summary(summary)
assert all(r["passed"] for r in results), f"Slicing failed; inspect {out}"
assert all(r["wall_loops"] == PROCESS["wall_loops"] for r in results), "Wrong diagnostic wall count"
assert all(r["infill_percent"] == infill(r["part"], r["material"]) for r in results), "Wrong diagnostic infill"
assert all(r["effective_settings"]["sparse_infill_pattern"] == pattern(infill(r["part"], r["material"])) for r in results)
assert all(r["effective_settings"]["enable_support"] == "0" for r in results)
summary["project_3mf"] = build_project_3mf()
if TEST_PLATES:
    summary["test_3mf"] = build_project_3mf(TEST_PLATES, TEST_3MF, "test-3mf", full_build=False, process_file=profiles / "process-test.json", mono=TEST_FILAMENT)
    summary["test_3mf"]["process"] = {key: TEST_PROCESS[key] for key in ("wall_loops", "top_shell_layers", "bottom_shell_layers", "infill")}
write_summary(summary)
test = summary.get("test_3mf")
print(f"PASS: {len(results)} slices; {summary['total_parts']} parts; "
      f"{summary['total_grams_individual_plates']} g; {summary['total_hours_individual_plates']} h; "
      f"project 3MF with {summary['project_3mf']['plates']} plates: {summary['project_3mf']['total_grams_plates']} g; "
      f"{summary['project_3mf']['total_hours_plates']} h as plates"
      + (f"; test 3MF with {test['plates']} plates: {test['total_grams_plates']} g; {test['total_hours_plates']} h" if test else ""))
