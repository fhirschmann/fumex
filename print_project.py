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
    "filter_support": (1, "PETG-black", 1),
    "usbc_fit_base": (0, "PETG-black", 1),
    "usbc_fit_lid": (0, "PETG-black", 1),
}
FULL_INFILL = {"filter_support"}
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
    "filter_support": "filter_support();",
    "magnets": "magnets_env();",
    "battery": "battery_env();",
    "pwm_board": "pwm_board_env();",
    "pot": "pot_env();",
    "chg_module": "chg_module_env();",
    "chg_sink": "chg_sink_env();",
    "chg_tie": "chg_tie_env();",
    "usbc": "usbc_env();",
    "switch": "sw_env();",
    "led": "led_env();",
    "ballast": "ballast_env();",
    "screws_fan": "screws_fan();",
    "screws_back": "screws_back();",
    "screws_head": "screws_head();",
    "screws_lid": "screws_lid();",
    "screws_feet": "screws_feet();",
    "screws_pwm": "screws_pwm();",
    # A bit and its holder on every screw head. These must not touch anything, which is the whole check.
    "driver_fan": "drivers_fan();",
    "driver_back": "drivers_back();",
    "driver_head": "drivers_head();",
    "driver_feet": "drivers_feet();",
    "driver_lid": "drivers_lid();",
    "driver_pwm": "drivers_pwm();",
}
# the fan and the pot are solid envelopes, their screws and shaft run through them
ALLOWED_OVERLAPS = [("base", "screws_pwm"),     # thread forms into the pilot; independently bounded by check_pwm_mount
                    # PCB is fastened before the head, filter and cover assembly is installed.
                    ("head", "driver_pwm"), ("filter", "driver_pwm"), ("cassette", "driver_pwm"),
                    ("filter_support", "driver_pwm"), ("fan", "driver_pwm"),
                    ("driver_fan", "driver_pwm"), ("driver_back", "driver_pwm"),
                    ("fan", "screws_fan"),      # screws run through the holes of the solid fan envelope
                    ("knob", "pot"),           # the slotted sleeve is a press fit on the knurled shaft
                    # The drivers are checked against the state of the build at the moment that screw is
                    # driven, not against the finished assembly: the head screws go in through the open
                    # back before the cover, and the ballast lid is closed before the head goes on at all.
                    ("head_back", "driver_head"), ("head_back", "driver_lid"), ("head", "driver_lid"),
                    ("driver_fan", "driver_head"), ("driver_head", "driver_lid"),
                    # and the fan is screwed to the cover on the bench, where its front face is reachable,
                    # before either of them goes into the head
                    ("head", "driver_fan"), ("cassette", "driver_fan"), ("filter", "driver_fan"),
                    ("screws_back", "driver_lid"), ("driver_back", "driver_lid")]

# Multicolour: part -> inlay names. Black and grey are whole parts here, no inlays and no prime tower.
COLOR_PARTS = {}
STL_DIR, COLOR_DIR, ASM_DIR, REPORT = "stl", "stl/multicolour", "asm", "docs/verification.json"

PRINTER = dict(machine="Bambu Lab H2S 0.4 nozzle", process="0.20mm Standard @BBL H2S",
               bed="Textured PEI Plate", envelope_mm=(340, 320, 340))
PROCESS = dict(wall_loops=4, top_shell_layers=5, bottom_shell_layers=5, infill=20, pattern="gyroid")
FILAMENTS = [dict(material="PETG-black", profile="Generic PETG @BBL H2S", colour="#1A1B1D"),
             dict(material="PETG-grey", profile="Generic PETG @BBL H2S", colour="#8C9196"),
             dict(material="TPU", profile="Generic TPU @BBL H2S", colour="#1A1B1D")]
PLATES = [("Head", ["head", "ball_lid", "filter_support"]),
          ("Base and back cover", ["base", "head_back"]),
          ("Grey parts", ["cassette", "knob"]),
          ("TPU feet", ["foot"])]
PROJECT_3MF = "stl/fumex_all_parts.3mf"
TEST_PLATES = [("USB insertion fit", ["usbc_fit_base", "usbc_fit_lid"])]
TEST_3MF = "stl/fumex_usb_fit.3mf"
TEST_FILAMENT = 1
SLICER_SUMMARY = "docs/slicer-summary.json"

# Masses used only for the tipping check: printed parts from their mesh volume, bought parts measured
# or from the data sheet. The effective PETG density covers walls plus 20 % gyroid;
# the solid filter cross uses the PETG density from the Bambu filament profile.
# g/mm3; the ballast is iron offcuts potted in epoxy, about 60 % metal by volume
# loose iron offcuts under a lid, roughly 60 % of the volume actually metal
MAT = (120, 120, 17)      # the mat the user cut from a cooker hood filter
DENSITY = {"PETG": 0.90e-3, "PETG-solid": 1.27e-3, "TPU": 1.20e-3, "nylon": 1.14e-3, "iron-loose": 4.7e-3}
MASSES_G = {"fan": 185, "battery": 150, "filter": 15, "pwm_board": 12, "chg_module": 3, "chg_sink": 5,
            "usbc": 2, "switch": 5, "led": 0.6, "magnets": 18, "pot": 6, "screws_pwm": 0.7,
            "screws_fan": 6, "screws_back": 4, "screws_head": 6, "screws_feet": 3, "screws_lid": 1.5}
# bodies whose mass comes from their volume rather than a data sheet
BY_VOLUME = {"base": "PETG", "head": "PETG", "head_back": "PETG", "cassette": "PETG", "knob": "PETG",
             "feet": "TPU", "ball_lid": "PETG", "filter_support": "PETG-solid", "ballast": "iron-loose",
             "chg_tie": "nylon"}

LIMITATIONS = ["Hardware envelopes, not detailed vendor CAD",
               "Service motions are sampled; only the USB-to-base translation has a continuous swept-volume check",
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
        # The tie occupies the cool end. The warm component face remains exposed.
        'component_face_space': _air_box([70, 54.6, 33.2], [83, 56.6, 42.2]),
        'heatsink_rear_space': _air_box([77.6, 67.7, 31.7], [89.6, 69.5, 43.7]),
        'component_side_route': _air_corridor([[74.5, 59, 60], [74.5, 59, 47], [74.5, 55.5, 45],
                                           [74.5, 55.5, 37], [74.5, 54.5, 37], [50, 54.5, 37],
                                           [50, 75, 37]], cylinder),
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
    spaces = {'component_face_space': ([70, 54.6, 33.2], [83, 56.6, 42.2]),
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


def check_charger_holder(ctx):
    """Measure the cool-end seats, open hot end and usable tie passages on the meshes."""
    lid, module, tie = (ctx.solids[n] for n in ("ball_lid", "chg_module", "chg_tie"))
    pcb = ctx.meshes["chg_module"].bounds
    x0, z0 = pcb[0, 0], pcb[0, 2]
    yback = pcb[1, 1]
    top_lid = ctx.metrics["ballast"][3] + ctx.metrics["lid_screw"][0]
    holder = lid ^ _air_box([0, 0, top_lid + 0.01], [150, 80, 80])
    assert holder.volume() > 100, "Charge-module holder is missing"
    hot = _air_box([x0 + 21.8, 50, top_lid + 0.01], [95, 72, 46])
    hot_overlap = (holder ^ hot).volume()
    sink_gap = holder.min_gap(ctx.solids["chg_sink"], 6)
    assert hot_overlap < 0.01 and sink_gap >= 4.6, \
        f"Charge-module holder obstructs its hot end: {hot_overlap:.4f} mm3, gap {sink_gap:.3f} mm"

    # Separate physical seats; a contact at one end cannot stand in for the others.
    contacts = {}
    for name, delta, region in [
        ("lower_edge", [0, 0, -0.05], ([x0 + 2.9, 59, z0 - 0.1], [x0 + 11.1, 61, z0 + 0.1])),
        ("rear_bearing", [0, 0.05, 0], ([x0 + 8.9, yback - 0.1, z0 + 3.4],
                                      [x0 + 18.1, yback + 0.1, z0 + 7.6])),
        ("out_end", [-0.05, 0, 0], ([x0 - 0.1, 59.4, z0 + 3.4], [x0 + 0.1, 60.6, z0 + 7.6])),
    ]:
        volume = (module.translate(delta) ^ lid ^ _air_box(*region)).volume()
        assert volume > 0.1, f"Charge-module seat missing: {name}, {volume:.4f} mm3"
        contacts[name] = round(volume, 5)

    # Probe a slightly inset copy of each tunnel to avoid coplanar facet noise.
    # These are spaces in the printed lid; the separate band collision check
    # below proves that the installed tie fits with the board in place as well.
    tunnels = {
        "under_board": _air_box([64.87, 55.02, 30.72], [67.93, 68.38, 32.48]),
        "rear_vertical": _air_box([64.87, 64.02, 30.72], [67.93, 65.78, 44.68]),
    }
    overlaps = {n: round((probe ^ lid).volume(), 6) for n, probe in tunnels.items()}
    assert all(v < 0.01 for v in overlaps.values()), f"Charge tie tunnel blocked: {overlaps}"
    assert (tunnels["under_board"] ^ tunnels["rear_vertical"]).volume() > 1, "Disconnected tie passages"
    bounds = np.asarray(tie.bounding_box()).reshape(2, 3)
    assert abs(bounds[:, 0].mean() - x0 - 12.5) < 0.05, "Charge tie moved off the reviewed cool-end position"
    assert abs(bounds[1, 0] - bounds[0, 0] - 2.5) < 0.05, "Charge tie has the wrong width"
    assert bounds[0, 2] < z0 - 1.1 and bounds[1, 2] > pcb[1, 2] + 1.1, "Charge tie does not wrap the board"
    assert len(tie.decompose()) == 1, "Charge tie band is disconnected"
    collision = {n: round((tie ^ s).volume(), 6) for n, s in ctx.solids.items()
                 if n != "chg_tie" and not n.startswith("driver_")}
    assert not any(v > 0.01 for v in collision.values()), f"Charge tie intersects the assembly: {collision}"
    forward = (module.translate([0, -0.05, 0]) ^ tie).volume()
    assert forward > 0.1, "Charge tie does not retain the board against its rear bearing"
    tie_gap = tie.min_gap(lid, 1)
    assert 0.25 <= tie_gap <= 0.35, f"Charge tie tunnel clearance is {tie_gap:.3f} mm"
    return dict(charger_holder=dict(hot_zone_overlap_mm3=round(hot_overlap, 5),
        holder_to_sink_mm=round(sink_gap, 3), seat_contact_mm3=contacts,
        tunnel_overlap_mm3=overlaps, tie_to_lid_mm=round(tie_gap, 3),
        tie_forward_contact_mm3=round(forward, 5)))


def check_head_fasteners(ctx):
    """Four real button-head seats; no cable or air cut may open their bearing rings."""
    m = ctx.metrics
    axes = np.asarray(m['rim_screws'], float)
    assert axes.shape == (4, 2), f'Head needs exactly four screw axes: {axes.tolist()}'
    recess, length, seat_d = m['head_screw']
    entry, thickness = m['base_h'], m['wall']
    seat = entry + thickness - recess
    penetration = length - thickness + recess
    assert thickness - recess >= 1.2 and 5 <= penetration <= m['insert_depth'] - 0.5, \
        f'Invalid head screw stack: bearing {thickness-recess}, penetration {penetration}'
    local = {n: ctx.manifold(head_frame(ctx.meshes[n], m)) for n in ('head', 'screws_head', 'base')}
    assert len(local['screws_head'].decompose()) == 4, 'Head must have four separate screws'
    rows = []
    for x, y in axes:
        def cyl(z, height, radius):
            return ctx.cylinder([x, y, z], [0, 0, 1], height, radius, 120)
        # Independent annuli preserve a full load path and a closed rim around the shallow pocket.
        bearing = cyl(entry + .02, thickness - recess - .04, 3.15) - cyl(entry, thickness, 1.75)
        enclosure = cyl(seat + .02, recess - .04, 3.9) - cyl(seat, recess, 3.25)
        fill = (bearing ^ local['head']).volume() / bearing.volume()
        rim_fill = (enclosure ^ local['head']).volume() / enclosure.volume()
        assert fill > .995 and rim_fill > .995, f'Incomplete head screw seat at {x,y}: {fill}, {rim_fill}'
        screw = local['screws_head'] ^ _air_box([x-3, y-3, entry-10], [x+3, y+3, seat+3])
        sb = screw.bounding_box()
        assert screw.volume() > 20 and abs(sb[2] - (seat-length)) < .02 \
            and abs(sb[5] - (seat+1.65)) < .02, f'Wrong head screw length or seat at {x,y}'
        contact = (screw.translate([0, 0, -.05]) ^ local['head']).volume()
        assert contact > .1, f'Head screw floats above its bearing at {x,y}'
        press = cyl(entry + .02, 60, 3.175)
        access = (press ^ local['base']).volume()
        assert access < .01, f'Head insert press access blocked at {x,y}: {access}'
        rows.append(dict(axis_mm=[x, y], bearing_fill=round(fill, 5), enclosed_rim_fill=round(rim_fill, 5),
                         screw_contact_mm3=round(contact, 5), insert_access_overlap_mm3=round(access, 5)))
    return dict(head_fasteners=dict(count=4, screw_length_mm=length, insert_penetration_mm=round(penetration, 3),
                bearing_thickness_mm=round(thickness-recess, 3), hole_bottom_clearance_mm=round(m['insert_depth']-penetration, 3),
                seats=rows))


def check_lid_fasteners(ctx):
    """Two closed button-head seats and open, accessible Ruthex pockets."""
    m, solids = ctx.metrics, ctx.solids
    axes = np.asarray(m["ballast_posts"], float)
    assert axes.shape == (2, 2) and np.allclose(axes, [[10, 63], [135, 63]], atol=0.01), \
        f"Ballast lid must have two symmetric screw axes: {axes.tolist()}"
    thickness, recess, length = m["lid_screw"]
    entry, depth = m["ballast"][3], m["insert_depth"]
    seat = entry + thickness - recess
    penetration = length - (thickness - recess)
    assert thickness - recess >= 1.2 and 5.7 <= penetration <= depth - 0.5, \
        f"Ballast lid screw stack is invalid: seat {thickness-recess}, penetration {penetration}"
    assert len(solids["screws_lid"].decompose()) == 2, "Ballast lid must have exactly two screws"
    rows = []
    for x, y in axes:
        def cyl(z, height, radius):
            return ctx.cylinder([x, y, z], [0, 0, 1], height, radius, 120)
        bearing = cyl(entry + 0.01, thickness - recess - 0.02, 3.15) - \
                  cyl(entry, thickness, 1.75)
        enclosure = cyl(seat + 0.02, recess - 0.04, 4.4) - cyl(seat, recess, 3.25)
        bearing_fill = (bearing ^ solids["ball_lid"]).volume() / bearing.volume()
        enclosure_fill = (enclosure ^ solids["ball_lid"]).volume() / enclosure.volume()
        assert bearing_fill > 0.995 and enclosure_fill > 0.995, \
            f"Open or incomplete ballast lid screw seat at {x,y}: {bearing_fill}, {enclosure_fill}"
        screw = solids["screws_lid"] ^ _air_box([x-4, y-4, 0], [x+4, y+4, 40])
        sb = screw.bounding_box()
        assert screw.volume() > 20 and abs(sb[2] - (seat - length)) < 0.02 \
            and abs(sb[5] - (seat + 1.65)) < 0.02, f"Incorrect lid screw length or seat at {x,y}"
        contact = (screw.translate([0, 0, -0.05]) ^ solids["ball_lid"]).volume()
        assert contact > 0.1, f"Lid screw does not bear on its seat at {x,y}"
        # A straight 6.35-mm tool can reach the insert on the bare base.
        press = cyl(entry + 0.01, 60, 3.175)
        access_overlap = (press ^ solids["base"]).volume()
        assert access_overlap < 0.01, f"Lid insert press access blocked at {x,y}: {access_overlap:.4f} mm3"
        bore = cyl(entry - depth + 0.01, depth - 0.02, 1.95)
        assert (bore ^ solids["base"]).volume() < 0.01, f"Lid insert bore is obstructed at {x,y}"
        assert (bore ^ solids["ballast"]).volume() < 0.01, f"Lid insert bore counted as ballast at {x,y}"
        rows.append(dict(axis_mm=[x, y], bearing_fill=round(bearing_fill, 5),
                         enclosed_rim_fill=round(enclosure_fill, 5), screw_contact_mm3=round(contact, 5),
                         insert_tool_diameter_mm=6.35, insert_access_overlap_mm3=round(access_overlap, 5)))
    return dict(lid_fasteners=dict(screw_length_mm=length, insert_engagement_mm=5.7,
                hole_bottom_clearance_mm=round(depth - penetration, 3), seats=rows))


def check_usb_wire_access(ctx):
    """Open inner PCB end and wire corridors around the lateral plug-force stop."""
    bounds = ctx.meshes["usbc"].bounds
    cx, y0 = bounds[:, 0].mean(), bounds[0, 1]
    assert abs(y0 - ctx.metrics["usb_origin"][1]) < 0.03, "USB inner-end reference does not match its mesh"
    rows = {}
    for name, lo_y, hi_y, lo_z, hi_z in (
            ("inner_end", y0 - 2.3, y0 - 0.1, bounds[0, 2] + 0.2, bounds[1, 2] - 0.2),
            ("below", y0 - 5.5, y0 + 1.3, bounds[0, 2] - 2.4, bounds[0, 2] - 0.4),
            ("above", y0 - 5.5, y0 + 1.3, bounds[1, 2] + 0.4, bounds[1, 2] + 2.4)):
        probe = _air_box([cx - 2, lo_y, lo_z], [cx + 2, hi_y, hi_z])
        collisions = {n: round((probe ^ s).volume(), 6) for n, s in ctx.solids.items()
                      if not n.startswith("driver_")}
        collisions = {n: v for n, v in collisions.items() if v > 0.01}
        assert not collisions, f"USB {name}-board wire corridor blocked: {collisions}"
        rows[name] = dict(width_mm=4, height_mm=round(hi_z - lo_z, 3),
                          length_mm=round(hi_y - lo_y, 3), collisions_mm3=collisions)
    return dict(usb_wire_access=rows)


def check_usb_support(ctx):
    """Rear-wall 45-degree gussets, free space below and clear rear-open lid slots."""
    bounds = ctx.meshes['usbc'].bounds
    xmin, xmax = bounds[:, 0]
    y0, zseat = bounds[0, 1], bounds[0, 2]
    front, back = y0 - 2, 71.0
    lower, upper = zseat - 2.2, zseat + 4.5
    floor, top = 3.2, ctx.metrics['ballast'][3]
    front_bottom = top - .4
    left = [xmin - 2.2, xmin - .2]
    right = [xmax - 2.7, xmax + 2.2]
    underside = {}
    for name, (lo, hi) in [('left', left), ('right', right)]:
        ys = np.array([front + .5, (front + back) / 2, back - .5])
        origins = np.array([[(lo + hi) / 2, y, floor + .05] for y in ys])
        hits, rays, _ = ctx.meshes['base'].ray.intersects_location(
            origins, np.tile([0, 0, 1], (len(origins), 1)), multiple_hits=True)
        measured = []
        for index, y in enumerate(ys):
            zs = np.sort(hits[rays == index, 2])
            assert len(zs), f'USB {name} gusset missing above the trough floor'
            expected = front_bottom - (y - front)
            assert abs(zs[0] - expected) < .03, \
                f'USB {name} underside is not the reviewed 45-degree slope at y={y:.3f}: {zs[0]:.3f}'
            measured.append(float(zs[0]))
        slopes = np.diff(measured) / np.diff(ys)
        assert np.allclose(slopes, -1, atol=.01), f'USB {name} underside slope changed: {slopes}'
        # Probe the whole volume below the sloping face, inset from all boundaries.
        ya, yb = front + .03, back - .03
        profile = np.array([[ya, floor + .03], [yb, floor + .03],
                            [yb, front_bottom - (yb - front) - .03],
                            [ya, front_bottom - (ya - front) - .03]])
        free = md.CrossSection([profile], md.FillRule.NonZero).extrude(hi - lo - .06).transform(
            [[0, 0, 1, lo + .03], [1, 0, 0, 0], [0, 1, 0, 0]])
        overlap = (free ^ ctx.solids['base']).volume()
        assert overlap < .01, f'USB {name} still has material below its gusset: {overlap:.4f} mm3'
        underside[name] = dict(y_mm=np.round(ys, 3).tolist(), z_mm=np.round(measured, 3).tolist(),
                               slopes=np.round(slopes, 5).tolist(), free_space_overlap_mm3=round(overlap, 6))
    # The upper walls, broad right support and plug-force stop stay continuous.
    core_specs = {
        'left_wall': ([left[0] + .02, front + .02, top + .02], [left[1] - .02, back - .02, upper - .02]),
        'right_gusset': ([right[0] + .02, front + .02, top + .02], [right[1] - .02, back - .02, lower - .02]),
        'right_wall': ([xmax + .22, front + .02, top + .02], [right[1] - .02, back - .02, upper - .02]),
    }
    filled = {}
    for name, (lo, hi) in core_specs.items():
        probe = _air_box(lo, hi)
        fill = (probe ^ ctx.solids['base']).volume() / probe.volume()
        assert fill > .999, f'USB upper support is not continuous: {name}, {fill:.5f}'
        filled[name] = round(fill, 6)
    slot_overlap = {}
    for name, (lo, hi) in [('left', left), ('right', right)]:
        probe = _air_box([lo - .19, front - .19, top + .01], [hi + .19, 75, top + 2.99])
        overlap = (probe ^ ctx.solids['ball_lid']).volume()
        assert overlap < .01, f'USB support lid slot is blocked or too tight: {name}, {overlap:.4f} mm3'
        slot_overlap[name] = round(overlap, 6)
    contact = (ctx.solids['usbc'].translate([0, 0, -.05]) ^ ctx.solids['base']).volume()
    assert contact > 1, f'USB board floats above its rear seat: {contact:.4f} mm3'
    # A fixed front stop formerly trapped the receptacle in the back wall.
    # Preserve the outer guide but keep the whole moving PCB section open forwards.
    mouth = _air_box([xmin + .02, front - .02, zseat + .02],
                    [xmax - .02, y0 - .22, zseat + 4.28])
    assert (mouth ^ ctx.solids['base']).volume() < .01, 'Fixed USB front stop blocks insertion'
    keeper = ctx.solids['ball_lid'] ^ _air_box([xmax - 2.7, front - 5, top],
                                             [xmax + 5, y0, upper + .1])
    assert keeper.volume() > 400, 'Removable USB stop is missing or too slender'
    gap = keeper.min_gap(ctx.solids['base'], 2)
    assert gap >= .19, f'Removable USB keeper rubs the fixed channel: {gap:.4f} mm'
    # The envelope includes 4.3 mm of components. Test only the first 0.1 mm
    # above the underside so component height cannot stand in for a PCB edge.
    pcb_edge = _air_box([xmax - 2.6, y0, zseat], [xmax - .1, y0 + .5, zseat + .1])
    edge_hit = (pcb_edge.translate([0, -.3, 0]) ^ keeper).volume()
    assert edge_hit > .02, f'USB keeper misses the actual lower PCB edge: {edge_hit:.5f} mm3'
    return dict(usb_support=dict(gusset_undersides=underside, upper_material_fill=filled,
                removable_keeper_to_base_mm=round(gap, 4),
                lower_pcb_edge_contact_mm3=round(edge_hit, 5),
                minimum_floor_clearance_mm=round(float(front_bottom - (back-front) - floor), 3),
                slot_overlap_mm3=slot_overlap, pcb_seat_z_mm=round(float(zseat), 3),
                seat_contact_mm3=round(contact, 5)))


def check_led_window(ctx):
    """Measure both blind LED pockets, optical skins and access from the assembled bay."""
    positions, diameter, clearance, skin, boss = ctx.metrics["led_pocket"]
    base, leds = ctx.solids["base"], ctx.solids["led"]
    assert len(positions) == 2, "Both LED holders must be present"
    assert abs(skin - 0.8) < 0.01, "LED window must retain the reviewed 0.8-mm optical skin"
    assert abs(diameter - 3) < 0.01 and abs(diameter + clearance - 3.2) < 0.01, \
        "LED pocket no longer matches the nominal LEO-AC1 LED and flange seat"
    radius, rear = (diameter + clearance) / 2, boss[1]
    rows, exceptions = [], []
    for x, z in positions:
        material = ctx.cylinder([x, 0.01, z], [0, 1, 0], skin - 0.02, radius, 120)
        missing = (material - base).volume()
        assert missing < 0.0001, f"LED front skin at {(x, z)} is open: {missing:.6f} mm3 missing"
        # The small radial inset avoids comparing two different faceted circles.
        pocket = ctx.cylinder([x, skin + 0.01, z], [0, 1, 0], rear - skin + 0.49, radius - 0.03, 120)
        filled = (pocket ^ base).volume()
        assert filled < 0.0001, f"Blind LED pocket at {(x, z)} is obstructed: {filled:.6f} mm3"

        offsets = [(0, 0), (-0.6, 0), (0.6, 0), (0, -0.6), (0, 0.6)]
        origins = np.array([[x + dx, -1, z + dz] for dx, dz in offsets])
        hits, rays, _ = ctx.meshes["base"].ray.intersects_location(
            origins, np.tile([0, 1, 0], (len(origins), 1)), multiple_hits=True)
        measured = []
        for index in range(len(origins)):
            ys = np.sort(hits[rays == index, 1])
            assert len(ys) >= 2 and abs(ys[0]) < 0.01, "LED window ray misses the closed front face"
            depth = float(ys[1] - ys[0])
            assert abs(depth - 0.8) < 0.02, f"Actual LED skin at {(x, z)} is {depth:.4f} mm"
            measured.append(round(depth, 5))

        led = leds ^ _air_box([x - 2, 0, z - 2], [x + 2, rear + 2, z + 2])
        assert led.volume() > 1, f"Nominal LED envelope missing at {(x, z)}"
        lens_gap = float(led.bounding_box()[1] - skin)
        assert 0.25 <= lens_gap <= 0.35, f"LED lens at {(x, z)} misses the skin clearance: {lens_gap:.3f} mm"
        assert (led ^ base).volume() < 0.01, f"Installed LED at {(x, z)} intersects its pocket"
        ring = ctx.cylinder([x, rear - 0.2, z], [0, 1, 0], 0.19, 1.88, 120) - \
               ctx.cylinder([x, rear - 0.21, z], [0, 1, 0], 0.21, radius + 0.02, 120)
        ring_fill = (ring ^ base).volume() / ring.volume()
        flange_contact = (led.translate([0, -0.05, 0]) ^ base ^
                          _air_box([x - 2, rear - 0.06, z - 2], [x + 2, rear + 0.01, z + 2])).volume()
        assert ring_fill > 0.995 and flange_contact > 0.1, \
            f"LED flange seat at {(x, z)} missing: ring fill {ring_fill:.4f}, contact {flange_contact:.4f} mm3"
        rows.append(dict(centre_xz_mm=[x, z], skin_measurements_mm=measured,
            skin_missing_mm3=round(missing, 7), pocket_filled_mm3=round(filled, 7),
            lens_to_skin_mm=round(lens_gap, 3), flange_ring_fill=round(ring_fill, 5),
            flange_contact_mm3=round(flange_contact, 5)))
        exceptions.append(dict(part="base", feature=f"Closed LED optical skin at x={x}, z={z}",
            nominal_mm=0.8, standard_threshold_mm=1.2,
            bounds_mm=[[x - radius, 0, z - radius], [x + radius, skin, z + radius]],
            policy="Report this intended thin optical area; retain the standard 1.2 mm check elsewhere"))

    # Both paths are parallel in Y; their disjoint XZ envelopes also establish
    # clearance to the other LED when either one remains installed.
    assert np.linalg.norm(np.subtract(positions[0], positions[1])) > 4, "LED access envelopes overlap"
    fixed = [name for name in ctx.solids if name != "led" and not name.startswith("driver_")]
    path = ctx.paths([("led_inside_access", "led", fixed, [0, 1, 0], 15, 0.5)])
    ctx.summary.append("LEDs: two closed 0.8 mm windows and 15 mm inside access")
    ctx.open_items.append("LEDs: test visibility through both 0.8 mm black PETG skins; nominal 3 mm body and "
                          "3.8 mm flange dimensions remain unmeasured, as in LEO-AC1")
    return dict(led_window=dict(windows=rows, inside_access=path, checked_fixed_bodies=fixed,
                               expected_thickness_findings=exceptions))


def check_ballast_cover(ctx):
    """Actual top slices must overlap apart from the narrow assembly seam."""
    top = ctx.metrics["ballast"][3]
    ballast = ctx.solids["ballast"].slice(top - 0.01)
    cover = ctx.solids["ball_lid"].slice(top + 0.1)
    assert ballast.area() > 1000 and cover.area() > 1000, "Ballast cover probe misses the top section"
    uncovered = (ballast - cover.offset(0.3, circular_segments=64)).area()
    assert uncovered < 0.01, f"Ballast lid leaves a top opening beyond its seam: {uncovered:.3f} mm2"
    # Measure the required normal dilation, rather than just testing a formula
    # derived from the nominal clearance. The former 5-mm corner cuts fail here.
    lo, hi = 0.0, 0.45
    for _ in range(14):
        mid = (lo + hi) / 2
        if (ballast - cover.offset(mid, circular_segments=64)).area() > 0.01:
            lo = mid
        else:
            hi = mid
    assert hi <= 0.45, f"Ballast lid seam exceeds 0.45 mm: {hi:.3f} mm"
    return dict(ballast_top_cover=dict(ballast_section_mm2=round(ballast.area(), 3),
        uncovered_beyond_seam_mm2=round(uncovered, 5), max_normal_seam_mm=round(hi, 3)))


def check_switch_trough_clearance(ctx):
    # Only the trough step beside the switch; the mounting well at x >= 138.5
    # intentionally holds the switch and must not be part of this clearance test.
    step = ctx.solids["base"] ^ _air_box([118, 52.9, 3.21], [138.49, 65, 26.01])
    assert step.volume() > 100, "Switch/trough clearance probe misses the trough step"
    gap = step.min_gap(ctx.solids["switch"], 3)
    assert gap >= 1.2, f"Ballast trough crowds the switch body or pins: {gap:.3f} mm"
    return dict(switch_trough_clearance_mm=round(gap, 3))



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


def check_filter_support(ctx):
    """Check the separate cross, all four captured ends and its added air blockage."""
    m = ctx.metrics
    bar, thickness, span, front, rear, pad, post_inner, clearance = m["mat_support"]
    cx, cz = m["body"][0] / 2, m["base_h"] + m["head_h"] / 2
    meshes = {n: head_frame(ctx.meshes[n], m) for n in ("head", "fan", "filter", "filter_support")}
    solids = {n: ctx.manifold(mesh) for n, mesh in meshes.items()}
    support = solids["filter_support"]

    # The end posts nearly touch the fan frame by design. Inspect the part inside
    # the nominal 113-mm rotor disc separately, so those stops cannot hide a bar
    # reaching towards the impeller. This is an envelope gap, not a measured rotor.
    rotor_region = ctx.cylinder([cx, front - 1, cz], [0, 1, 0], rear - front + 2, 113 / 2, 180)
    core = support ^ rotor_region
    assert core.volume() > 100, "Filter support has no central cross"
    core_bounds = core.bounding_box()
    mat_gap = core_bounds[1] - meshes["filter"].bounds[1, 1]
    fan_gap = solids["fan"].min_gap(core, 6.0)
    assert clearance < mat_gap <= 2.35, f"Filter support leaves insufficient mat clearance: {mat_gap:.3f} mm"
    assert abs(core_bounds[1] - front) < 0.03 and abs(core_bounds[4] - front - thickness) < 0.03, \
        "Filter support centre is not in its specified support plane"
    assert fan_gap >= 4.95, f"Filter support approaches the fan envelope: {fan_gap:.3f} mm"
    assert fan_gap - clearance >= 4.75, "Filter support axial play consumes its fan clearance"

    # Check each captured end independently: a summed contact could pass with
    # missing seats. The front stop is the head; the rear stop is the fan frame.
    # No ALLOWED_OVERLAPS entry is used for this part or these probes.
    stop_rows = []
    end_inner = post_inner - 1
    for axis, label in ((0, "horizontal"), (2, "vertical")):
        for sign in (-1, 1):
            lo = np.array([cx - pad / 2 - 0.01, front - 0.01, cz - pad / 2 - 0.01])
            hi = np.array([cx + pad / 2 + 0.01, rear + 0.01, cz + pad / 2 + 0.01])
            centre = cx if axis == 0 else cz
            lo[axis], hi[axis] = ((centre - span / 2 - 0.01, centre - end_inner) if sign < 0
                                  else (centre + end_inner, centre + span / 2 + 0.01))
            end = support ^ _air_box(lo.tolist(), hi.tolist())
            assert end.volume() > 20, f"Filter support end missing: {label}/{sign}"
            row = dict(end=f"{label}_{'negative' if sign < 0 else 'positive'}", volume_mm3=round(end.volume(), 4))
            for direction, target in ((-1, "head"), (1, "fan")):
                # 0.1 mm must remain free; a 0.25-mm shift must reach the stop.
                free = (end.translate([0, direction * clearance / 2, 0]) ^ solids[target]).volume()
                contact = (end.translate([0, direction * (clearance + 0.05), 0]) ^ solids[target]).volume()
                assert free < 0.01, f"Filter support end binds before its nominal stop: {row['end']}/{target}"
                assert contact > 0.01, f"Filter support end has no axial stop: {row['end']}/{target}"
                row[f"{target}_contact_mm3"] = round(contact, 5)
            stop_rows.append(row)

    # Rotate the air axis onto Z, then project the actual cross and all its end
    # posts. Only material within the already open throat counts as added blockage.
    throat_square = md.CrossSection.square([m["open_sq"], m["open_sq"]], True).translate([cx, -cz])
    throat = throat_square - solids["head"].rotate([90, 0, 0]).slice(m["head_y"][2] - 0.1)
    projected = support.rotate([90, 0, 0]).project()
    shadow = md.CrossSection(projected.to_polygons(), md.FillRule.Positive)
    blocked = (shadow ^ throat).area()
    open_area = throat.area()
    assert open_area > 13000, f"Unexpected filter throat area: {open_area:.1f} mm2"
    ideal_cross = 2 * m["open_sq"] * bar - bar * bar
    assert blocked >= ideal_cross * 0.98, "Filter support projection is missing a full-width arm"
    # The reinforced 4-mm arms, rounded centre and broad seats retain at least 92% of the throat.
    assert blocked / open_area < 0.08, f"Filter support blocks {100 * blocked / open_area:.2f}% of the throat"
    return dict(filter_support_checks=dict(
        mat_centre_gap_mm=round(mat_gap, 3), centre_to_fan_mm=round(fan_gap, 3),
        mat_gap_at_front_stop_mm=round(mat_gap - clearance, 3),
        fan_gap_at_rear_stop_mm=round(fan_gap - clearance, 3),
        end_clearance_mm=clearance, end_stops=stop_rows,
        throat_area_mm2=round(open_area, 3), blocked_area_mm2=round(blocked, 3),
        blocked_percent=round(100 * blocked / open_area, 3),
        remaining_area_mm2=round(open_area - blocked, 3)))


def check_pwm_mount(ctx):
    """Measured PCB holes, solid boss seats, blind pilots and two floor-mount screws."""
    m, solids = ctx.metrics, ctx.solids
    assert np.allclose(m['pwm_pcb'], [41.05, 32, 1.6], atol=.001), 'PWM PCB differs from the measured 32 x 41.05 x 1.6 mm'
    assert abs(m['pwm_hole_d'] - 3.2) < .001, 'PWM PCB mounting holes must be 3.2 mm'
    assert abs(m['pwm_boss_d'] - 6) < .001, 'PWM boss exceeds or loses the confirmed 6-mm bearing pad'
    assert np.allclose(m['pwm_core'], [2, 7.4, 2.7, .7], atol=.001), 'PWM pilot or relieved mouth changed'
    assert np.allclose(m['pwm_screw'], [2.5, 8, 4.5, 2.5], atol=.001), 'PWM screw differs from the reviewed 2.5 x 8 / 4.5-mm head envelope'
    x0, y0, z0 = m['pwm_origin']
    axes = np.asarray(m['pwm_holes'], float)
    expected = [[x0 + 3, y0 + 3], [x0 + 29, y0 + 3]]
    assert axes.shape == (2, 2) and np.allclose(axes, expected, atol=.01), \
        f'PWM holes must lie 3 mm from the front/sides, 26 mm apart: {axes.tolist()}'
    pcb, base, screws, drivers = (solids[n] for n in ('pwm_board', 'base', 'screws_pwm', 'driver_pwm'))
    assert len(screws.decompose()) == 2, 'PWM mount requires two separate screws'
    # The section crosses the real PCB, not the component or solder-pin envelopes.
    section = pcb.slice(z0 + .8)
    assert np.allclose(section.bounds(), [x0, y0, x0 + 32, y0 + 41.05], atol=.02), \
        f'PWM PCB mesh bounds differ from the measured board: {section.bounds()}'
    expected_area = 32 * 41.05 - 2 * math.pi * 1.6**2
    assert abs(section.area() - expected_area) < .5, 'PWM PCB section has missing material or extra openings'
    floor_reserve = z0 - 7.4 - m['floor_t']
    assert floor_reserve >= 2, f'PWM pilot leaves only {floor_reserve:.3f} mm above the floor'
    rows, allowed_thread_regions = [], []
    for x, y in axes:
        def cyl(z, height, radius):
            return ctx.cylinder([x, y, z], [0, 0, 1], height, radius, 120)
        def fill(probe, solid):
            return (probe ^ solid).volume() / probe.volume()
        # Test the complete mounting annulus independently on both sides of the PCB.
        board_ring = cyl(z0 + .02, 1.56, 2.95) - cyl(z0, 1.6, 1.63)
        boss_seat = cyl(z0 - .10, .08, 2.95) - cyl(z0 - .12, .12, 1.40)
        board_fill, seat_fill = fill(board_ring, pcb), fill(boss_seat, base)
        assert board_fill > .995 and seat_fill > .995, f'Incomplete PWM bearing ring at {x,y}: {board_fill}, {seat_fill}'
        pcb_hole = cyl(z0 + .01, 1.58, 1.57)
        assert (pcb_hole ^ pcb).volume() < .01, f'PWM PCB hole is not open at {x,y}'
        pilot = cyl(z0 - 7.4 + .02, 7.36, .94)
        assert (pilot ^ base).volume() < .01, f'PWM pilot is obstructed or too shallow at {x,y}'
        # The 2-mm core wall below the conical mouth and the full-depth outer wall must both exist.
        core_wall = cyl(z0 - 7.4 + .02, 6.66, 2.95) - cyl(z0 - 7.4, 6.72, 1.05)
        outer_wall = cyl(z0 - 7.4 + .02, 7.36, 2.95) - cyl(z0 - 7.4, 7.4, 1.40)
        bottom = cyl(m['floor_t'] + .02, floor_reserve - .04, .94)
        wall_fill, outer_fill, bottom_fill = fill(core_wall, base), fill(outer_wall, base), fill(bottom, base)
        assert min(wall_fill, outer_fill, bottom_fill) > .995, \
            f'PWM pilot wall or blind floor missing at {x,y}: {wall_fill}, {outer_fill}, {bottom_fill}'
        roi = _air_box([x-3.1, y-3.1, z0-9], [x+3.1, y+3.1, z0+5])
        screw = screws ^ roi
        sb = np.asarray(screw.bounding_box())
        assert screw.volume() > 50 and np.allclose(sb, [x-2.25, y-2.25, z0-6.4, x+2.25, y+2.25, z0+4.1], atol=.02), \
            f'Incorrect PWM screw length, head or seat at {x,y}: {sb.tolist()}'
        assert (screw ^ pcb).volume() < .01, f'PWM screw overlaps the PCB at {x,y}'
        head_contact = (screw.translate([0, 0, -.05]) ^ pcb).volume()
        board_contact = ((pcb.translate([0, 0, -.05]) ^ base) ^ roi).volume()
        assert head_contact > .2 and board_contact > .5, \
            f'PWM screw head or PCB floats above its bearing at {x,y}: {head_contact}, {board_contact}'
        # Only the shank's 6.4-mm engagement may form a thread in the undersized pilot.
        allowed = cyl(z0 - 6.42, 6.44, 1.27)
        allowed_thread_regions.append(allowed)
        thread = screw ^ base
        excess = (thread - allowed).volume()
        upper_volume = math.pi * (1.25**2 - .97**2) * 6.4
        assert excess < .01 and .5 < thread.volume() < upper_volume, \
            f'PWM screw/base overlap exceeds the intentional pilot thread at {x,y}: {thread.volume()}, excess {excess}'
        # A real slim shaft reaches 25 mm above the conservative screw-head envelope.
        tool_start = z0 + 4.1
        slim = cyl(tool_start + .02, 24.94, 1.97)
        fat = cyl(tool_start + .02, 24.94, 3.3) - cyl(tool_start, 25, 2.04)
        assert fill(slim, drivers) > .995 and (fat ^ drivers).volume() < .01, \
            f'PWM screwdriver lacks the required slim 4-mm / 25-mm exposed shaft at {x,y}'
        for name in ('base', 'pwm_board', 'pot', 'screws_pwm'):
            assert (slim ^ solids[name]).volume() < .01, f'PWM screwdriver blocked by {name} at {x,y}'
        rows.append(dict(axis_mm=[float(x), float(y)], pcb_bearing_fill=round(board_fill, 5), boss_bearing_fill=round(seat_fill, 5),
                         pilot_wall_fill=round(min(wall_fill, outer_fill), 5), blind_floor_fill=round(bottom_fill, 5),
                         head_contact_mm3=round(head_contact, 5), pcb_contact_mm3=round(board_contact, 5),
                         intentional_thread_overlap_mm3=round(thread.volume(), 5), excess_overlap_mm3=round(excess, 5)))
    allowed_all = md.Manifold.batch_boolean(allowed_thread_regions, md.OpType.Add)
    assert ((screws ^ base) - allowed_all).volume() < .01, 'PWM/base collision outside the two intentional thread regions'
    ctx.open_items.append('PWM mounting: verify the 2.0 mm PETG pilot fit with the real 2.5 x 8 screws and measure their head height '
                          '(4.5 mm head diameter confirmed; 2.5 mm height is a conservative envelope). '
                          'Assembly requires a slim 4 mm screwdriver shaft exposed for at least 25 mm.')
    return dict(pwm_mount=dict(pcb_mm=[32, 41.05, 1.6], hole_diameter_mm=3.2, hole_pitch_mm=26,
                screw_length_mm=8, penetration_mm=6.4, pilot_depth_mm=7.4, bottom_clearance_mm=1,
                floor_reserve_mm=round(floor_reserve, 3), driver_shaft_mm=[4, 25], seats=rows))


def check_loaded_lid_removal(ctx):
    """Lift, roll and withdraw the loaded lid through the open electronics bay.

    Remove the head, battery and both lid screws first. The USB-C board, PWM
    controller and rocker switch remain installed. The small roll raises the
    right edge past the switch well while the USB supports occupy their slots.
    """
    m, s = ctx.metrics, ctx.solids
    assert abs(m['ballast'][3] - 26) < .01 and abs(m['usb_origin'][0] - 106) < .01, \
        'Revalidate the loaded-lid service path after changing its reference geometry'
    moving_names = ['ball_lid', 'chg_module', 'chg_sink', 'chg_tie']
    fixed_names = ['base', 'pwm_board', 'pot', 'usbc', 'switch', 'led', 'ballast', 'feet']
    moving = md.Manifold.batch_boolean([s[n] for n in moving_names], md.OpType.Add)
    fixed = md.Manifold.batch_boolean([s[n] for n in fixed_names], md.OpType.Add)
    lift, roll, forward, final_lift = 11.4, -5.9, 20., 60.
    pivot = np.array([106., 63., 37.])
    lifted = moving.translate([0, 0, lift])

    def tilted(angle):
        return lifted.translate(-pivot).rotate([0, angle, 0]).translate(pivot)

    rolled = tilted(roll)
    segments = [
        ('lift', (moving.translate([0, 0, float(d)]) for d in np.linspace(0, lift, 115)),
         dict(distance_mm=lift, step_mm=.1)),
        ('roll_right_edge_up', (tilted(float(a)) for a in np.linspace(0, roll, 60)),
         dict(angle_deg=roll, step_deg=.1, pivot_mm=pivot.tolist())),
        ('forward', (rolled.translate([0, -float(d), 0]) for d in np.linspace(0, forward, 201)),
         dict(distance_mm=forward, step_mm=.1)),
        ('out', (rolled.translate([0, -forward, float(d)]) for d in np.linspace(0, final_lift, 121)),
         dict(distance_mm=final_lift, step_mm=.5)),
    ]
    rows = []
    for name, poses, specification in segments:
        peak, count, minimum_gap = 0., 0, 2.
        for count, q in enumerate(poses, 1):
            overlap = (q ^ fixed).volume()
            assert overlap < .01, \
                f'Loaded lid removal blocked during {name}/{count}: {overlap:.6f} mm3'
            peak = max(peak, overlap)
            if name != 'lift':
                minimum_gap = min(minimum_gap, q.min_gap(fixed, 2.))
        row = dict(stage=name, samples=count, maximum_overlap_mm3=round(peak, 7), **specification)
        if name != 'lift':
            assert minimum_gap >= .15, \
                f'Loaded lid needs practical clearance during {name}: {minimum_gap:.5f} mm'
            row['minimum_clearance_mm'] = round(minimum_gap, 5)
        rows.append(row)

    # The starting lid intentionally bears on its screw posts. Report free
    # clearances only after lifting; a zero at the initial seat is not a fault.
    gap_cap = 2.
    endpoint_gaps = {}
    for name, q in [('lifted', lifted), ('rolled', rolled),
                    ('forward', rolled.translate([0, -forward, 0]))]:
        endpoint_gaps[name] = round(q.min_gap(fixed, gap_cap), 5)
    final = rolled.translate([0, -forward, final_lift])
    above_base = final.bounding_box()[2] - s['base'].bounding_box()[5]
    assert above_base > 10, 'Loaded lid path ends inside the housing instead of fully outside it'
    ctx.open_items.append('Loaded ballast lid: after removing the head, battery and lid screws, lift 11.4 mm, '
                          'raise its right edge with a 5.9-degree roll, move 20 mm forwards and lift out. '
                          'The sampled rigid path requires at least 0.15 mm clearance after the initial lift; '
                          'real print tolerance, finger access '
                          'and connected wiring are not validated.')
    return dict(loaded_lid_removal=dict(moving=moving_names, fixed=fixed_names,
                removed_first=['head_group', 'battery', 'screws_lid'], stages=rows,
                endpoint_clearance_mm=endpoint_gaps, clearance_search_cap_mm=gap_cap,
                final_bottom_above_base_mm=round(above_base, 3)))


def check_pwm_removal(ctx):
    """Sample the complete service motion with the real tab and both screws.

    Remove the head, battery, loaded ballast lid, knob, PCB screws and rocker
    switch first. The USB-C board and LEDs remain fitted. The reverse motion
    installs the controller before the switch; wiring flexibility is unmodelled.
    """
    m, s = ctx.metrics, ctx.solids
    assert np.allclose(m['pwm_origin'], [100, 2.55, 13.1], atol=.01), 'Revalidate PWM service path for changed PCB placement'
    tab_probe = _air_box([114.97, .62, 15.22], [117.03, 1.78, 15.98])
    assert (tab_probe ^ s['pot']).volume() / tab_probe.volume() > .995, 'PWM service path lacks the real potentiometer tab'
    fixed_names = ['base', 'ballast', 'usbc', 'led', 'feet']
    fixed = md.Manifold.batch_boolean([s[n] for n in fixed_names], md.OpType.Add)
    board = s['pwm_board'] + s['pot']
    pivot = np.array([116, .9, 24.4])

    def pose(lift=3.4, rear=8, angle=0, postrear=0, postup=0):
        return (board.translate([0, rear, lift]).translate(-pivot)
                .rotate([angle, 0, 0]).translate(pivot + [0, postrear, postup]))

    # Keep intermediate poses: checking only endpoints misses both the front
    # boss/pin crescents and the upper-front loft. Angles raise the PCB's rear.
    segments = [
        ('lift_first', [pose(lift=d, rear=0) for d in np.linspace(0, 2, 21)]),
        ('lift_clear', [pose(lift=2 + 1.4*u, rear=.5*u) for u in np.linspace(0, 1, 29)]),
        ('retract', [pose(rear=d) for d in np.linspace(.5, 8, 76)]),
        ('pitch', [pose(rear=8 + max(0, a-15)/20*.6, angle=a, postup=-.6*a/35)
                   for a in np.linspace(0, 35, 71)]),
        ('withdraw', [pose(rear=8.6, angle=35, postrear=d, postup=-.6)
                      for d in np.linspace(0, 7.9, 80)]),
        ('lift_rear', [pose(rear=8.6, angle=35, postrear=7.9, postup=-.6+d)
                      for d in np.linspace(0, 4.5, 46)]),
        ('clear_rim', [pose(rear=8.6, angle=35, postrear=7.9+d, postup=3.9)
                      for d in np.linspace(0, 2, 21)]),
        ('up', [pose(rear=8.6, angle=35, postrear=9.9, postup=3.9+d)
                for d in np.linspace(0, 60, 121)]),
    ]
    rows = []
    for name, poses in segments:
        peak = 0.
        for index, q in enumerate(poses):
            volume = (q ^ fixed).volume()
            assert volume < .01, f'PWM removal blocked during {name}/{index}: {volume:.5f} mm3'
            peak = max(peak, volume)
        rows.append(dict(stage=name, samples=len(poses), maximum_overlap_mm3=round(peak, 6)))

    # Both fasteners leave vertically. While unscrewing, only the already
    # reviewed pilot-thread region may overlap the base; no broad exemption.
    allowed_thread = md.Manifold.batch_boolean([
        ctx.cylinder([x, 5.55, 6.6], [0, 0, 1], 6.51, 1.3, 120)
        for x in (103, 129)], md.OpType.Add)
    fastener_fixed_names = fixed_names + ['pwm_board', 'pot', 'switch']
    screw_rows = []
    for index, screw in enumerate(s['screws_pwm'].decompose()):
        peak = 0.
        for d in np.linspace(0, 60, 241):
            q = screw.translate([0, 0, float(d)])
            for name in fastener_fixed_names:
                collision = q ^ s[name]
                if name == 'base':
                    collision -= allowed_thread
                volume = collision.volume()
                assert volume < .01, f'PWM screw {index} removal blocked by {name} at {d:.2f} mm: {volume:.5f} mm3'
                peak = max(peak, volume)
        screw_rows.append(dict(screw=index, distance_mm=60, step_mm=.25,
                               maximum_unintended_overlap_mm3=round(peak, 6)))

    # Shaft/sleeve contact is the intended push fit. Other fitted parts cannot
    # interfere while pulling the knob straight forwards with the head removed.
    knob_fixed = md.Manifold.batch_boolean([s[n] for n in fixed_names + ['pwm_board', 'switch']], md.OpType.Add)
    knob_peak = 0.
    for d in np.linspace(0, 20, 81):
        volume = (s['knob'].translate([0, -float(d), 0]) ^ knob_fixed).volume()
        assert volume < .01, f'PWM knob removal obstructed at {d:.2f} mm: {volume:.5f} mm3'
        knob_peak = max(knob_peak, volume)
    ctx.open_items.append('PWM service motion is sampled at 0.1 mm / 0.5 degrees (final lift 0.5 mm); '
                          'remove the head, battery, loaded ballast lid, knob, PCB screws and rocker switch first. '
                          'The real wiring and flexible leads are not modelled.')
    return dict(pwm_removal=dict(removed_first=['head_group', 'battery', 'loaded_ballast_lid', 'knob', 'screws_pwm', 'switch'],
                pivot_mm=pivot.tolist(), stages=rows, screws=screw_rows,
                knob_distance_mm=20, knob_step_mm=.25, knob_maximum_overlap_mm3=round(knob_peak, 6)))


def check_usb_installation(ctx):
    """Continuous rigid-body entry through the open bay before other parts are fitted."""
    usb, base = ctx.solids["usbc"], ctx.solids["base"]
    mesh = ctx.meshes["usbc"]
    assert usb.volume() > 1 and len(mesh.faces), "USB installation probe has no moving body"
    offsets = [np.array(p, dtype=float) for p in ([0, 0, 0], [0, -20, 0], [0, -20, 30])]
    rows = []
    for start, end in zip(offsets[:-1], offsets[1:]):
        # The starting body plus every swept boundary triangle covers the complete
        # translational sweep. Each triangle sweeps an exact convex prism; hulling
        # the whole PCB would fill its concave transition to the receptacle.
        collisions = [usb.translate(start) ^ base]
        for triangle in mesh.triangles:
            prism = md.Manifold.hull_points(np.vstack([triangle + start, triangle + end]))
            if prism.volume() > 1e-9:  # parallel triangles sweep no volume
                collisions.append(prism ^ base)
        overlap = md.Manifold.batch_boolean(collisions, md.OpType.Add).volume()
        assert overlap < .01, \
            f"USB installation sweep {start.tolist()} to {end.tolist()} blocked: {overlap:.6f} mm3"
        rows.append(dict(from_offset_mm=start.tolist(), to_offset_mm=end.tolist(),
                         swept_overlap_mm3=round(overlap, 8)))
    free_bounds = np.asarray(mesh.bounds) + offsets[-1]
    base_top = float(ctx.meshes["base"].bounds[1, 2])
    free_height = float(free_bounds[0, 2] - base_top)
    assert free_height > 5, \
        f"USB installation path does not reach outside the base: {free_height:.3f} mm above its top"
    ctx.summary.append("USB: continuous 20 mm forward / 30 mm upward extraction reaches outside the open base")
    return dict(usb_installation=dict(
        assembly_stage="Bare open base, before fitting the ballast lid and other components; install by reversing the path",
        checked_fixed_bodies=["base"], method="Continuous swept boundary-triangle prisms and starting body",
        maximum_overlap_mm3=.01, extraction_segments=rows,
        installation_offsets_mm=[p.tolist() for p in reversed(offsets)],
        free_end_bounds_mm=np.round(free_bounds, 5).tolist(), base_top_mm=round(base_top, 5),
        free_end_above_base_mm=round(free_height, 5)))


def check_battery_retention(ctx):
    """Test axial capture on the meshes, including the cell's radial play in its saddles."""
    battery, lid = ctx.solids["battery"], ctx.solids["ball_lid"]
    x0, cy, cz, diameter, length, bms = ctx.metrics["battery"]
    assert abs(diameter - 32.5) < .01 and abs(length - 71.6) < .01, \
        "Battery envelope no longer matches the measured LEO-AC1 cell"
    end = float(battery.bounding_box()[3])
    rim = ctx.metrics["ballast"][3]
    # Restrict the stop to the new tongue so another part cannot conceal its absence.
    tongue = lid ^ _air_box([end, cy - 6, rim], [end + 14, cy + 17, rim + 3.01])
    assert tongue.volume() > 400, "Battery has no substantial right-hand lid stop"
    gap = battery.min_gap(tongue, 2)
    assert .45 <= gap <= .55, f"Battery end-stop clearance is {gap:.3f} mm"
    rows = []
    # The closed head catches an upward-moving cell within 3 mm. Test the
    # tongue at the seated position and after 1/2 mm of lift, without foam friction.
    for dy in (-.4, 0, .4):
        for dz in (0, 1, 2):
            moved = battery.translate([0, dy, dz])
            assert (moved ^ ctx.solids["base"]).volume() < .01, \
                f"Battery retention probe starts inside the base at {(dy, dz)}"
            free = (moved.translate([.3, 0, 0]) ^ tongue).volume()
            hit = (moved.translate([.75, 0, 0]) ^ tongue).volume()
            assert free < .01, f"Battery stop removes the assembly clearance at {(dy, dz)}"
            assert hit > 5, f"Battery can slide past its lid stop at {(dy, dz)}: {hit:.4f} mm3"
            rows.append(dict(offset_yz_mm=[dy, dz], free_at_03_mm3=round(free, 6),
                             contact_at_075_mm3=round(hit, 5)))
    # Reserve the space beyond the upper end of the BMS. This is a geometric
    # opening, not a measurement of the real pack's wires or connector.
    corridor = _air_box([end + .05, cy - bms[0] / 2, cz + diameter / 4],
                        [end + 12, cy + bms[0] / 2, cz + diameter / 2 + bms[1]])
    blocked = (corridor ^ lid).volume()
    assert blocked < .01, f"Battery stop blocks the upper cable exit: {blocked:.4f} mm3"
    ctx.summary.append("Battery: axial lid stop holds in nine shifted/lifted poses")
    ctx.open_items.append("Battery: check the replacement lid's end-stop fit and actual cable exit; "
                          "the open base intentionally permits upward battery removal")
    return dict(battery_retention=dict(right_gap_mm=round(gap, 4), shifted_axial_probes=rows,
                upper_cable_corridor_overlap_mm3=round(blocked, 6),
                limitation="Rigid translation probes; no foam friction, strength or physical-fit proof"))


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
        ("pwm_board", "base", [0, 0, -1]),            # board on the bosses and rear rib pads
        ("chg_module", "ball_lid", [0, 0, -1]),       # lower cut edge at the cool OUT end
        ("ball_lid", "base", [0, 0, -1]),             # lid on its posts and walls
        ("usbc", "base", [0, 0, -1]),                 # PCB on the gusset-supported rear seat
    ])
    # Stops: the fan cannot move sideways in its corner guides, the head is located by its screws
    # There is no register between head and base: the four screws locate it, so that is what is checked
    # usbc_in: pushing a cable into the socket must not push the board into the bay
    stops = ctx.stops([("fan_sideways", "fan", "head", [1, 0, 0], 1.5),
                       ("usbc_in", "usbc", "ball_lid", [0, -1, 0], 0.6),
                       ("head_on_screws", "head", "screws_head", [1, 0, 0], 0.6),
                       ("battery_right", "battery", "ball_lid", [1, 0, 0], 0.8),
                       ("battery_left", "battery", "base", [-1, 0, 0], 1.25),
                       ("battery_up_closed", "battery", "head", [0, 0, 1], 3),
                       ("battery_down", "battery", "base", [0, 0, -1], 0.8),
                       ("battery_forward", "battery", "base", [0, -1, 0], 0.8),
                       ("battery_backward", "battery", "base", [0, 1, 0], 0.8),
                       ("charger_forward", "chg_module", "chg_tie", [0, -1, 0], 0.4),
                       ("charger_backward", "chg_module", "ball_lid", [0, 1, 0], 0.4)])
    # Foam tape cushions the open saddles; the lid tongue supplies positive axial retention.
    # 0.2 for the heatsink: nominal 0.3 in its wall cut-out, less the facets of the rounded corners
    gaps = ctx.clearances([("battery", "base", 0.3), ("battery", "head", 1.0),
                           ("chg_sink", "fan", 1.5), ("ball_lid", "switch", 1.2)])
    # Assembly paths, not only end positions. The head is pulled off along the tilted normal.
    up = [0, -math.sin(tilt), math.cos(tilt)]
    out = [0, -math.cos(tilt), -math.sin(tilt)]       # out of the intake face, normal to it
    paths = ctx.paths([
        ("cassette_off", "cassette", ["head", "base", "fan", "filter"], out, 30, 0.5),
        # the fan is bolted to the cover, so it comes off with it
        ("cover_off", ["head_back", "fan", "screws_fan"], ["head", "base", "filter_support", "chg_module", "chg_sink", "chg_tie"],
         [-o for o in out], 30, 0.5),
        # The fan frame captures the support's four ends. Remove fan and cover,
        # then lift the cross straight out of the rear-open head sockets.
        ("support_out", "filter_support", ["head", "base", "filter"], [-o for o in out], 30, 0.5),
        # Remove the head and cut/remove the cable tie, then lift the board and heatsink.
        ("chg_off", ["chg_module", "chg_sink"],
         ["base", "ball_lid", "battery", "pwm_board", "usbc", "switch", "led", "pot", "screws_lid"],
         [0, 0, 1], 30, 0.5),
        # Remove the head, battery and lid screws before lifting the loaded lid.
        # Retain the initial straight lift as a separate probe; the full lift,
        # roll and withdrawal is checked in check_loaded_lid_removal().
        ("lid_off", ["ball_lid", "chg_module", "chg_sink", "chg_tie"],
         ["base", "ballast", "pwm_board", "usbc", "switch"], [0, 0, 1], 10, 0.5),
        ("fan_out", ["fan", "screws_fan"], ["head", "base", "filter_support"], [-o for o in out], 40, 0.5),   # cover off first
        ("head_off", ["head", "head_back", "cassette", "fan", "filter", "filter_support", "magnets"],
         ["base", "battery", "pwm_board", "usbc", "switch", "pot", "led", "ball_lid", "ballast",
          "chg_module", "chg_sink", "chg_tie"], up, 60, 1),
        ("battery_out", "battery", ["base", "pwm_board", "usbc", "switch", "ball_lid"], [0, 0, 1], 40, 0.5),
        # Remove the head and loaded ballast lid first. Withdraw the USB board
        # into the bay, then lift it completely above the rim; reverse to install.
        ("usbc_out", "usbc", ["base", "battery", "pwm_board", "pot", "switch", "led", "ballast"],
         [([0, -1, 0], 20, .25), ([0, 0, 1], 30, .25)]),
        ("knob_off", "knob", ["base"], [0, -1, 0], 20, 0.5),
    ])
    # Heat-set insert pockets: core open, datasheet wall and floor ring material. Everything in the head
    # is pressed in along its own axis, so the probes use the tilted frame.
    d, depth, w = m["insert_hole_d"], m["insert_depth"], m["insert_w_min"]
    back = [-o for o in out]
    probes = ctx.insert_probes(
        [("head_back", _tilt(m, [p[0], m["head_y"][3], p[1]]), back, depth, d, w) for p in m["fan_holes"]] +
        [("head", _tilt(m, [p[0], m["back_y"], p[1]]), out, depth, d, w) for p in m["head_bosses"]] +
        [("base", _tilt(m, [p[0], p[1], m["base_h"]]), [-u for u in up], depth, d, w) for p in m["rim_screws"]] +
        [("base", [p[0], p[1], 0], [0, 0, 1], depth, d, w) for p in _foot_xy(m)] +
        [("base", [p[0], p[1], m["ballast"][3]], [0, 0, -1], depth, d, w)
         for p in m["ballast_posts"]])
    # Air must not bypass the mat: the chamber lip overlaps it on every side, front and back
    lip = (m["chamber"][0] - m["open_sq"]) / 2
    assert lip >= 2, f"Intake lip only {lip:.2f} mm wide"
    # And the mat must not travel back into the fan. The rear lip closes the bore from the chamber to
    # open_sq along a ramp, so a 120 mm mat is caught where the bore first drops below 120.
    y0, y1 = m["mat_stop"]
    mat_free = y0 + (m["chamber"][0] - MAT[0]) / (2 * lip) * (y1 - y0) - (m["head_y"][0] + MAT[2])
    fan_gap = m["head_y"][2] - (m["head_y"][0] + MAT[2])
    assert 0 < mat_free < 0.25 * fan_gap, f"Mat travels {mat_free:.1f} mm of the {fan_gap:.1f} mm to the fan"
    # The rigid nominal mat must not be displaced by the head or its rear support.
    # Flexible bulging towards the central cross is outside this envelope check.
    squashed = (ctx.solids["filter"] ^ ctx.solids["head"]).volume()
    mat = MAT[0] * MAT[1] * MAT[2]
    assert squashed < 0.05 * mat, f"Head displaces {squashed / mat:.1%} of the mat"

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
                **check_rim_chamfers(ctx), **check_charger_air(ctx), **check_charger_holder(ctx),
                **check_lid_fasteners(ctx), **check_head_fasteners(ctx), **check_pwm_mount(ctx), **check_pwm_removal(ctx), **check_usb_wire_access(ctx), **check_ballast_cover(ctx),
                **check_switch_trough_clearance(ctx), **check_filter_support(ctx), **check_led_window(ctx), **check_usb_support(ctx),
                **check_battery_retention(ctx), **check_usb_installation(ctx), **check_loaded_lid_removal(ctx))


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
           ("filter_support", "Filter support cross", "black", "#aeb5bb", "1x", [0, 0.15, 1.35]),
           ("knob", "Speed knob", "grey", "#c4c9ce", "1x", [0, -0.6, 0]),
           ("feet", "Feet", "tpu", "#55595e", "4x", [0, 0, -0.6]),
           ("fan_visual", "Fan 120 x 25", "bought", "#6a6f75", "1x", [0, 0.5, 1.35]),
           ("filter", "Filter mat 120 x 120 x 17", "bought", "#a09488", "1x", [0, -0.9, 1.1]),
           ("battery", "LiFePO4 3.2 V 6 Ah", "bought", "#4a6d3f", "1x", [0, 0, -0.2]),
           ("pwm_board", "PWM controller", "bought", "#2f5d3a", "1x", [0, -0.2, 0]),
           ("chg_module", "Charge / boost module", "bought", "#2f5d3a", "1x", [0, 0, 0.3]),
           ("chg_sink", "Heatsink", "bought", "#9aa0a6", "1x", [0, 0, 0.3]),
           ("chg_tie", "Charge-module cable tie", "bought", "#55595e", "1x", [0, 0, 0.3]),
           ("usbc", "USB-C PD trigger", "bought", "#2f5d3a", "1x", [0, 0.8, 0]),
           ("switch", "Rocker switch", "bought", "#3a3d42", "1x", [0.8, 0, 0]),
           ("magnets", "Magnets 10 x 3", "bought", "#9aa0a6", "8x", [0, -1.2, 0.9]),
           ("screws_fan", "Screws M3 x 30", "bought", "#9aa0a6", "4x", [0, 0.9, 1.35]),
           ("screws_back", "Screws M3 x 8", "bought", "#9aa0a6", "4x", [0, 2.8, 0.6]),
           ("screws_head", "Screws M3 x 8", "bought", "#9aa0a6", "4x", [0, -0.3, 1.6]),
           ("screws_feet", "Screws M3 x 8", "bought", "#9aa0a6", "4x", [0, 0, -1.0]),
           ("screws_pwm", "PCB screws 2.5 x 8", "bought", "#9aa0a6", "2x", [0, 0, 0.9]),
           ("screws_lid", "Lid screws M3 x 8", "bought", "#9aa0a6", "2x", [0, 0, 1.1]),
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
                              "color(\"#aeb5bb\") chg_sink_env(); color(\"#55595e\") chg_tie_env();", "110,-90,90,70,60,34"),
         "05_charger_back": ("color(\"#8a9096\") ball_lid(); color(\"#2f5d3a\") chg_module_env(); "
                             "color(\"#aeb5bb\") chg_sink_env(); color(\"#55595e\") chg_tie_env();", "110,180,90,70,60,34"),
         "06_filter_support": ("color(\"#aeb5bb\") filter_support_raw();", "220,-240,220,72.5,26,120.5"),
         # Exploded only along Z: the two screw heads and both lid holes stay visible.
         "07_ballast_mount": ("color(\"#717980\") intersection() { base(); "
                              "translate([0, ball[2] - 1, 0]) cube([body_w, body_d - ball[2] + 1, ball[3] + 0.2]); } "
                              "color(\"#b8c0c7\") translate([0, 0, 8]) ball_lid(); "
                              "color(\"#414950\") translate([0, 0, 16]) screws_lid(socket = true);",
                              "100,-180,240,72.5,63,24"),
         "08_usb_mount": ("color(\"#8a9096\") intersection() { base(); "
                          "translate([94, 57.4, 0]) cube([24, 17.6, 60]); } "
                          "color(\"#2f5d3a\") usbc_env();",
                          "145,-45,85,106,64,25"),
         "09_head_mount": ("color(\"#aeb5bb\") head_at() intersection() { head_raw(); "
                           "translate([-1, head_y[3], base_h - 0.1]) "
                           "cube([body_w + 2, body_d - head_y[3] + 1, 12]); } "
                           "color(\"#414950\") translate([0, -5*sin(tilt), 5*cos(tilt)]) "
                           "screws_head(socket = true);",
                           "105,-165,230,72.5,63,55"),
         "10_pwm_mount": ("color(\"#8a9096\") intersection() { base(); "
                          "translate([96, 1, 0]) cube([41, 45, pwm_z0 + 0.1]); } "
                          "color(\"#2f5d3a\") translate([0, 0, 5]) intersection() { pwm_board_env(); "
                          "translate([pwm_x[0]-1, pwm_y0-1, pwm_z0]) cube([pwm_pcb[1]+2, pwm_pcb[0]+2, pwm_pcb[2]]); } "
                          "color(\"#aeb5bb\") translate([0, 0, 5]) pot_env(); "
                          "color(\"#414950\") translate([0, 0, 12]) screws_pwm();",
                          "180,-90,110,116,21,14"),
         "11_battery_usb_stops": ("color(\"#8a9096\") ball_lid(); "
                                 "color(\"#4a6d3f\") battery_env(); "
                                 "color(\"#2f5d3a\") usbc_env();",
                                 "135,-120,160,72.5,45,25")}
