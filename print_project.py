"""Project settings for the openscad-print-project tools in scripts/.

Everything project-specific lives here, the scripts stay identical to the skill copies
(python3 ~/.claude/skills/openscad-print-project/scripts/skill_sync.py status).
"""
import math
import numpy as np
import trimesh
import manifold3d as md

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


def corner_jumps(local_meshes, width, depth, top, plan_r=3.5, corner_r=6.0,
                 edge_c=1.2, max_jump=15.0):
    rows = []
    for name, rear in (("head", False), ("head_back", True)):
        mesh = local_meshes[name]
        adj = mesh.face_adjacency
        edges = mesh.vertices[mesh.face_adjacency_edges]
        mid = edges.mean(axis=1)
        length = np.linalg.norm(edges[:, 0] - edges[:, 1], axis=1)
        angle = np.degrees(mesh.face_adjacency_angles)
        normals = mesh.face_normals[adj]
        longest = np.linalg.norm(mesh.triangles - np.roll(mesh.triangles, 1, axis=1), axis=2).max(axis=1)
        altitude = 2 * mesh.area_faces / np.maximum(longest, 1e-20)
        # Micron-thin triangles from CSG intersections have numerically unstable
        # normals even when their area is nonzero. Reject by altitude, not area.
        stable = altitude[adj].min(axis=1) > 0.001
        for right in (False, True):
            x = width - mid[:, 0] if right else mid[:, 0]
            y = depth - mid[:, 1] if rear else mid[:, 1]
            nx = normals[:, :, 0] * (1 if right else -1)
            ny = normals[:, :, 1] * (1 if rear else -1)
            # Deliberate bed-edge chamfer, cavity faces and numerical slivers
            # are outside this regression's scope. Mesh validity stays a
            # separate, mandatory prerequisite in the normal export checks.
            keep = ((x < plan_r) & (y > edge_c + 0.1) & (y < plan_r - 0.05)
                    & (mid[:, 2] > top - corner_r + 0.15)
                    & (mid[:, 2] < top - 0.15)
                    & (length > 0.03) & stable
                    & (nx.min(axis=1) > 0.05)
                    & (ny.min(axis=1) > -0.02)
                    & (normals[:, :, 2].min(axis=1) > -0.02))
            count = int(keep.sum())
            assert count >= 5, f"G2 {name}/{right}: corner ROI has insufficient coverage"
            peak = float(angle[keep].max())
            row = dict(part=name, side="right" if right else "left", edges=count,
                       max_jump_deg=round(peak, 3),
                       over_limit_length_mm=round(float(length[keep & (angle > max_jump)].sum()), 5))
            rows.append(row)
    # Return rows on failure too when using this function as a diagnostic.
    return rows


def magnet_skin(local_head, cylinder, manifold, axes, depth=3.2, radius=5.15):
    solid = manifold(local_head)
    rows = []
    for x, z in axes:
        # 1.21 rather than 1.20 covers the <0.001-mm sag of this 360-sided
        # inscribed probe. Exclude only 0.001 mm at the open pocket end faces.
        outer = cylinder([x, 0.001, z], [0, 1, 0], depth - 0.002, radius + 1.21, 360)
        inner = cylinder([x, 0.001, z], [0, 1, 0], depth - 0.002, radius + 0.01, 360)
        missing = float(((outer - inner) - solid).volume())
        rows.append(dict(axis_xz=[x, z], tested_radial_skin_mm=1.21,
                         missing_mm3=round(missing, 8)))
    return rows


def check_top_corners(ctx):
    """checks(ctx) adapter for installed-position assembly meshes."""
    m = ctx.metrics
    plan_r, corner_r, edge_c, mag_off = (m[k] for k in ("plan_r", "corner_r", "edge_c", "mag_off"))
    width, depth = m["body"]
    top = m["base_h"] + m["head_h"]
    local = {name: head_frame(ctx.meshes[name], m) for name in ("head", "head_back")}
    corners = corner_jumps(local, width, depth, top, plan_r, corner_r, edge_c)
    centre_z = m["base_h"] + m["head_h"] / 2
    axes = [(width / 2 + sx * mag_off, centre_z + sz * mag_off)
            for sx in (-1, 1) for sz in (-1, 1)]
    pockets = magnet_skin(local["head"], ctx.cylinder, ctx.manifold, axes,
                          depth=m["magnet_pocket"][1], radius=m["magnet_pocket"][0] / 2)
    assert all(r["max_jump_deg"] <= 15 for r in corners), f"corner crease: {corners}"
    assert all(r["missing_mm3"] < 1e-5 for r in pockets), f"magnet skin missing: {pockets}"
    return dict(top_corner_normals=corners, magnet_radial_skin=pockets)


def head_frame(mesh, metrics):
    out = mesh.copy()
    v = out.vertices.copy()
    t = math.radians(metrics["tilt"])
    dy, dz = v[:, 1] - metrics["joint_y"], v[:, 2] - metrics["base_h"]
    v[:, 1] = metrics["joint_y"] + math.cos(t) * dy + math.sin(t) * dz
    v[:, 2] = metrics["base_h"] - math.sin(t) * dy + math.cos(t) * dz
    out.vertices = v
    return out


def silhouette_span(mesh, x, z):
    start_y = float(mesh.bounds[0, 1]) - 10
    points, _, _ = mesh.ray.intersects_location([[x, start_y, z]], [[0, 1, 0]], multiple_hits=True)
    assert len(points) >= 2, f"silhouette probe misses mesh at x={x}, z={z}"
    return [float(points[:, 1].min()), float(points[:, 1].max())]


def joint_profile_rows(base_local, head_local, width, joint_z, plan_r=3.5):
    # At 2 mm from the joint both the R0.5 neck and the 1.2-mm rear chamfer
    # are behind us. Compare exported silhouettes; no loft formula is repeated.
    xs = [plan_r / 2, plan_r + 1, width / 2, width - plan_r - 1, width - plan_r / 2]
    rows = []
    for x in xs:
        base = silhouette_span(base_local, x, joint_z - 2)
        head = silhouette_span(head_local, x, joint_z + 2)
        delta = (base[1] - base[0]) - (head[1] - head[0])
        rows.append(dict(x_mm=x, base_front_back_mm=base, head_front_back_mm=head,
                         base_excess_span_mm=round(delta, 5)))
    return rows


def check_joint_profile(ctx):
    m = ctx.metrics
    base = head_frame(ctx.meshes["base"], m)
    head = trimesh.util.concatenate([head_frame(ctx.meshes[n], m) for n in ("head", "head_back")])
    rows = joint_profile_rows(base, head, m["body"][0], m["base_h"], m["plan_r"])
    # The reviewed 8-mm transition retains about 0.20 mm per side 2 mm below
    # the joint. Allow 0.30 mm per side; reject both the old 1.30-mm shoulder
    # and an inward overcut of the upper base. These are design tolerances,
    # not a second evaluation of the SCAD loft function.
    assert all(-0.1 <= r["base_excess_span_mm"] <= 0.6 for r in rows), f"upper-base shoulder: {rows}"
    return dict(upper_base_silhouette=rows)


# These fixed probe routes describe the reviewed layout, not a fluid simulation.
# A moved board or vent must keep the routes attached to the real surfaces and outlets.
def _air_box(lo, hi):
    return md.Manifold.cube([b - a for a, b in zip(lo, hi)]).translate(lo)


def _air_corridor(points, cylinder, radius=0.6):
    chunks = [md.Manifold.sphere(radius, 32).translate(p) for p in points]
    for start, end in zip(points[:-1], points[1:]):
        axis = np.asarray(end, float) - start
        chunks.append(cylinder(start, axis, float(np.linalg.norm(axis)), radius, 48))
    return md.Manifold.batch_boolean(chunks, md.OpType.Add)


def _charger_air_probes(cylinder):
    return {
        'component_face_space': _air_box([57, 54.6, 33.2], [83, 56.6, 42.2]),
        'heatsink_rear_space': _air_box([77.6, 67.7, 31.7], [89.6, 69.5, 43.7]),
        'component_side_route': _air_corridor([[65.5, 59, 60], [65.5, 59, 47], [65.5, 55.5, 45],
                                           [65.5, 55.5, 37], [50, 55.5, 37], [50, 75, 37]], cylinder),
        'heatsink_side_route': _air_corridor([[83.5, 63, 60], [83.5, 63, 47], [83.5, 68.5, 46],
                                          [83.5, 68.5, 37], [85, 68.5, 37], [85, 75, 37]], cylinder),
    }


def _charger_air_report(meshes, solids, cylinder):
    result = {'module_extents_mm': meshes['chg_module'].extents.tolist(), 'probes': {}}
    # This particular board is upright along X/Z, with its thickness and parts
    # along Y. These independent physical dimensions reject the old flat pose.
    extent = meshes['chg_module'].extents
    result['vertical_pose'] = bool(abs(extent[0] - 32.2) < 0.05 and abs(extent[1] - 3.7) < 0.05
                                   and abs(extent[2] - 11) < 0.05)
    module_bounds, sink_bounds = meshes['chg_module'].bounds, meshes['chg_sink'].bounds
    spaces = {'component_face_space': ([57, 54.6, 33.2], [83, 56.6, 42.2]),
              'heatsink_rear_space': ([77.6, 67.7, 31.7], [89.6, 69.5, 43.7])}
    result['face_anchor_gaps_mm'] = {'components': float(module_bounds[0, 1] - 56.6),
                                      'heatsink': float(67.7 - sink_bounds[1, 1])}
    result['fields_inside_face_extents'] = all(
        bounds[0, axis] + 0.05 <= lo[axis] < hi[axis] <= bounds[1, axis] - 0.05
        for bounds, (lo, hi) in [(module_bounds, spaces['component_face_space']),
                                 (sink_bounds, spaces['heatsink_rear_space'])]
        for axis in (0, 2))
    bodies = _charger_air_probes(cylinder)
    for name, probe in bodies.items():
        collisions = {n: round(float((probe ^ s).volume()), 7) for n, s in solids.items()
                      if not n.startswith('driver_')}
        result['probes'][name] = {'volume_mm3': round(probe.volume(), 4),
                                  'collisions_mm3': {n: v for n, v in collisions.items() if v > 0.0001}}
    result['route_connections'] = {}
    for side, space in [('component', 'component_face_space'), ('heatsink', 'heatsink_rear_space')]:
        route = bodies[side + '_side_route']
        result['route_connections'][side] = dict(components=len(route.decompose()),
            face_space_overlap_mm3=round(float((route ^ bodies[space]).volume()), 5),
            probe_diameter_mm=1.2)
    return result


def check_charger_air(ctx):
    result = _charger_air_report(ctx.meshes, ctx.solids, ctx.cylinder)
    assert result['vertical_pose'], f"Charge board is not upright: {result['module_extents_mm']}"
    assert result['fields_inside_face_extents'], 'Air probe fields do not cover the board faces'
    assert all(0.05 <= gap <= 0.5 for gap in result['face_anchor_gaps_mm'].values()), \
        f"Air probe fields detached from board faces: {result['face_anchor_gaps_mm']}"
    assert all(not item['collisions_mm3'] for item in result['probes'].values()), \
        f"Charge-module air corridor blocked: {result['probes']}"
    assert all(q['components'] == 1 and q['face_space_overlap_mm3'] > 1
               for q in result['route_connections'].values()), 'Disconnected charge-module air corridor'
    return dict(charger_air_access=result)



def check_rim_chamfers(ctx):
    """Measure real end profiles, including the four formerly truncated cassette sides."""
    m = ctx.metrics
    width, depth = m["body"]
    bottom, top = m["base_h"], m["base_h"] + m["head_h"]
    local = {n: head_frame(ctx.meshes[n], m) for n in ("head", "head_back", "cassette")}
    rows = []
    for d in (0.1, 0.6, 1.1, 1.3):
        edge, cass = max(0, m["edge_c"] - d), max(0, m["cass_c"] - d)
        cy = -m["cass_t"] + d
        # (part, profile, mesh, ray origin, ray axis, expected outer limits)
        cases = [
            ("base", "left/right", ctx.meshes["base"], [-1, depth / 2, d], 0, [edge, width - edge]),
            ("base", "front/back", ctx.meshes["base"], [width / 2, -1, d], 1, [edge, depth - edge]),
            ("cassette", "left/right", local["cassette"], [-1, cy, (bottom + top) / 2], 0,
             [m["plan_r"] + cass, width - m["plan_r"] - cass]),
            ("cassette", "bottom/top", local["cassette"], [width / 2, cy, 0], 2,
             [bottom + m["cass_inset"] + cass, top - m["cass_inset"] - cass]),
            ("head", "bottom/top", local["head"], [width / 2, d, 0], 2, [bottom + edge, top - edge]),
            ("head_back", "bottom/top", local["head_back"], [width / 2, depth - d, 0], 2,
             [bottom + m["cover_gap"] + edge, top - edge]),
        ]
        for name, profile, mesh, origin, axis, expected in cases:
            direction = np.eye(3)[axis]
            hits, _, _ = mesh.ray.intersects_location([origin], [direction], multiple_hits=True)
            assert len(hits) >= 2, f"Chamfer probe misses {name}/{profile} at depth {d}"
            measured = [float(hits[:, axis].min()), float(hits[:, axis].max())]
            error = float(np.max(np.abs(np.asarray(measured) - expected)))
            assert error < 0.03, f"Incorrect rim chamfer {name}/{profile} at depth {d}: {measured} vs {expected}"
            rows.append(dict(part=name, profile=profile, depth_mm=d,
                             limits_mm=[round(x, 4) for x in measured], max_error_mm=round(error, 5)))
    return dict(rim_chamfer_profiles=rows)


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
        ("chg_module", "ball_lid", [0, 0, -1]),       # upright board rests on two narrow PCB-edge seats
        ("ball_lid", "base", [0, 0, -1]),             # lid on its posts and walls
    ])
    # Stops: the fan cannot move sideways in its corner guides, the head is located by its screws
    # There is no register between head and base: the four screws locate it, so that is what is checked
    # usbc_in: pushing a cable into the socket must not push the board into the bay
    stops = ctx.stops([("fan_sideways", "fan", "head", [1, 0, 0], 1.5),
                       ("usbc_in", "usbc", "base", [0, -1, 0], 0.6),
                       ("head_on_screws", "head", "screws_head", [1, 0, 0], 0.6),
                       ("charger_forward", "chg_module", "ball_lid", [0, -1, 0], 0.4),
                       ("charger_backward", "chg_module", "ball_lid", [0, 1, 0], 0.4)])
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
        # Remove the head first, then lift board and heatsink out of the open-top guides.
        ("chg_off", ["chg_module", "chg_sink"],
         ["base", "ball_lid", "battery", "pwm_board", "usbc", "switch", "led", "pot", "screws_lid"],
         [0, 0, 1], 30, 0.5),
        # Remove the head, battery and lid screws before lifting the loaded lid.
        # 10 mm up: clear of the trough walls, its posts, the USB-C channel above it and the run-outs of
        # the rear head screw bosses. Out of the bay it comes at an angle, past the switch well box on the
        # right - a tilt, which a rigid axis-aligned path cannot express.
        ("lid_off", ["ball_lid", "chg_module", "chg_sink"],
         ["base", "ballast", "pwm_board", "usbc", "switch"], [0, 0, 1], 10, 0.5),
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
                tip_angle_deg=round(tip_angle, 1), **check_top_corners(ctx), **check_joint_profile(ctx),
                **check_rim_chamfers(ctx), **check_charger_air(ctx))


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
         "03_back": ("assembly();", "60,320,150,0,0,205"),
         "04_charger_front": ("color(\"#8a9096\") ball_lid(); color(\"#2f5d3a\") chg_module_env(); "
                              "color(\"#aeb5bb\") chg_sink_env();", "110,-90,90,70,60,34"),
         "05_charger_back": ("color(\"#8a9096\") ball_lid(); color(\"#2f5d3a\") chg_module_env(); "
                             "color(\"#aeb5bb\") chg_sink_env();", "110,180,90,70,60,34")}
