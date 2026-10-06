#!/usr/bin/env python3
"""Diagnostic Bambu Studio slicing and the multi-plate project 3MF (skill openscad-print-project).

1. Slices every print STL on its own with the installed system profiles (PRINTER, PROCESS, FILAMENTS in
   print_project.py): supports off unless explicitly enabled, default infill, solid for FULL_INFILL parts and FULL_INFILL_MATERIALS.
2. Builds PROJECT_3MF: every part of the full build on the fixed PLATES, each plate centred; multicolour
   parts as one object per copy with their inlay filaments, parts at the left edge and the prime tower
   to their right (CENTRE_PLATES: parts centred, tower behind or in front of them). Every plate is sliced (layout, instances, effective settings); multicolour plates also prove the inlays print.
3. Optional TEST_PLATES (e.g. fit tests; entries are part names or (name, count), one copy by default) become TEST_3MF
   the same way, with TEST_PROCESS overriding PROCESS (e.g. fewer walls and less infill: same geometry, less material).
   TEST_FILAMENT = slot prints every test part single-colour from that filament slot (no inlays, no prime tower).
   PART_INFILL = {part: percent} changes production/diagnostic infill, preserving solid parts and TEST_PROCESS.
   PART_FILAMENTS = {part: slot} selects a plain base slot per part; slots are 1-based and must match its material.

Generated G-code and 3MF files under build/ are diagnostics, NOT print releases.
Writes build/slicer-diagnostic/summary.json and SLICER_SUMMARY (default docs/slicer-summary.json).
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
from xml.sax.saxutils import quoteattr
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import manifold3d as md
import trimesh

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
               bed="Engineering Plate") | getattr(P, "PRINTER", {})
# PROCESS["settings"]: further Bambu process keys for every part, e.g. {"infill_direction": "0"} (first-layer lines
# along x, parallel to a long bed face; Bambu alternates solid layers by 90 degrees from there)
def merge_process(base, overrides):
    """Keep shared settings through project/test overrides, including the legacy first-wall alias."""
    merged = base | overrides
    settings = dict(base.get("settings", {}))
    key = "only_one_wall_first_layer"
    if key in overrides:
        settings[key] = str(int(overrides[key]))
    settings.update(overrides.get("settings", {}))
    for flag in (key, "enable_support"):
        if flag in settings:
            settings[flag] = str(int(settings[flag]))
    merged.pop(key, None)
    merged["settings"] = settings
    return merged


PROCESS = merge_process(dict(wall_loops=4, top_shell_layers=5, bottom_shell_layers=5, infill=25,
                             pattern="gyroid", settings={"only_one_wall_first_layer": "1", "enable_support": "0"}),
                        getattr(P, "PROCESS", {}))
PART_INFILL = getattr(P, "PART_INFILL", {})
FULL_INFILL = set(getattr(P, "FULL_INFILL", ()))
FULL_INFILL_MATERIALS = set(getattr(P, "FULL_INFILL_MATERIALS", ("TPU",)))
# Filament slots of the project 3MF, 1-based in list order; inlay slots name their inlay or a tuple of inlays sharing the slot
FILAMENTS = getattr(P, "FILAMENTS", None) or [dict(material=m, profile=f"Generic {m} @BBL H2S")
                                              for m in sorted({m for _, m, _ in PARTS.values()})]
PART_FILAMENTS = getattr(P, "PART_FILAMENTS", {})
PLATES = getattr(P, "PLATES", None) or [(name, [name]) for name in PARTS if PARTS[name][0] > 0]
# Successive virtual plates use distinct contact regions of one fully sprayed physical bed.
BED_REUSE = getattr(P, "BED_REUSE", None)
# Multicolour plates (by title) whose parts stay in the middle of the bed, prime tower behind or in front of them
# instead of parts at the left edge and the tower beside them
CENTRE_PLATES = set(getattr(P, "CENTRE_PLATES", ()))
assert CENTRE_PLATES <= {title for title, _ in PLATES}, f"CENTRE_PLATES names unknown plates: {sorted(CENTRE_PLATES - {t for t, _ in PLATES})}"
# Print pauses (e.g. to embed magnets or lay mesh): part -> print_z of the first layer printed after the pause.
# A pause stops its whole plate, so give such parts their own plate.
PAUSES = getattr(P, "PAUSES", {})
# Extra nozzle/bed clearance while inserting hardware; zero keeps the stock machine pause.
PAUSE_LIFT_MM = float(getattr(P, "PAUSE_LIFT_MM", 30))
PROJECT_3MF = ROOT / getattr(P, "PROJECT_3MF", f"{STL_DIR.relative_to(ROOT).as_posix()}/{ROOT.name}_all_parts.3mf")
# Test prints (fit tests, samples) as their own project: plates of part names or (name, count), one copy by default
TEST_PLATES = getattr(P, "TEST_PLATES", [])
TEST_PROCESS = merge_process(PROCESS, getattr(P, "TEST_PROCESS", {}))
TEST_FILAMENT = getattr(P, "TEST_FILAMENT", None)
TEST_3MF = ROOT / getattr(P, "TEST_3MF", f"{STL_DIR.relative_to(ROOT).as_posix()}/{ROOT.name}_test_prints.3mf")
SUMMARY = ROOT / getattr(P, "SLICER_SUMMARY", "docs/slicer-summary.json")
INLAY_FILAMENT = {inlay: i for i, f in enumerate(FILAMENTS, 1)
                  for inlay in ((f["inlay"],) if isinstance(f.get("inlay"), str) else f.get("inlay", ()))}
DEFAULT_INFILL = int(PROCESS["infill"])
# Keep already chosen STL orientations and centre their actual geometry explicitly.
# Useful when the arranger's projected brim margin rejects an otherwise valid print pose.
FIXED_PRINT_POSES = bool(getattr(P, "FIXED_PRINT_POSES", False))
# Optional absolute bed-local bounding-box minima, one [x, y] per copy.
PLATE_PART_POSITIONS = getattr(P, "PLATE_PART_POSITIONS", None)


def base_filament(material):
    return next(i for i, f in enumerate(FILAMENTS, 1) if f["material"] == material and not f.get("inlay"))


def validate_plain_slot(slot, label):
    assert type(slot) is int and 1 <= slot <= len(FILAMENTS), \
        f"{label}: filament slot must be an integer in 1..{len(FILAMENTS)}, got {slot!r}"
    assert not FILAMENTS[slot - 1].get("inlay"), f"{label}: slot {slot} is reserved for inlays"
    return slot


def part_filament(name, mono=None):
    # The explicit single-colour test choice takes precedence over the normal part palette.
    if mono is not None:
        return validate_plain_slot(mono, "TEST_FILAMENT")
    return PART_FILAMENTS[name] if name in PART_FILAMENTS else base_filament(PARTS[name][1])


def validate_part_filaments():
    assert isinstance(PART_FILAMENTS, dict), "PART_FILAMENTS must map part names to 1-based filament slots"
    assert set(PART_FILAMENTS) <= set(PARTS), \
        f"PART_FILAMENTS names unknown parts: {sorted(set(PART_FILAMENTS) - set(PARTS))}"
    for name, slot in PART_FILAMENTS.items():
        validate_plain_slot(slot, f"PART_FILAMENTS[{name!r}]")
        assert FILAMENTS[slot - 1]["material"] == PARTS[name][1], \
            f"{name}: slot {slot} material {FILAMENTS[slot - 1]['material']} differs from {PARTS[name][1]}"
    if TEST_FILAMENT is not None:
        validate_plain_slot(TEST_FILAMENT, "TEST_FILAMENT")


def expected_filaments(name, mono=None):
    if mono is None and name in COLOR_PARTS:
        return {f"{name}_base": part_filament(name),
                **{f"{name}_{inlay}": INLAY_FILAMENT[inlay] for inlay in COLOR_PARTS[name]}}
    return {name: part_filament(name, mono)}


def verify_object_filaments(model_settings, mono=None):
    """Verify every saved volume, including mono parts and sliced per-volume overrides."""
    found = {}
    for obj in ET.fromstring(model_settings).findall("object"):
        own = {m.get("key"): m.get("value") for m in obj.findall("metadata") if m.get("key")}
        name = slicer_part_name(own["name"], PARTS)
        assert name in PARTS, f"Unknown filament-assigned object {name}"
        actual = {}
        for part in obj.findall("part"):
            meta = {m.get("key"): m.get("value") for m in part.findall("metadata") if m.get("key")}
            piece = slicer_part_name(meta["name"], expected_filaments(name, mono))
            actual[piece] = int(meta.get("extruder", own.get("extruder", "0")))
        wanted = expected_filaments(name, mono)
        assert actual == wanted, f"{name}: filament slots {actual}, expected {wanted}"
        found[name] = actual
    return found


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


def validate_part_infill():
    assert isinstance(PART_INFILL, dict), "PART_INFILL must map part names to integer percentages"
    assert set(PART_INFILL) <= set(PARTS), \
        f"PART_INFILL names unknown parts: {sorted(set(PART_INFILL) - set(PARTS))}"
    for name, density in PART_INFILL.items():
        assert type(density) is int and 0 <= density <= 100, \
            f"PART_INFILL[{name!r}] must be an integer percentage in 0..100, got {density!r}"
        assert density == 100 or not (name in FULL_INFILL or PARTS[name][1] in FULL_INFILL_MATERIALS), \
            f"{name}: PART_INFILL cannot reduce a FULL_INFILL part or material"


def infill(name, material, full_build=True):
    if material in FULL_INFILL_MATERIALS or name in FULL_INFILL:
        return 100
    # Fit-test process settings deliberately supersede production part tuning.
    return PART_INFILL.get(name, DEFAULT_INFILL) if full_build else int(TEST_PROCESS["infill"])


def pattern(density, full_build=True):
    # Bambu serializes Rectilinear as "zig-zag" ("rectilinear" maps to cubic); gyroid is refused at 100 %
    return "zig-zag" if density == 100 else (PROCESS if full_build else TEST_PROCESS)["pattern"]


def set_object_infill(model_settings, names, project_settings, full_build=True):
    """Store whole-object density/pattern overrides; colour volumes must not override them."""
    keys = ("sparse_infill_density", "sparse_infill_pattern")
    def configured(match):
        object_id, body = match.group(1), match.group(2)
        for key in keys:
            body = re.sub(rf'\s*<metadata key="{key}" value="[^"]*"\s*/>', "", body)
        head, separator, rest = body.partition("<part ")
        name = names[object_id]
        density = infill(name, PARTS[name][1], full_build)
        wanted = dict(sparse_infill_density=f"{density}%", sparse_infill_pattern=pattern(density, full_build))
        for key, value in wanted.items():
            if value != project_settings.get(key):
                head += ET.tostring(ET.Element("metadata", key=key, value=value), encoding="unicode") + "\n"
        return f'<object id="{object_id}">{head}{separator}{rest}</object>'
    return re.sub(r'<object id="(\d+)">(.*?)</object>', configured, model_settings, flags=re.S)


def verify_object_infill(project_settings, model_settings, full_build=True):
    """Check effective object settings and all copies after saving or slicing."""
    keys = ("sparse_infill_density", "sparse_infill_pattern")
    found = {}
    for obj in ET.fromstring(model_settings).findall("object"):
        own = {m.get("key"): m.get("value") for m in obj.findall("metadata")}
        stem = Path(own["name"]).stem
        name = stem if stem in PARTS else re.sub(r"_\d+$", "", stem)
        assert name in PARTS, f"Unknown infill-assigned object {name}"
        density = infill(name, PARTS[name][1], full_build)
        wanted = dict(sparse_infill_density=f"{density}%", sparse_infill_pattern=pattern(density, full_build))
        actual = {key: own.get(key, project_settings.get(key)) for key in keys}
        assert actual == wanted, f"{name}: effective infill {actual}, expected {wanted}"
        for part in obj.findall("part"):
            overrides = {m.get("key"): m.get("value") for m in part.findall("metadata")}
            assert all(overrides.get(key, actual[key]) == actual[key] for key in keys), \
                f"{name}: colour volume changes effective infill"
        row = found.setdefault(name, dict(instances=0, **actual))
        row["instances"] += 1
    return found


validate_part_filaments()
validate_part_infill()
for material in {m for _, m, _ in PARTS.values()}:
    base_filament(material)                       # every material needs a plain slot
for name, inlays in COLOR_PARTS.items():
    assert all(inlay in INLAY_FILAMENT for inlay in inlays), f"{name}: no FILAMENTS slot for {inlays}"

def insertion_pause_gcode(native_gcode, lift_mm, relative_e=True):
    """Lower a Bambu bed for insertion, preserving its native parking/resume operation."""
    assert math.isfinite(lift_mm) and lift_mm >= 0, "PAUSE_LIFT_MM must be finite and nonnegative"
    if not lift_mm:
        return native_gcode
    assert native_gcode.strip() == "M400 U1", "Extra pause clearance requires the stock Bambu M400 U1 pause"
    e_mode = "M83" if relative_e else "M82"
    return "\n".join(["; INSERTION_PAUSE_BEGIN", "M400", "G91", f"G1 Z{lift_mm:g} F600", "M400",
                      "G90", e_mode, native_gcode.strip(), "G91", f"G1 Z{-lift_mm:g} F600", "M400",
                      "G90", e_mode, "; INSERTION_PAUSE_END"])


machine = resolve(PRINTER["machine"])
machine["curr_bed_type"] = PRINTER["bed"]
native_pause_gcode = machine.get("machine_pause_gcode", "M400 U1")
native_pause_gcode = (native_pause_gcode[0] if isinstance(native_pause_gcode, list) else native_pause_gcode).strip()
relative_e = str(machine.get("use_relative_e_distances", "1")) == "1"
if PAUSES:
    machine["machine_pause_gcode"] = insertion_pause_gcode(native_pause_gcode, PAUSE_LIFT_MM, relative_e)
(profiles / "machine.json").write_text(json.dumps(machine, indent=2))


def write_process(name, settings, density):
    process = resolve(PRINTER["process"])
    process.update(wall_loops=str(settings["wall_loops"]), sparse_infill_density=f"{density}%", enable_support="0",
                   top_shell_layers=str(settings["top_shell_layers"]),
                   bottom_shell_layers=str(settings["bottom_shell_layers"]),
                   sparse_infill_pattern="zig-zag" if density == 100 else settings["pattern"])
    process.update({key: str(value) for key, value in settings.get("settings", {}).items()})
    (profiles / name).write_text(json.dumps(process, indent=2))


def verify_process_overrides(actual, profile):
    """Confirm saved/sliced profiles retain the requested wall count and process overrides."""
    wanted = json.loads(profile.read_text())
    keys = {"wall_loops", *PROCESS["settings"], *TEST_PROCESS["settings"]} & wanted.keys()
    for key in keys:
        assert actual.get(key) == wanted[key], f"Process setting {key}: {actual.get(key)!r}, wanted {wanted[key]!r}"
    return {key: actual[key] for key in sorted(keys)}


for density in {infill(n, m) for n, (_, m, _) in PARTS.items()} | {DEFAULT_INFILL}:
    write_process(f"process-{density}.json", PROCESS, density)
if TEST_PLATES:
    write_process("process-test.json", TEST_PROCESS, int(TEST_PROCESS["infill"]))
for slot, filament in enumerate(FILAMENTS, 1):
    profile = resolve(filament["profile"])
    if filament.get("colour"):
        profile["filament_colour"] = [filament["colour"]]
    (profiles / f"filament-{slot}.json").write_text(json.dumps(profile, indent=2))


def centred_diagnostic_3mf(source, target, printer):
    """Package one STL at the bed centre without rotating, scaling or relaxing slicer checks."""
    mesh = trimesh.load_mesh(source, process=False)
    low, high = mesh.bounds
    bed = [[float(value) for value in point.split("x")] for point in printer["printable_area"]]
    bed_low = [min(point[axis] for point in bed) for axis in range(2)]
    bed_high = [max(point[axis] for point in bed) for axis in range(2)]
    extent = high - low
    limit = [*(bed_high[axis] - bed_low[axis] for axis in range(2)), float(printer["printable_height"])]
    assert all(size <= maximum + 1e-4 for size, maximum in zip(extent, limit)), \
        f"{source.name}: fixed print pose {extent.tolist()} exceeds {limit}"
    delta = [(bed_low[axis] + bed_high[axis] - low[axis] - high[axis]) / 2 for axis in range(2)] + [-low[2]]
    # STL repeats vertices per triangle. 3MF needs shared indices for closed adjacency;
    # otherwise Bambu can discard a small valid mesh as empty. Weld exact duplicates only.
    unique_vertices, vertex_index = np.unique(mesh.vertices, axis=0, return_inverse=True)
    vertices = ''.join(f'<vertex x="{v[0]:.9g}" y="{v[1]:.9g}" z="{v[2]:.9g}"/>' for v in unique_vertices)
    triangles = ''.join(f'<triangle v1="{face[0]}" v2="{face[1]}" v3="{face[2]}"/>'
                        for face in vertex_index[mesh.faces])
    transform = '1 0 0 0 1 0 0 0 1 ' + ' '.join(f'{value:.9g}' for value in delta)
    model = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources><object id="1" type="model" name={quoteattr(source.stem)}><mesh>'
             f'<vertices>{vertices}</vertices><triangles>{triangles}</triangles></mesh></object></resources>'
             f'<build><item objectid="1" transform="{transform}"/></build></model>')
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml',
                         '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                         '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        archive.writestr('_rels/.rels',
                         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                         '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
                         'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        archive.writestr('3D/3dmodel.model', model)
    return dict(mode="fixed_centred", translation_mm=[float(value) for value in delta],
                bounds_mm=(mesh.bounds + delta).tolist())


def run(name):
    quantity, material, _ = PARTS[name]
    folder = out / name
    folder.mkdir(exist_ok=True)
    source = STL_DIR / f"{name}.stl"
    slice_input = source
    positioning = dict(mode="automatic")
    if FIXED_PRINT_POSES:
        slice_input = folder / f"{name}-CENTRED.3mf"
        positioning = centred_diagnostic_3mf(source, slice_input, machine)
    # never read a result of an earlier run
    for stale in (folder / "result.json", folder / f"{name}-DIAGNOSTIC.3mf"):
        stale.unlink(missing_ok=True)
    command = [str(executable), "--datadir", str(folder / "config"), "--debug", "2",
               "--load-settings", f"{profiles / 'machine.json'};{profiles / f'process-{infill(name, material)}.json'}",
               "--load-filaments", str(profiles / f"filament-{part_filament(name)}.json"),
               "--orient", "0", "--arrange", "0" if FIXED_PRINT_POSES else "1", "--slice", "0",
               # --outputdir must be absolute, otherwise the CLI exits with 243
               "--export-3mf", f"{name}-DIAGNOSTIC.3mf", "--outputdir", str(folder), str(slice_input)]
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
            verify_process_overrides(settings, profiles / f"process-{infill(name, material)}.json")
            assert settings.get("curr_bed_type") == PRINTER["bed"], f"{name}: diagnostic lost bed type"
    row = dict(part=name, quantity=quantity, material=material, filament_slot=part_filament(name), passed=passed,
               positioning=positioning,
               source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
               exit_code=result.returncode, result_code=data.get("return_code"),
               warnings=plate.get("warning_message"),
               hours=round(plate.get("total_predication", 0) / 3600, 3),
               grams=round(sum(f["total_used_g"] for f in plate.get("filaments", [])), 3),
               wall_loops=data.get("wall_loops"), infill_percent=data.get("sparse_infill_density"),
               layer_height=data.get("layer_height"),
               effective_settings={key: settings.get(key) for key in
                                   ("sparse_infill_pattern", "enable_support", "curr_bed_type",
                                    "top_shell_layers", "bottom_shell_layers", *PROCESS["settings"])},
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


def slicer_part_name(raw_name, known_names):
    """Preserve source names; only remove a CLI copy number when its source is known."""
    if raw_name in known_names:
        return raw_name
    original, separator, copy_number = raw_name.rpartition("_")
    if separator and copy_number.isdigit() and original in known_names:
        return original
    raise ValueError(f"Unknown slicer part name: {raw_name!r}")


def project_object_name(piece_names, part_names, colour_parts):
    """Map an object to an exact part or a complete, explicitly declared colour assembly."""
    pieces = set(piece_names)
    if len(pieces) == 1 and next(iter(pieces)) in part_names:
        return next(iter(pieces))
    matches = [name for name, inlays in colour_parts.items()
               if pieces == {f"{name}_{piece}" for piece in ("base", *inlays)}]
    if len(matches) == 1:
        return matches[0]
    raise ValueError(f"Unexpected slicer object parts: {sorted(pieces)}")


def plate_counts(group, full_build):
    """Plate entries are part names or (name, count); names take the PARTS quantity in the full build, else one copy."""
    return dict((entry, PARTS[entry][0] if full_build else 1) if isinstance(entry, str) else tuple(entry) for entry in group)


def archive_geometry_bounds(archive, per_item=False):
    """Measure the actual transformed objects saved by Bambu, including colour components."""
    documents = {}
    result = np.array([[float("inf")] * 3, [float("-inf")] * 3])

    def document(path):
        if path not in documents:
            documents[path] = ET.fromstring(archive.read(path))
        return documents[path]

    def matrix(text):
        value = np.eye(4)
        value[:3, :] = transform(text)
        return value

    def visit(path, object_id, outer, ancestry=()):
        nonlocal result
        assert (path, object_id) not in ancestry, "Cyclic 3MF component reference"
        obj = document(path).find(f"{{*}}resources/{{*}}object[@id='{object_id}']")
        assert obj is not None, f"Missing 3MF object {path}:{object_id}"
        points = obj.findall("{*}mesh/{*}vertices/{*}vertex")
        if points:
            vertices = np.array([[float(point.get(axis)) for axis in "xyz"] for point in points])
            placed = vertices @ outer[:3, :3].T + outer[:3, 3]
            result[0] = np.minimum(result[0], placed.min(axis=0))
            result[1] = np.maximum(result[1], placed.max(axis=0))
        for component in obj.findall("{*}components/{*}component"):
            next_path = next((value.lstrip("/") for key, value in component.attrib.items()
                              if key.endswith("}path") or key == "path"), path)
            visit(next_path, component.get("objectid"), outer @ matrix(component.get("transform")),
                  (*ancestry, (path, object_id)))

    item_bounds = []
    for item in document("3D/3dmodel.model").findall("{*}build/{*}item"):
        result = np.array([[float("inf")] * 3, [float("-inf")] * 3])
        visit("3D/3dmodel.model", item.get("objectid"), matrix(item.get("transform")))
        assert np.isfinite(result).all(), "Missing finite 3MF geometry bounds"
        item_bounds.append(result.copy())
    assert item_bounds, "Missing 3MF build items"
    if per_item:
        return item_bounds
    return np.array([np.min([b[0] for b in item_bounds], axis=0),
                     np.max([b[1] for b in item_bounds], axis=0)])


def plate_part_positions_configuration(config, resolved, colour_parts):
    """Validate an exact per-copy manifest; explicit positions currently require monochrome parts."""
    if config is None:
        return {}
    assert isinstance(config, dict), "PLATE_PART_POSITIONS must be a mapping"
    assert set(config) == {title for title, _ in resolved}, \
        "PLATE_PART_POSITIONS must name every production plate exactly once"
    result = {}
    for title, group in resolved:
        positions = config[title]
        assert isinstance(positions, dict) and set(positions) == set(group), \
            f"PLATE_PART_POSITIONS {title}: part keys must exactly match the plate"
        assert not set(group) & set(colour_parts), \
            f"PLATE_PART_POSITIONS {title}: multicolour component placement is not supported"
        result[title] = {}
        for name, count in group.items():
            copies = positions[name]
            assert isinstance(copies, (list, tuple)) and len(copies) == count, \
                f"PLATE_PART_POSITIONS {title}/{name}: expected {count} positions"
            for point in copies:
                assert isinstance(point, (list, tuple)) and len(point) == 2 and all(
                    isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
                    for v in point), f"PLATE_PART_POSITIONS {title}/{name}: positions require two finite coordinates"
            result[title][name] = [[float(v) for v in point] for point in copies]
    return result


def explicit_part_placements(title, positions, mesh_bounds, printer):
    """Place unchanged STL poses, checking each bounding rectangle and known excluded areas."""
    bed_points = [[float(v) for v in point.split("x")] for point in printer["printable_area"]]
    bed = md.CrossSection([bed_points])
    excluded_points = [[float(v) for v in point.split("x")]
                       for point in printer.get("bed_exclude_area", [])]
    excluded = md.CrossSection([excluded_points]) if excluded_points else md.CrossSection()
    rows, transforms, footprints = [], {}, []
    for name, copies in positions.items():
        bounds = np.asarray(mesh_bounds[name], dtype=float)
        assert bounds.shape == (2, 3) and np.isfinite(bounds).all(), f"{title}/{name}: invalid STL bounds"
        size = bounds[1] - bounds[0]
        assert np.all(size > 0), f"{title}/{name}: empty STL extent"
        assert size[2] <= float(printer["printable_height"]) + 0.001, f"{title}/{name}: exceeds bed height"
        transforms[name] = []
        for copy, point in enumerate(copies, 1):
            delta = np.array([*point, 0.0]) - bounds[0]
            placed = bounds + delta
            footprint = md.CrossSection.square(size[:2]).translate(point)
            assert (footprint - bed).area() <= 0.001, f"{title}/{name}[{copy}]: outside printable bed"
            assert (footprint ^ excluded).area() <= 0.001, f"{title}/{name}[{copy}]: overlaps excluded bed area"
            for other_name, other_copy, other_footprint in footprints:
                assert (footprint ^ other_footprint).area() <= 0.001, \
                    f"{title}: print bounding boxes overlap: {other_name}[{other_copy}] and {name}[{copy}]"
            transforms[name].append(delta.tolist())
            footprints.append((name, copy, footprint))
            rows.append(dict(part=name, copy=copy, min_xy=list(point), bounds_mm=placed.tolist()))
    return transforms, rows


def assert_instance_bounds(expected, actual, message):
    """Compare all instance bounds, not only their common envelope."""
    assert len(expected) == len(actual), f"{message}: instance count changed"
    expected = sorted(tuple(np.asarray(b).reshape(-1)) for b in expected)
    actual = sorted(tuple(np.asarray(b).reshape(-1)) for b in actual)
    assert np.allclose(actual, expected, atol=0.01, rtol=0), message


def bed_reuse_configuration(config, titles):
    """Require explicit, complete reusable-bed batches and bed-local group placements."""
    if not config:
        return {}, {}
    assert isinstance(config, dict), "BED_REUSE must be a mapping"
    batches = config.get("batches", [])
    flat = [title for batch in batches for title in batch]
    assert batches and all(batches), "BED_REUSE needs nonempty batches"
    assert sorted(flat) == sorted(titles), "BED_REUSE batches must name every production plate exactly once"
    placements = config.get("placements", {})
    assert set(placements) == set(titles), "BED_REUSE placements must name every production plate"
    clearance = float(config.get("clearance_mm", 5))
    assert math.isfinite(clearance) and clearance >= 0, "BED_REUSE clearance_mm must be finite and nonnegative"
    for title, placement in placements.items():
        assert isinstance(placement, dict) and "min_xy" in placement, f"BED_REUSE {title}: missing min_xy"
        for key, point in placement.items():
            assert key in ("min_xy", "prime_tower_xy"), f"BED_REUSE {title}: unknown placement {key}"
            assert len(point) == 2 and all(math.isfinite(float(v)) for v in point), \
                f"BED_REUSE {title}: {key} must have two finite coordinates"
    return placements, {title: index for index, batch in enumerate(batches, 1) for title in batch}


def first_layer_contact(gcode, clearance_mm=5, cell_mm=1):
    """Conservative sampled contact grid, including Bambu brims, skirts and prime towers.

    Every extrusion curve is sampled at <= 0.5 cell; its samples are expanded by half that
    distance and a cell circumradius as well as line radius and half the reuse clearance.
    Thus the grid covers the complete swept contact footprint, not only sample points.
    The separately reported native start sequence is never counted as fresh reusable area.
    """
    assert clearance_mm >= 0 and cell_mm > 0
    position = {axis: None for axis in "XYZE"}
    absolute, relative_e = True, False
    layer, width, feature = 0, 0.5, "Custom"
    cells, widths, features = set(), set(), set()
    bounds = [[float("inf")] * 2, [float("-inf")] * 2]
    startup_bounds = [[float("inf")] * 2, [float("-inf")] * 2]
    segments, startup_segments = 0, 0
    max_step = cell_mm / 2
    disks = {}

    def cover(points, line_width, active):
        nonlocal segments, startup_segments
        target = bounds if active else startup_bounds
        radius = line_width / 2
        # Sampling arc chords misses extrema by at most max_step/2; retain that reserve.
        for point in points:
            for axis in range(2):
                target[0][axis] = min(target[0][axis], point[axis] - radius - max_step / 2)
                target[1][axis] = max(target[1][axis], point[axis] + radius + max_step / 2)
        if not active:
            startup_segments += 1
            return
        segments += 1
        widths.add(line_width)
        features.add(feature)
        # Snap samples to grid centres: two circumradii cover both the snapping offset
        # and any intersected cell. Extra cells only make the reuse check stricter.
        expanded = radius + clearance_mm / 2 + max_step / 2 + math.sqrt(2) * cell_mm
        key = round(expanded, 6)
        if key not in disks:
            limit = math.ceil(expanded / cell_mm)
            disks[key] = [(x, y) for x in range(-limit, limit + 1) for y in range(-limit, limit + 1)
                          if math.hypot(x * cell_mm, y * cell_mm) <= expanded]
        offsets = disks[key]
        for x, y in points:
            cx, cy = math.floor(x / cell_mm), math.floor(y / cell_mm)
            cells.update((cx + dx, cy + dy) for dx, dy in offsets)

    for raw in gcode.splitlines():
        line = raw.strip()
        if re.fullmatch(r";\s*(?:CHANGE_LAYER|LAYER_CHANGE)", line):
            layer += 1
            if layer > 1:
                break
        match = re.match(r";\s*(?:FEATURE|TYPE):\s*(.*)", line)
        if match:
            feature = match.group(1)
        match = re.match(r";\s*(?:LINE_WIDTH|WIDTH):\s*([\d.]+)", line)
        if match:
            width = float(match.group(1))
            assert 0 < width < 10, f"Invalid extrusion width: {width}"
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        words = dict((key, float(value)) for key, value in re.findall(r"([XYZEFIJP])\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))", code))
        command = code.split()[0]
        if command in ("G90", "G91"):
            absolute = command == "G90"
        elif command in ("M82", "M83"):
            relative_e = command == "M83"
        elif command == "G92":
            position.update({key: value for key, value in words.items() if key in position})
        elif command in ("G0", "G1", "G2", "G3"):
            previous = position.copy()
            for axis in "XYZ":
                if axis in words:
                    position[axis] = words[axis] if absolute else (position[axis] or 0) + words[axis]
            extrusion = words.get("E", 0) if relative_e else words.get("E", previous["E"] or 0) - (previous["E"] or 0)
            if "E" in words:
                position["E"] = (previous["E"] or 0) + extrusion
            if extrusion <= 0 or not any(key in words for key in ("X", "Y", "I", "J")):
                continue
            assert all(position[k] is not None and previous[k] is not None for k in "XY"), \
                "Cannot prove bed contact before both XY positions are known"
            start, end = tuple(previous[k] for k in "XY"), tuple(position[k] for k in "XY")
            points = []
            if command in ("G2", "G3"):
                assert "I" in words or "J" in words, "Contact arcs need I/J centre coordinates"
                centre = (start[0] + words.get("I", 0), start[1] + words.get("J", 0))
                radius = math.hypot(start[0] - centre[0], start[1] - centre[1])
                first = math.atan2(start[1] - centre[1], start[0] - centre[0])
                last = math.atan2(end[1] - centre[1], end[0] - centre[0])
                sweep = (last - first) % (2 * math.pi) if command == "G3" else -((first - last) % (2 * math.pi))
                if math.dist(start, end) < 1e-7:
                    sweep = 2 * math.pi if command == "G3" else -2 * math.pi
                steps = max(1, math.ceil(abs(sweep) * radius / max_step))
                points = [(centre[0] + radius * math.cos(first + sweep * i / steps),
                           centre[1] + radius * math.sin(first + sweep * i / steps)) for i in range(steps + 1)]
                points.append(end)
            else:
                steps = max(1, math.ceil(math.dist(start, end) / max_step))
                points = [(start[0] + (end[0] - start[0]) * i / steps,
                           start[1] + (end[1] - start[1]) * i / steps) for i in range(steps + 1)]
            cover(points, width, layer == 1)
    assert layer >= 1 and segments > 0, "Missing first-layer extrusion; cannot verify reusable bed contact"
    return dict(cells=cells, bounds_mm=[[round(v, 3) for v in row] for row in bounds],
                extrusion_segments=segments, features=sorted(features), line_widths_mm=sorted(widths),
                grid_mm=cell_mm,
                startup_bounds_mm=([[round(v, 3) for v in row] for row in startup_bounds] if startup_segments else None),
                startup_extrusion_segments=startup_segments)


def verify_bed_reuse(config, contact, printer):
    """Reject reused contact regions; keep startup purge explicitly outside that guarantee."""
    if not config:
        return None
    placements, batches = bed_reuse_configuration(config, list(contact))
    clearance = float(config.get("clearance_mm", 5))
    points = [[float(v) for v in point.split("x")] for point in printer["printable_area"]]
    bed_low = [min(point[axis] for point in points) for axis in range(2)]
    bed_high = [max(point[axis] for point in points) for axis in range(2)]
    rows = []
    for title, footprint in contact.items():
        for axis in range(2):
            assert footprint["bounds_mm"][0][axis] >= bed_low[axis] - 0.01 and \
                   footprint["bounds_mm"][1][axis] <= bed_high[axis] + 0.01, \
                f"Plate {title}: sliced bed contact extends outside the printable bed"
        rows.append(dict(name=title, batch=batches[title], placement=placements[title],
                         **{key: value for key, value in footprint.items() if key != "cells"}))
    for batch in config["batches"]:
        for index, first in enumerate(batch):
            for second in batch[index + 1:]:
                overlap = contact[first]["cells"] & contact[second]["cells"]
                assert not overlap, \
                    f"BED_REUSE batch {batches[first]}: {first} and {second} reuse first-layer contact near {next(iter(overlap), None)} mm"
    return dict(batches=config["batches"], clearance_mm=clearance, plates=rows,
                method="Conservative 1 mm contact grid from actual first-layer extrusion, including arcs, brims, skirts and prime towers",
                workflow="Remove each finished print, brim, skirt and tower before starting the next virtual plate; retain the same plate orientation",
                startup_policy="Native startup/purge/wipe/calibration remains enabled and may revisit its fixed area; reported startup bounds are not part of the fresh-area guarantee")


def build_project_3mf(plate_list=None, target=None, folder_name="project-3mf", full_build=True, process_file=None, mono=None):
    """Every part of the full build (no test prints) as one Bambu Studio project on the fixed PLATES; with
    full_build=False any plate list (test prints) into its own target file, optionally with its own process profile;
    mono = filament slot prints every part single-colour from its plain STL."""
    colour_parts = {} if mono is not None else COLOR_PARTS
    target = target or PROJECT_3MF
    process_file = process_file or profiles / f"process-{DEFAULT_INFILL}.json"
    folder = out / folder_name
    folder.mkdir(exist_ok=True)
    resolved = [(title, plate_counts(group, full_build)) for title, group in (PLATES if plate_list is None else plate_list)]
    reuse_config = BED_REUSE if full_build else None
    reuse_placements, reuse_batches = bed_reuse_configuration(reuse_config, [title for title, _ in resolved])
    explicit_positions = plate_part_positions_configuration(
        PLATE_PART_POSITIONS if full_build else None, resolved, colour_parts)
    explicit_rows = {}
    listed = [name for _, group in resolved for name in group]
    assert set(listed) <= set(PARTS), f"Plates name unknown parts: {sorted(set(listed) - set(PARTS))}"
    if full_build:
        wanted = [name for name in PARTS if PARTS[name][0] > 0]
        assert sorted(listed) == sorted(wanted), f"PLATES does not match PARTS: {sorted(set(listed) ^ set(wanted))}"
    plates, assembled = [], 0
    for title, group in resolved:
        objects = []
        translations = {}
        if title in explicit_positions:
            mesh_bounds = {name: trimesh.load_mesh(STL_DIR / f"{name}.stl", process=False).bounds for name in group}
            translations, explicit_rows[title] = explicit_part_placements(
                title, explicit_positions[title], mesh_bounds, machine)
            if title in reuse_placements:
                group_min = np.min([row["bounds_mm"][0][:2] for row in explicit_rows[title]], axis=0)
                assert np.allclose(group_min, reuse_placements[title]["min_xy"], atol=0.001, rtol=0), \
                    f"{title}: BED_REUSE min_xy conflicts with absolute PLATE_PART_POSITIONS"
        for name, quantity in group.items():
            material = PARTS[name][1]
            if name in colour_parts:
                # Base and inlays as one object with several parts: all parts of one copy share one assemble_index,
                # each copy gets its own (a shared index merges every copy into one object)
                indices = list(range(assembled + 1, assembled + quantity + 1))
                assembled += quantity
                for piece, filament in (("base", part_filament(name)),
                                        *((inlay, INLAY_FILAMENT[inlay]) for inlay in COLOR_PARTS[name])):
                    objects.append(dict(path=str(COLOR_DIR / f"{name}_{piece}.stl"), count=quantity,
                                        filaments=[filament] * quantity, assemble_index=indices))
                continue
            entry = dict(path=str(STL_DIR / f"{name}.stl"), count=quantity,
                         filaments=[part_filament(name, mono)] * quantity)
            if name in translations:
                entry.update({f"pos_{axis}": [point[i] for point in translations[name]]
                              for i, axis in enumerate("xyz")})
            objects.append(entry)
        # One complete object needs no packing; our explicit centring below preserves its pose.
        # Multi-object plates still use the arranger to avoid overlaps before centring the group.
        need_arrange = title not in explicit_positions and not (FIXED_PRINT_POSES and sum(group.values()) == 1)
        if not need_arrange and title not in explicit_positions:
            # Bambu adds the plate-grid origin later, but classifies objects by their bounds.
            # Put the complete object inside its local bed before that classification; colour
            # pieces must share the same translation rather than being centred separately.
            name = next(iter(group))
            low, high = trimesh.load_mesh(STL_DIR / f"{name}.stl", process=False).bounds
            bed = np.array([[float(value) for value in point.split("x")] for point in machine["printable_area"]])
            delta = [*((bed.min(axis=0) + bed.max(axis=0)) / 2 - (low[:2] + high[:2]) / 2), -low[2]]
            for entry in objects:
                entry.update({f"pos_{axis}": [float(value)] for axis, value in zip("xyz", delta)})
        plates.append(dict(plate_name=title, need_arrange=need_arrange, objects=objects))
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
    known_piece_names = set(PARTS) | {f"{name}_{piece}" for name, inlays in colour_parts.items()
                                    for piece in ("base", *inlays)}

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
                raw_name = re.search(r'key="name" value="([^"]+)"', part).group(1)
                parts[slicer_part_name(raw_name, known_piece_names)] = extruder.group(1)
            name = project_object_name(parts, PARTS, colour_parts)
            expected = {piece: str(slot) for piece, slot in expected_filaments(name, mono).items()}
            assert parts == expected, f"{name}: parts {parts}, expected {expected}"
            names[match.group(1)] = name
        # assembled objects are called assemble_N; give them the part name
        settings = re.sub(r'(<object id="(\d+)">\s*<metadata key="name" value=")assemble_\d+(")',
                          lambda m: m.group(1) + names[m.group(2)] + m.group(3), settings)
        object_filaments = verify_object_filaments(settings, mono)
        assert len(plate_ids) == len(resolved), f"{target.name} has {len(plate_ids)} plates, expected {len(resolved)}"
        # Plate grid like Bambu Studio: columns from the square root of the plate count, 20 % gap
        width = max(float(p.split("x")[0]) for p in machine["printable_area"])
        depth = max(float(p.split("x")[1]) for p in machine["printable_area"])
        root = len(plate_ids) ** 0.5
        columns = round(root) + 1 if root > round(root) else round(root)
        project_settings = json.loads(source.read("Metadata/project_settings.config"))
        settings = set_object_infill(settings, names, project_settings, full_build)
        object_infill = verify_object_infill(project_settings, settings, full_build)
        assert set(object_infill) == set(listed), f"{target.name}: wrong infill-configured objects"
        assert project_settings.get("curr_bed_type") == PRINTER["bed"], "Saved project lost requested bed type"
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
            if title in explicit_rows:
                for name in group:
                    expected = [row["bounds_mm"] for row in explicit_rows[title] if row["part"] == name]
                    actual = [np.array(bounds(i)) - np.array([*origin, 0]) for i in ids if names[i] == name]
                    assert_instance_bounds(expected, actual, f"{title}/{name}: Bambu moved explicit instances during import")
                delta = (0.0, 0.0)
                entry["part_positions"] = explicit_rows[title]
                entry["bed_exclude_area"] = machine.get("bed_exclude_area", [])
                entry["placement_check"] = "Each unchanged STL bounding rectangle is inside printable_area, outside bed_exclude_area and disjoint from other parts"
            if title not in reuse_placements and set(group) & set(colour_parts) and title in CENTRE_PLATES:
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
            elif title not in reuse_placements and set(group) & set(colour_parts):
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
            if title in reuse_placements:
                requested = reuse_placements[title]
                delta = tuple(float(requested["min_xy"][axis]) - low[axis] for axis in range(2))
                if set(group) & set(colour_parts):
                    assert "prime_tower_xy" in requested, f"BED_REUSE {title}: explicit prime_tower_xy required"
                    towers[index] = tuple(float(value) for value in requested["prime_tower_xy"])
                    entry["prime_tower_xy"] = list(towers[index])
                entry["reuse_batch"] = reuse_batches[title]
            entry["object_bounds_mm"] = [[round(low[axis] + delta[axis], 4) for axis in range(2)],
                                         [round(high[axis] + delta[axis], 4) for axis in range(2)]]
            assert all(entry["object_bounds_mm"][0][axis] >= 0 and
                       entry["object_bounds_mm"][1][axis] <= (width, depth)[axis]
                       for axis in range(2)), f"Plate {title}: requested placement exceeds the bed"
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
    inherited_density = project_settings["sparse_infill_density"]
    own_infill = sum(row["instances"] for row in object_infill.values()
                     if row["sparse_infill_density"] != inherited_density)
    expected_own = sum(count for _, group in resolved for n, count in group.items()
                       if f"{infill(n, PARTS[n][1], full_build)}%" != inherited_density)
    assert placed == sum(count for _, group in resolved for count in group.values()), f"{target.name} places {placed} parts"
    assert own_infill == expected_own, f"{target.name}: {own_infill} parts with own infill, expected {expected_own}"
    print(f"{target.name}: {placed} parts on {len(plate_ids)} plates, slicing every plate before publishing", flush=True)
    multicolour, pauses, plate_slices, bed_contact = {}, {}, {}, {}
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
        with zipfile.ZipFile(plate_dir / "sliced.3mf") as sliced:
            sliced_settings = json.loads(sliced.read("Metadata/project_settings.config"))
            process_overrides = verify_process_overrides(sliced_settings, process_file)
            sliced_infill = verify_object_infill(sliced_settings, sliced.read("Metadata/model_settings.config"), full_build)
            assert sliced_infill == {name: object_infill[name] | dict(instances=count) for name, count in group.items()}, \
                f"Plate {title}: object infill settings changed during slicing"
            sliced_filaments = verify_object_filaments(sliced.read("Metadata/model_settings.config"), mono)
            assert sliced_filaments == {name: object_filaments[name] for name in group}, \
                f"Plate {title}: filament assignments changed during slicing"
            assert sliced_settings.get("curr_bed_type") == PRINTER["bed"], f"Plate {title}: lost bed type"
            if reuse_config:
                actual_bounds = archive_geometry_bounds(sliced)[:, :2]
                origin = np.array([((index - 1) % columns) * width * 1.2,
                                   -((index - 1) // columns) * depth * 1.2])
                expected_bounds = np.array(layout[index - 1]["object_bounds_mm"])
                assert np.allclose(actual_bounds - origin, expected_bounds, atol=0.01), \
                    f"Plate {title}: sliced objects moved from requested bed-local placement"
                layout[index - 1]["sliced_object_bounds_mm"] = (actual_bounds - origin).round(4).tolist()
                gcode_name = next(n for n in sliced.namelist() if re.fullmatch(r"Metadata/plate_\d+\.gcode", n))
                bed_contact[title] = first_layer_contact(sliced.read(gcode_name).decode(errors="replace"),
                                                        float(reuse_config.get("clearance_mm", 5)))
            if title in explicit_rows:
                origin3 = np.array([((index - 1) % columns) * width * 1.2,
                                    -((index - 1) // columns) * depth * 1.2, 0])
                actual = [b - origin3 for b in archive_geometry_bounds(sliced, per_item=True)]
                assert_instance_bounds([row["bounds_mm"] for row in explicit_rows[title]], actual,
                                       f"{title}: sliced individual objects moved from explicit positions")
        if index - 1 in pause_plates:
            with zipfile.ZipFile(plate_dir / "sliced.3mf") as sliced:
                name = next(n for n in sliced.namelist() if re.fullmatch(r"Metadata/plate_\d+\.gcode", n))
                gcode_text = sliced.read(name).decode(errors="replace")
                actual_settings = json.loads(sliced.read("Metadata/project_settings.config"))
                assert actual_settings["machine_pause_gcode"] == pause_gcode, "Lost insertion-pause printer override"
                assert str(actual_settings["use_relative_e_distances"]) == str(int(relative_e)), "Unexpected extrusion mode"
                found = pause_heights(gcode_text, native_pause_gcode)
            wanted = pause_plates[index - 1]
            # Bambu emits the pause at the layer change: in the layer at the requested height, before it extrudes
            assert [z for z, _ in found] == wanted and not any(e for _, e in found), \
                f"Plate {title}: pauses {found} (layer, extruded before), wanted at the start of {wanted}"
            clearance = verify_pause_lifts(gcode_text, PAUSE_LIFT_MM, float(machine["printable_height"]), relative_e)
            assert not PAUSE_LIFT_MM or [r["layer_mm"] for r in clearance] == wanted, "Missing insertion clearance"
            pauses[title] = dict(plate=index, pause_before_layer_mm=wanted, extra_clearance_mm=PAUSE_LIFT_MM,
                                 clearance_moves=clearance)
            print(f"Slice pause plate {title}: PASS, pause before layer {wanted} mm; {PAUSE_LIFT_MM:g} mm extra clearance", flush=True)
        needed = {slot for name in group for slot in expected_filaments(name, mono).values()}
        assert all(grams.get(slot, 0) > 0 for slot in needed), \
            f"Plate {title}: filament use {grams}, needs {sorted(needed)}"
        plate_slices[title] = dict(plate=index, hours=round(plate.get("total_predication", 0) / 3600, 2),
                                   grams_by_filament=grams, warnings=plate.get("warning_message"),
                                   process_overrides=process_overrides, object_infill=sliced_infill,
                                   expected_filament_slots=sorted(needed), object_filaments=sliced_filaments)
        if not coloured:
            print(f"Slice plate {title}: PASS, filament use {grams} g", flush=True)
            continue
        multicolour[title] = dict(plate=index, hours=round(plate.get("total_predication", 0) / 3600, 2),
                                  grams_by_filament=grams, warnings=plate.get("warning_message"))
        print(f"Slice multicolour plate {title}: PASS, filament use {grams} g", flush=True)
    reuse_report = verify_bed_reuse(reuse_config, bed_contact, machine)
    if reuse_report:
        print(f"Reusable bed: PASS, {len(reuse_report['batches'])} coating batches; disjoint sliced contact footprints", flush=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate, target)
    print(f"Project 3MF published -> {target.relative_to(ROOT)}", flush=True)
    return dict(file=str(target.relative_to(ROOT)), parts=placed, plates=len(plate_ids), layout=layout,
                bed_type=PRINTER["bed"], bed_reuse=reuse_report,
                total_hours_plates=round(sum(s["hours"] for s in plate_slices.values()), 1),
                total_grams_plates=round(sum(sum(s["grams_by_filament"].values()) for s in plate_slices.values()), 1),
                multicolour_parts=COLOR_PARTS, multicolour_slices=multicolour, pause_slices=pauses, plate_slices=plate_slices,
                object_filaments=object_filaments, object_infill=object_infill, own_infill_parts=own_infill, sha256=hashlib.sha256(target.read_bytes()).hexdigest())


def custom_gcode_xml(pause_plates, gcode):
    """Bambu project pauses: Metadata/custom_gcode_per_layer.xml, type 1 = pause print."""
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<custom_gcodes_per_layer>"]
    for index, heights in sorted(pause_plates.items()):
        lines += ["<plate>", f'<plate_info id="{index + 1}"/>']
        lines += [f'<layer top_z="{z:g}" type="1" extruder="1" color="" extra="" gcode={quoteattr(gcode)}/>' for z in heights]
        lines += ['<mode value="MultiAsSingle"/>', "</plate>"]
    return "\n".join(lines + ["</custom_gcodes_per_layer>"]) + "\n"


def pause_heights(gcode_text, pause_gcode):
    """For every pause in sliced G-code: (Z_HEIGHT of the layer it sits in, whether that layer extruded before it)."""
    found, layer, extruded = [], None, False
    e_relative, e_position = False, 0.0
    for line in gcode_text.splitlines():
        line = line.strip()
        if line.startswith("; Z_HEIGHT:"):
            layer, extruded = float(line.split(":")[1]), False
        command = line.split(";", 1)[0].strip()
        if command == pause_gcode and layer is not None:
            found.append((layer, extruded))
        elif command in ("G90", "G91", "M82", "M83"):
            e_relative = command in ("G91", "M83")
        elif re.match(r"(?:G[0123]|G92)\s", command):
            axis = re.search(r"(?:^|\s)E([+-]?\d*\.?\d+)", command)
            if axis:
                value = float(axis[1])
                if command.startswith("G92 "):
                    e_position = value
                else:
                    delta = value if e_relative else value - e_position
                    e_position = e_position + value if e_relative else value
                    extruded = extruded or delta > 1e-8
    return found


def verify_pause_lifts(gcode_text, lift_mm, printable_height, relative_e=True):
    """Check actual pre-pause Z, balanced clearance, modes and the next motion's feed rate.

    The layer marker is not the physical Z: Bambu may postpone the layer move until after
    the pause. This checks emitted commands; native firmware parking is not simulated.
    """
    if not lift_mm:
        return []
    lines = [line.strip() for line in gcode_text.splitlines()]
    expected = insertion_pause_gcode("M400 U1", lift_mm, relative_e).splitlines()
    absolute, e_relative, z, layer, feed = True, None, None, None, None
    active, found = None, []
    for i, line in enumerate(lines):
        if line.startswith("; Z_HEIGHT:"):
            layer = float(line.split(":")[1])
        if line == "; INSERTION_PAUSE_BEGIN":
            assert active is None and z is not None and layer is not None, "Unknown/nested insertion-pause position"
            assert absolute and e_relative == relative_e, "Unexpected pre-pause coordinate or extrusion mode"
            # Bambu may remove a redundant F600 from the return move; check the modal feed below.
            normalize = lambda block: [re.sub(r" F600$", "", item) for item in block]
            assert normalize(lines[i:i + len(expected)]) == normalize(expected), "Altered or incomplete insertion-pause motion block"
            assert 0 <= z and z + lift_mm <= printable_height - 2, \
                f"Insertion pause at actual Z{z:g} + {lift_mm:g} exceeds the {printable_height - 2:g} mm clearance limit; reduce PAUSE_LIFT_MM"
            active = dict(layer_mm=layer, before_z_mm=round(z, 5), paused_z_mm=None, restored_z_mm=None)
        command = line.split(";", 1)[0].strip()
        if command in ("G90", "G91"):
            absolute = command == "G90"
            # Marlin's coordinate commands reset the extrusion override; restore it explicitly.
            e_relative = not absolute
        elif command in ("M82", "M83"):
            e_relative = command == "M83"
        elif re.match(r"(?:G[0123]|G92)\s", command):
            speed = re.search(r"(?:^|\s)F(\d*\.?\d+)", command)
            if speed:
                feed = float(speed[1])
            axis = re.search(r"(?:^|\s)Z(-?\d*\.?\d+)", command)
            if axis:
                if active is not None:
                    assert feed == 600, "Insertion-pause Z movement has the wrong feed rate"
                value = float(axis[1])
                z = value if absolute or command.startswith("G92 ") else (z + value if z is not None else None)
        if command == "M400 U1" and active is not None:
            assert absolute and e_relative == relative_e, "Native pause entered in the wrong mode"
            assert abs(z - active["before_z_mm"] - lift_mm) < 1e-4, "Wrong insertion clearance"
            active["paused_z_mm"] = round(z, 5)
        if line == "; INSERTION_PAUSE_END":
            assert active is not None and active["paused_z_mm"] is not None, "Missing native insertion pause"
            assert absolute and e_relative == relative_e, "Pause failed to restore coordinate/extrusion modes"
            assert abs(z - active["before_z_mm"]) < 1e-4, "Pause failed to restore the original physical Z"
            # The added Z moves use F600. Do not silently change the following print/travel speed.
            for following in lines[i + 1:]:
                following = following.split(";", 1)[0].strip()
                if re.match(r"G[0123]\s", following):
                    assert re.search(r"(?:^|\s)F\d", following), "First post-pause motion must reset the feed rate"
                    break
            else:
                raise AssertionError("No motion after insertion pause")
            active["restored_z_mm"] = round(z, 5)
            found.append(active)
            active = None
    assert active is None, "Unfinished insertion-pause motion block"
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
                       f"{PROCESS['top_shell_layers']}/{PROCESS['bottom_shell_layers']} top/bottom, "
                       f"{'supports enabled' if PROCESS['settings']['enable_support'] == '1' else 'no supports'}; "
                       f"{DEFAULT_INFILL} % {PROCESS['pattern']}, 100 % zig-zag: {', '.join(solid) or 'none'}",
               process_overrides=PROCESS["settings"],
               part_infill=PART_INFILL,
               parts=results, total_parts=sum(r["quantity"] for r in results),
               total_grams_individual_plates=round(sum(r["quantity"] * r["grams"] for r in results), 1),
               total_hours_individual_plates=round(sum(r["quantity"] * r["hours"] for r in results), 1),
               production_gcode=False)
write_summary(summary)
assert all(r["passed"] for r in results), f"Slicing failed; inspect {out}"
assert all(r["wall_loops"] == PROCESS["wall_loops"] for r in results), "Wrong diagnostic wall count"
assert all(r["infill_percent"] == infill(r["part"], r["material"]) for r in results), "Wrong diagnostic infill"
assert all(r["effective_settings"]["sparse_infill_pattern"] == pattern(infill(r["part"], r["material"])) for r in results)
assert all(r["effective_settings"]["enable_support"] == PROCESS["settings"]["enable_support"] for r in results), "Wrong diagnostic support setting"
summary["project_3mf"] = build_project_3mf()
if TEST_PLATES:
    summary["test_3mf"] = build_project_3mf(TEST_PLATES, TEST_3MF, "test-3mf", full_build=False, process_file=profiles / "process-test.json", mono=TEST_FILAMENT)
    summary["test_3mf"]["process"] = {key: TEST_PROCESS[key] for key in ("wall_loops", "top_shell_layers", "bottom_shell_layers", "infill")}
    summary["test_3mf"]["process_overrides"] = TEST_PROCESS["settings"]
write_summary(summary)
test = summary.get("test_3mf")
print(f"PASS: {len(results)} slices; {summary['total_parts']} parts; "
      f"{summary['total_grams_individual_plates']} g; {summary['total_hours_individual_plates']} h; "
      f"project 3MF with {summary['project_3mf']['plates']} plates: {summary['project_3mf']['total_grams_plates']} g; "
      f"{summary['project_3mf']['total_hours_plates']} h as plates"
      + (f"; test 3MF with {test['plates']} plates: {test['total_grams_plates']} g; {test['total_hours_plates']} h" if test else ""))
