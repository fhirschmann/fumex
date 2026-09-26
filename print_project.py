"""Project settings for the openscad-print-project tools in scripts/.

Everything project-specific lives here, the scripts stay identical to the skill copies
(python3 ~/.claude/skills/openscad-print-project/scripts/skill_sync.py status).
"""
import math

SOURCE = "fumex.scad"
METRICS_TAG = "PROJECT_METRICS"       # part="metrics" echoes this tag with [key, value] pairs

# Print parts: name -> (quantity in the full build, material, body count). Quantity 0 = optional test print.
# Must match the part branches in SOURCE exactly (checked). One material key per colour, same keys in FILAMENTS.
PARTS = {
    "base": (1, "PETG-black", 1),
    "head": (1, "PETG-black", 1),
    "head_back": (1, "PETG-black", 1),
    "cassette": (1, "PETG-grey", 1),
    "knob": (1, "PETG-grey", 1),
    "foot": (4, "TPU", 1),
    "ball_lid": (1, "PETG-black", 1),
}
FULL_INFILL = set()
FULL_INFILL_MATERIALS = {"TPU"}

# Assembly bodies in installed position: name -> OpenSCAD call. Every pair is checked for overlap.
ASSEMBLY = {
    "base": "base();",
    "head": "head();",
    "head_back": "head_back();",
    "cassette": "cassette();",
    "knob": "knob();",
    "feet": "place_feet();",
    "ball_lid": "ball_lid();",
    "fan": "fan_env();",
    "filter": "filter_env();",
    "magnets": "magnets_env();",
    "battery": "battery_env();",
    "pwm_board": "pwm_board_env();",
    "pot": "pot_env(nut = false);",
    "pot_nut": "pot_nut_env();",
    "chg_module": "chg_module_env();",
    "chg_sink": "chg_sink_env();",
    "usbc": "usbc_env();",
    "switch": "sw_env();",
    "led": "led_env();",
    "ballast": "ballast_env();",
    "screws_fan": "screws_fan();",
    "screws_back": "screws_back();",
    "screws_head": "screws_head();",
    "screws_lid": "screws_lid();",
    "screws_feet": "screws_feet();",
    # A bit and its holder on every screw head. These must not touch anything, which is the whole check.
    "driver_fan": "drivers_fan();",
    "driver_back": "drivers_back();",
    "driver_head": "drivers_head();",
    "driver_feet": "drivers_feet();",
    "driver_lid": "drivers_lid();",
}
# the fan and the pot are solid envelopes, their screws and shaft run through them
ALLOWED_OVERLAPS = [("fan", "screws_fan"),      # screws run through the holes of the solid fan envelope
                    ("knob", "pot"),           # the slotted sleeve is a press fit on the knurled shaft
                    # The drivers are checked against the state of the build at the moment that screw is
                    # driven, not against the finished assembly: the head screws go in through the open
                    # back before the cover, and the ballast lid is closed before the head goes on at all.
                    ("head_back", "driver_head"), ("head_back", "driver_lid"), ("head", "driver_lid"),
                    ("driver_fan", "driver_head"), ("driver_head", "driver_lid"),
                    # and the fan is screwed to the cover on the bench, where its front face is reachable,
                    # before either of them goes into the head
                    ("head", "driver_fan"), ("cassette", "driver_fan"), ("filter", "driver_fan"),
                    ("screws_back", "driver_lid"), ("driver_back", "driver_lid"),
                    # the lid screws form their own thread: the shank is wider than the core hole, and that
                    # hole is a void in the base, so the trough envelope contains it
                    ("base", "screws_lid"), ("ballast", "screws_lid")]

# Multicolour: part -> inlay names. Black and grey are whole parts here, no inlays and no prime tower.
COLOR_PARTS = {}
STL_DIR, COLOR_DIR, ASM_DIR, REPORT = "stl", "stl/multicolour", "asm", "docs/verification.json"

PRINTER = dict(machine="Bambu Lab H2S 0.4 nozzle", process="0.20mm Standard @BBL H2S",
               bed="Textured PEI Plate", envelope_mm=(340, 320, 340))
PROCESS = dict(wall_loops=4, top_shell_layers=5, bottom_shell_layers=5, infill=20, pattern="gyroid")
FILAMENTS = [dict(material="PETG-black", profile="Generic PETG @BBL H2S", colour="#1A1B1D"),
             dict(material="PETG-grey", profile="Generic PETG @BBL H2S", colour="#8C9196"),
             dict(material="TPU", profile="Generic TPU @BBL H2S", colour="#1A1B1D")]
PLATES = [("Head", ["head", "ball_lid"]),
          ("Base and back cover", ["base", "head_back"]),
          ("Grey parts", ["cassette", "knob"]),
          ("TPU feet", ["foot"])]
PROJECT_3MF = "stl/fumex_all_parts.3mf"
SLICER_SUMMARY = "docs/slicer-summary.json"

# Masses used only for the tipping check: printed parts from their mesh volume, bought parts measured
# or from the data sheet. The effective print density covers walls plus 20 % gyroid.
# g/mm3; the ballast is iron offcuts potted in epoxy, about 60 % metal by volume
# loose iron offcuts under a lid, roughly 60 % of the volume actually metal
MAT = (120, 120, 17)      # the mat the user cut from a cooker hood filter
DENSITY = {"PETG": 0.90e-3, "TPU": 1.20e-3, "iron-loose": 4.7e-3}
MASSES_G = {"fan": 185, "battery": 150, "filter": 15, "pwm_board": 12, "chg_module": 3, "chg_sink": 5,
            "usbc": 2, "switch": 5, "led": 0.3, "magnets": 18, "pot": 6, "pot_nut": 2,
            "screws_fan": 6, "screws_back": 4, "screws_head": 3, "screws_feet": 3, "screws_lid": 3}
# bodies whose mass comes from their volume rather than a data sheet
BY_VOLUME = {"base": "PETG", "head": "PETG", "head_back": "PETG", "cassette": "PETG", "knob": "PETG",
             "feet": "TPU", "ball_lid": "PETG", "ballast": "iron-loose"}

LIMITATIONS = ["Hardware envelopes, not detailed vendor CAD",
               "Sampled motion, no continuous swept-volume proof",
               "No flexible deformation, physical fit, strength or thermal validation",
               "Tipping margin uses estimated part masses and the static centre of mass only",
               "Filter pressure drop and capture distance are not modelled",
               "The mat is compressible: it is pressed in and pulled out past the intake lip, which a\n                rigid-body path check cannot show"]


def checks(ctx):
    """Project-specific checks after export."""
    m = ctx.metrics
    assert m["wall"] >= 1.2, "Walls below three perimeters"
    assert m["fan_thread"] >= 5, "Fan screws bite less than 5 mm"
    assert m["head_thread"] >= 5, "Head screws bite less than 5 mm"
    assert m["fan_post"][1] >= m["insert_depth"] + 1, "Fan posts too short for their inserts"
    assert m["knob_top_z"] + 2 <= m["front_rim_z"], "Knob reaches over the front rim"
    # Standard figures, independent of the model: 120 mm fans have a 105 mm hole pitch, the mat is 120 mm
    assert m["fan_axis_pitch"] == 105, "120 mm fans have a 105 mm mounting hole pitch"
    assert m["open_sq"] < 120, "The intake lip must overlap the 120 mm mat"
    assert m["chamber"][0] >= 120 and m["chamber"][1] >= 17, "Filter chamber smaller than the mat"
    assert m["opening_sq"] >= 113, "Air passage narrower than the swept blade diameter"
    assert m["fan_post"][0] / 2 >= m["insert_hole_d"] / 2 + m["insert_w_min"], \
        "Fan posts too thin around their inserts"
    assert m["magnet_pocket"] == [10.3, 3.2], "Magnet pockets no longer fit a 10 x 3 disc"

    # Contact, not just freedom from overlap
    tilt = math.radians(m["tilt"])
    into = [0, math.cos(tilt), math.sin(tilt)]        # into the intake face, normal to it
    contacts = ctx.contacts([
        ("head", "base", [0, 0, -1]),                 # head floor on the base rim
        ("cassette", "head", into),                   # cassette flange flat on the intake face
        ("fan", "head", [-i for i in into]),          # fan frame on the end face of the filter tube
        ("fan", "head_back", into),                   # and on the spacer posts of the cover
        ("feet", "base", [0, 0, 1]),
        ("pwm_board", "base", [0, 0, -1]),            # board on the rib pads
        ("chg_module", "ball_lid", [0, 0, -1]),       # board down in its tray on the ballast lid
        ("ball_lid", "base", [0, 0, -1]),             # lid on its posts and walls
    ])
    # Stops: the fan cannot move sideways in its corner guides, the head is located by its screws
    # There is no register between head and base: the four screws locate it, so that is what is checked
    # usbc_in: pushing a cable into the socket must not push the board into the bay
    stops = ctx.stops([("fan_sideways", "fan", "head", [1, 0, 0], 1.5),
                       ("usbc_in", "usbc", "base", [0, -1, 0], 0.6),
                       ("head_on_screws", "head", "screws_head", [1, 0, 0], 0.6)])
    # The cell is held in open saddles by foam tape, so it has clearance instead of contact
    # 0.2 for the heatsink: nominal 0.3 in its wall cut-out, less the facets of the rounded corners
    gaps = ctx.clearances([("battery", "base", 0.3), ("battery", "head", 1.0),
                           ("chg_sink", "fan", 1.5)])
    # Assembly paths, not only end positions. The head is pulled off along the tilted normal.
    up = [0, -math.sin(tilt), math.cos(tilt)]
    out = [0, -math.cos(tilt), -math.sin(tilt)]       # out of the intake face, normal to it
    paths = ctx.paths([
        ("cassette_off", "cassette", ["head", "base", "fan", "filter"], out, 30, 0.5),
        # the fan is bolted to the cover, so it comes off with it
        ("cover_off", ["head_back", "fan", "screws_fan"], ["head", "base", "chg_module", "chg_sink"],
         [-o for o in out], 30, 0.5),
        # the board lifts out of its grooves once the cover is off; it has to, because it stands in the
        # way of the fan
        ("chg_off", ["chg_module", "chg_sink"], ["base", "ball_lid", "battery", "pwm_board"], [0, 0, 1], 30, 0.5),
        # the rear head screw bosses hang over the trough, so the lid slides forward first; the cell
        # is out by then anyway
        # 10 mm up: clear of the trough walls, its posts, the USB-C channel above it and the run-outs of
        # the rear head screw bosses. Out of the bay it comes at an angle, past the switch well box on the
        # right - a tilt, which a rigid axis-aligned path cannot express.
        ("lid_off", "ball_lid", ["base", "ballast", "pwm_board", "usbc", "switch"], [0, 0, 1], 10, 0.5),
        ("fan_out", ["fan", "screws_fan"], ["head", "base"], [-o for o in out], 40, 0.5),   # cover off first
        ("head_off", ["head", "head_back", "cassette", "fan", "filter", "magnets"],
         ["base", "battery", "pwm_board", "usbc", "switch", "pot", "led", "ball_lid", "ballast",
          "chg_module", "chg_sink"], up, 60, 1),
        ("battery_out", "battery", ["base", "pwm_board", "usbc", "switch", "ball_lid"], [0, 0, 1], 40, 0.5),
        ("knob_off", "knob", ["base", "pot_nut"], [0, -1, 0], 20, 0.5),
    ])
    # Heat-set insert pockets: core open, datasheet wall and floor ring material. Everything in the head
    # is pressed in along its own axis, so the probes use the tilted frame.
    d, depth, w = m["insert_hole_d"], m["insert_depth"], m["insert_w_min"]
    back = [-o for o in out]
    probes = ctx.insert_probes(
        [("head_back", _tilt(m, [p[0], m["head_y"][3], p[1]]), back, depth, d, w) for p in m["fan_holes"]] +
        [("head", _tilt(m, [p[0], m["back_y"], p[1]]), out, depth, d, w) for p in m["head_bosses"]] +
        [("base", _tilt(m, [p[0], p[1], m["base_h"]]), [-u for u in up], depth, d, w) for p in m["rim_screws"]] +
        [("base", [p[0], p[1], 0], [0, 0, 1], depth, d, w) for p in _foot_xy(m)])
    # Air must not bypass the mat: the chamber lip overlaps it on every side, front and back
    lip = (m["chamber"][0] - m["open_sq"]) / 2
    assert lip >= 2, f"Intake lip only {lip:.2f} mm wide"
    # And the mat must not travel back into the fan. The rear lip closes the bore from the chamber to
    # open_sq along a ramp, so a 120 mm mat is caught where the bore first drops below 120.
    y0, y1 = m["mat_stop"]
    mat_free = y0 + (m["chamber"][0] - MAT[0]) / (2 * lip) * (y1 - y0) - (m["head_y"][0] + MAT[2])
    fan_gap = m["head_y"][2] - (m["head_y"][0] + MAT[2])
    assert 0 < mat_free < 0.25 * fan_gap, f"Mat travels {mat_free:.1f} mm of the {fan_gap:.1f} mm to the fan"
    # The corner gussets press into the fleece. Bound how much of the mat that is.
    squashed = (ctx.solids["filter"] ^ ctx.solids["head"]).volume()
    mat = MAT[0] * MAT[1] * MAT[2]
    assert squashed < 0.05 * mat, f"Gussets displace {squashed / mat:.1%} of the mat"

    # Tipping: the head leans forward, so the centre of mass must stay well inside the foot polygon
    total, moment = 0.0, [0.0, 0.0, 0.0]
    for name, mesh in ctx.meshes.items():
        grams = (mesh.volume * DENSITY[BY_VOLUME[name]] if name in BY_VOLUME else MASSES_G.get(name, 0.0))
        total += grams
        moment = [moment[i] + grams * mesh.center_mass[i] for i in range(3)]
    com = [moment[i] / total for i in range(3)]
    # The pads are chamfered at the bottom, so the undeformed contact patch is foot_chamfer smaller all
    # round than the pad outline - and the floor is at -foot height, not at z = 0. Both were missing, which
    # flattered the tip angle by about two degrees (audit 2026-09-23, S1).
    fx, fy = m["foot_x"], m["foot_y"]
    c = m["foot_chamfer"]
    pad = [m["foot_size"][0] / 2 - c, m["foot_size"][1] / 2 - c]
    poly = [fx[0] - pad[0], fx[1] + pad[0], fy[0] - pad[1], fy[1] + pad[1]]
    margins = dict(front=com[1] - poly[2], back=poly[3] - com[1], left=com[0] - poly[0], right=poly[1] - com[0])
    assert min(margins.values()) >= 15, f"Centre of mass too close to a foot edge: {margins}"
    tip_angle = math.degrees(math.atan(min(margins.values()) / (com[2] + m["foot_size"][2])))
    ctx.summary.append(f"{len(paths)} paths, tips at {tip_angle:.1f} degrees")
    ctx.open_items.append("Masses of the bought parts are data-sheet or estimated values, not weighed")
    return dict(contact_volumes_mm3=contacts, stops=stops, clearances_mm=gaps, sampled_paths=paths, insert_probes=probes,
                intake_lip_mm=lip, mat_free_travel_mm=round(mat_free, 2), mat_squashed_percent=round(100 * squashed / mat, 2), mass_g=round(total, 1),
                centre_of_mass_mm=[round(c, 1) for c in com],
                foot_polygon_mm=poly, tip_margins_mm={k: round(v, 1) for k, v in margins.items()},
                tip_angle_deg=round(tip_angle, 1))


def _tilt(m, point):
    """A point of the untilted head frame in installed coordinates."""
    t = math.radians(m["tilt"])
    y, z = point[1] - m["joint_y"], point[2] - m["base_h"]
    return [point[0], m["joint_y"] + y * math.cos(t) - z * math.sin(t),
            m["base_h"] + y * math.sin(t) + z * math.cos(t)]


def _foot_xy(m):
    return [[x, y] for y in m["foot_y"] for x in m["foot_x"]]


VIEWER = dict(
    title="FUMEX", page_title="FUMEX solder fume extractor", eyebrow="Assembly · installed position",
    dims=[("Width", "145"), ("Depth", "112"), ("Height", "201")],
    # Viewer greys, not the filament colours: black PETG has no shading contrast on screen and the
    # geometry disappears (user, 2026-09-22). The plate and filament names keep the real colours.
    groups=[("black", "Printed · PETG black"), ("grey", "Printed · PETG grey"),
            ("tpu", "Printed · TPU"), ("bought", "Bought parts")],
    hidden_groups=["bought"],
    outer=["head", "head_back", "base", "cassette"],
    cut=["head", "base"],
    # id, label, group, colour, quantity, explode direction (mm per slider mm)
    parts=[("base", "Base", "black", "#8a9096", "1x", [0, 0, 0]),
           ("head", "Head", "black", "#8a9096", "1x", [0, -0.36, 1.35]),
           ("head_back", "Back cover", "black", "#7c8288", "1x", [0, 2.3, 0.6]),
           ("cassette", "Filter cassette", "grey", "#c4c9ce", "1x", [0, -1.55, 1.0]),
           ("knob", "Speed knob", "grey", "#c4c9ce", "1x", [0, -0.6, 0]),
           ("feet", "Feet", "tpu", "#55595e", "4x", [0, 0, -0.6]),
           ("fan_visual", "Fan 120 x 25", "bought", "#6a6f75", "1x", [0, 0.5, 1.35]),
           ("filter", "Filter mat 120 x 120 x 17", "bought", "#a09488", "1x", [0, -0.9, 1.1]),
           ("battery", "LiFePO4 3.2 V 6 Ah", "bought", "#4a6d3f", "1x", [0, 0, -0.2]),
           ("pwm_board", "PWM controller", "bought", "#2f5d3a", "1x", [0, -0.2, 0]),
           ("chg_module", "Charge / boost module", "bought", "#2f5d3a", "1x", [0, 0, 0.3]),
           ("chg_sink", "Heatsink", "bought", "#9aa0a6", "1x", [0, 0, 0.3]),
           ("usbc", "USB-C PD trigger", "bought", "#2f5d3a", "1x", [0, 0.8, 0]),
           ("switch", "Rocker switch", "bought", "#3a3d42", "1x", [0.8, 0, 0]),
           ("magnets", "Magnets 10 x 3", "bought", "#9aa0a6", "8x", [0, -1.2, 0.9]),
           ("screws_fan", "Screws M3 x 30", "bought", "#9aa0a6", "4x", [0, 0.9, 1.35]),
           ("screws_back", "Screws M3 x 8", "bought", "#9aa0a6", "4x", [0, 2.8, 0.6]),
           ("screws_head", "Screws M3 x 8", "bought", "#9aa0a6", "2x", [0, -0.3, 1.6]),
           ("screws_feet", "Screws M3 x 8", "bought", "#9aa0a6", "4x", [0, 0, -1.0]),
           ("ballast", "Ballast, loose iron", "bought", "#6b6f74", "1x", [0, 0, -0.3]),
           ("ball_lid", "Ballast lid", "black", "#7c8288", "1x", [0, 0, 0.8]),
],
    bodies={"fan_visual": "fan_visual();"},
    output="build/viewer.html",
)

VIEWS = {"01_assembly": ("assembly();", "60,-320,150,0,0,25"),
         "02_exploded": ("assembly(18);", "60,-360,170,0,0,30"),
         "03_back": ("assembly();", "60,320,150,0,0,205")}
