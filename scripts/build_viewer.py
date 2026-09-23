#!/usr/bin/env python3
"""Build the self-contained 3D assembly viewer page (skill openscad-print-project).

VIEWER in print_project.py lists the rows. Meshes come from ASM_DIR/<id>.stl (print_tools.py export) or,
for ids in VIEWER["bodies"], are exported here from OpenSCAD code: vendor meshes, multicolour pieces in
installed position (<id>_base, <id>_<inlay> for ids in VIEWER["colour"]). "$ROOT" in that code is the
project root. Those exports are cached by a hash of every *.scad in the root, the code and the imported
files, so a moved part never shows a stale mesh. Output: VIEWER["output"] (default build/viewer.html),
to be published as an artifact; --copy-to also writes it to a second path.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

import numpy as np
import trimesh

from print_tools import ASM_DIR, BUILD, P, ROOT, SOURCE

V = P.VIEWER
TEMPLATE = Path(__file__).with_name("viewer_tpl.html")
OUT = BUILD / "viewer"
IMPORT = re.compile(r'import\s*\(\s*"([^"]+)"')


def body_key(code):
    digest = hashlib.sha256(code.encode())
    for path in sorted(ROOT.glob("*.scad")):
        digest.update(path.read_bytes())
    for path in IMPORT.findall(code):
        digest.update(Path(path).read_bytes() if Path(path).exists() else b"missing")
    return digest.hexdigest()


def export_body(item):
    name, code = item
    code = code.replace("$ROOT", ROOT.as_posix())
    path, stamp = OUT / f"{name}.stl", OUT / f"{name}.key"
    key = body_key(code)
    if path.exists() and stamp.exists() and stamp.read_text() == key:
        return name, "cached"
    missing = [p for p in IMPORT.findall(code) if not Path(p).exists()]
    if missing:
        path.unlink(missing_ok=True)
        return name, f"skipped, missing {missing}"
    wrapper = OUT / f"{name}.scad"
    wrapper.write_text(f"include <{SOURCE.as_posix()}>\n{code}\n")
    command = [shutil.which("openscad") or "openscad", "--backend=Manifold", "--export-format", "binstl",
               "-D", 'part="none"', "-o", str(path), str(wrapper)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Viewer body {name} failed:\n{(result.stdout + result.stderr)[-3000:]}")
    stamp.write_text(key)
    return name, "exported"


def encode(path):
    mesh = trimesh.load_mesh(path, process=False)
    triangles = np.asarray(mesh.triangles, dtype="<f4").reshape(-1, 9)
    record = np.zeros(len(triangles), dtype=[("normal", "<f4", 3), ("v", "<f4", 9), ("attr", "<u2")])
    record["v"] = triangles    # the page computes flat normals itself
    data = b"\0" * 80 + np.uint32(len(triangles)).tobytes() + record.tobytes()
    return base64.b64encode(data).decode(), mesh.bounds, len(triangles)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--copy-to", type=Path, help="also write the page here (e.g. the published artifact path)")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    bodies = V.get("bodies", {})
    with ThreadPoolExecutor(max_workers=4) as pool:
        for name, state in pool.map(export_body, bodies.items()):
            print(f"Viewer body {name}: {state}", flush=True)
    colour = V.get("colour", {})
    parts, low, high = [], np.full(3, np.inf), np.full(3, -np.inf)

    def add(body, pid, path, label, group, col, qty, direction):
        nonlocal low, high
        if not path.exists():
            print(f"missing: {path.relative_to(ROOT)}")
            return
        stl, bounds, count = encode(path)
        low, high = np.minimum(low, bounds[0]), np.maximum(high, bounds[1])
        size = bounds[1] - bounds[0]
        parts.append(dict(id=pid, body=body, label=label, group=group, color=col, qty=qty, dir=direction,
                          tris=count, ext="%.0f × %.0f × %.0f mm" % tuple(size), stl=stl))

    for pid, label, group, col, qty, direction in V["parts"]:
        base = OUT / f"{pid}_base.stl"
        if pid in colour and base.exists():
            add(pid, pid, base, label, group, col, qty, direction)
            for piece, text, piece_colour in colour[pid]:
                add(pid, f"{pid}_{piece}", OUT / f"{pid}_{piece}.stl", text, group, piece_colour, qty, direction)
        elif pid in bodies:
            add(pid, pid, OUT / f"{pid}.stl", label, group, col, qty, direction)
        else:
            add(pid, pid, ASM_DIR / f"{pid}.stl", label, group, col, qty, direction)
    meta = dict(title=V["title"], eyebrow=V.get("eyebrow", "Assembly · installed position"), dims=V.get("dims", []), ui=V.get("ui", {}),
                groups=V.get("groups", []), hidden_groups=V.get("hidden_groups", []), toggle_groups=V.get("toggle_groups", []),
                swaps=V.get("swaps", []),
                outer=V.get("outer", []), cut=V.get("cut", []), screens=V.get("screens", []),
                bounds=[low.round(2).tolist(), high.round(2).tolist()],
                center=((low + high) / 2).round(2).tolist(), size=float(np.max(high - low)))
    page = TEMPLATE.read_text().replace("__TITLE__", V.get("page_title", V["title"]))
    page = page.replace("/*__DATA__*/", "window.PART_DATA=" + json.dumps(dict(meta=meta, parts=parts), ensure_ascii=False) + ";")
    target = ROOT / V.get("output", "build/viewer.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page)
    if args.copy_to:
        args.copy_to.parent.mkdir(parents=True, exist_ok=True)
        args.copy_to.write_text(page)
    megabytes = len(page.encode()) / 1e6
    print(f"{target.relative_to(ROOT)}: {megabytes:.1f} MB, {len(parts)} rows")
    if megabytes > 15:
        print("WARNING: artifacts are limited to 16 MB; simplify vendor meshes or hide bodies")


if __name__ == "__main__":
    main()
