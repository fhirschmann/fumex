# AGENTS.md — working on FUMEX

Internal notes for coding agents (Claude, Codex). The README is public and stays free of process notes, audits, assumptions and tool internals; put those here.

## Working rules

- Talk to the user in German. README, AGENTS.md, code comments, viewer labels, slicer plate/material names, check messages **and all commit messages** are English (user, 2026-09-21).
- The project follows the skill `openscad-print-project` (`~/.claude/skills/openscad-print-project`). After every model change run the full loop: `print_tools.py export` → `analyze.py islands/overhangs/thickness/fins` → `slice_check.py` → update README numbers → `build_viewer.py --copy-to docs/index.html` → commit.
- Always rebuild the viewer after every model or layout change, before reporting completion (user, 2026-09-23). Regenerate `build/viewer.html` and `docs/index.html` from the current assembly exports; updating only the STLs is not enough. If the open browser tab cannot be refreshed, say so explicitly rather than implying that its displayed state has updated.
- `scripts/` must stay identical to the skill (`python3 ~/.claude/skills/openscad-print-project/scripts/skill_sync.py status -C .`). Improve tools in the skill and adopt/install them; no project-local forks.
- No painted or scripted supports. Every part prints without them; `analyze.py overhangs` is CLEAN and must stay that way.
- No vendor CAD in the repo or the viewer. The fan is the simple `fan_visual()` placeholder.
- Electrically this is LEO-AC1 minus the bail, the QR code and the logo. When a measured value of a shared part is needed, take it from `~/Projects/leo-ac1/AGENTS.md` rather than re-measuring.

## BOSL2 provenance and scope

- `BOSL2/` is a Git submodule pinned to `989cc33b56313238f3ffeafcbd2876b71a0a593a`. Initialise it with `git submodule update --init --recursive`; it retains its BSD-2-Clause licence.
- `profile_sweep_y()` uses BOSL2 `offset_sweep()` and `os_chamfer()` on the finished head, cover, cassette and filter-support outlines. The bevels are measured from their actual end planes, so the former hull-tip thickness no longer changes their height or width. The base bottom bevel uses the same operations on `joint_plan_points(0)`.
- This is a targeted edge-profile change. The tangent R3.5 plan rounds along the long sides of the head and cover are deliberately retained; do not add a second bevel across them. The upper-corner blends and the joint loft remain the specific G2/G3 geometry described below.
- BOSL2 quantizes these offsets to 1/1024 mm, so a 1.2 mm chamfer finishes at 1.200195 mm. The cutters must extend beyond that end; the head/cover tools also offset the outside profile one grid step and add the same amount to the chamfer to avoid a vanishing cut against the native outline. Do not trim the tool at exactly `edge_c` or remove that overlap. The local helpers are named `bounds_rect` and `axis_orient` to avoid BOSL2's `rect` and `orient` names.

## User constraints and preferences

- Bench tool, no child-safety requirement. Plain and functional: no logo, no QR code, no decorative grooves (user, 2026-09-21).
- Two colours, part by part: base in Bambu PETG black; head, cassette, back cover, ballast lid, support cross and knob in grey (back cover, ballast lid and support cross changed at the user's request on 2026-09-28; head on 2026-09-29). The grey knob has a dark housing-colour pointer inlay (user, 2026-09-28); only its separate plate uses a prime tower. Other parts remain single-colour.
- Current production layout (user, 2026-09-28): plate 1 head, plate 2 base, plate 3 cassette, plate 4 grey back cover / ballast lid / support cross, plate 5 knob, plate 6 TPU feet. Head and cassette remain on separate plates, both grey. The 2026-09-29 screw interface removes all magnet insertion pauses; the earlier shared cassette/cover/lid plate is superseded. The grey support cross retains 100% infill.
- **The viewer colours are deliberately not the filament colours** (user, 2026-09-22): black PETG renders as a
  silhouette on screen and the geometry disappears, so `VIEWER["parts"]` uses lifted greys. Do not "correct"
  them back to #1a1b1d; the real colours live in `FILAMENTS`, the plate names and the README.
- Except for the two user-supplied 2.5 x 8 thermoplastic PWM PCB screws, screws only ISO 7380 button head Torx from the user's set (M3 × 6/8/10/12/16/25). The four fan screws M3 × 30 are a deliberate extra purchase — a 25 mm fan frame cannot be screwed with anything shorter, whichever side the screw comes from (the user first chose M3 × 25 from the set, which is geometrically impossible; corrected 2026-09-21).
- Ruthex RX-M3x5.7 per datasheet: hole 4.0, pocket depth ≥ 6.7, wall ≥ 1.6, pressable from an accessible side.
- Printer Bambu Lab H2S with AMS.
- Preferred build surface (user, 2026-09-29): Engineering Plate fully sprayed with
  3DLAC before a batch, for its smooth finish. Arrange successive virtual plates
  on separate physical bed areas so one coating serves multiple jobs. Remove all
  finished parts and print debris between jobs; do not leave previous parts standing.
  Keep different-material jobs separate; if future parts require insertion pauses, retain their separate jobs too. Include brims, skirts and prime
  towers in the used footprint; preserve normal start/calibration routines.

## Measured hardware

Shared parts are the ones measured for LEO-AC1 on 2026-09-15/18 (battery, PWM controller, potentiometer, charge module, USB-C module, rocker switch); the table there is the source. New here:

| Part | Value | Status |
|---|---|---|
| Fan Arctic P12 Pro (PST) | 120 × 120 × 25 mm, 185 g, 600–3000 rpm, 77 cfm / 131 m³/h, 6.9 mmH₂O, 12 V, **0.33 A**, start-up 3.3 V, 0 rpm below 5 % PWM, cable 400 + 80 mm, 0–40 °C | data sheet (ACFAN00306A) |
| Filter mat | cut by the user from a cooker hood mat to about 120 × 120 × 17 mm, white fleece with a dark carbon layer | user, 2026-09-21, hand-cut — the chamber is 121.5 mm and the lip 2.25 mm wide, so ±1 mm on the cut is fine |
| Former magnets (removed 2026-09-29) | 8 × neodymium disc Ø10 × 3 | historical interface only; nominal size was unmeasured and cavities were Ø10.04 × 3.2 mm with 1.2 mm skins. Superseded by four M3 × 8 screws and Ruthex inserts |
| USB-C PD module PCB width | 10.06 mm | measured on this board by the user, 2026-09-28; supersedes LEO-AC1's 10.35 mm width for FUMEX only |
| Masses for the tipping check | fan 185 g (data sheet), battery 150 g, PWM board 12 g, mat 15 g, rest estimated; the former 18 g magnet allowance is removed | **estimates**, reported as an open item |

## Current design state

- **Battery retention and USB fit (user, 2026-09-24):** the printed battery slid lengthwise,
  and the USB-C module could not be threaded into its fixed front stop. Neither issue was a confirmed
  tolerance mismatch. End-position collision checks alone had missed both problems.
  - The battery's right axial stop is now part of the **base**, not the ballast lid: x76.1..79.1,
    y30..51, rooted continuously in the 3.2 mm floor and ending at z29. It is 3 mm thick, with R1
    plan corners and a 0.4 mm top bevel. The nominal cell ends at x75.6, leaving 0.5 mm axial play.
    Its top stays 1.125 mm below the BMS envelope. The earlier 8 mm lid tongue is removed; the
    base must contain the new end wall. Foam cushions the pack but is not the axial restraint.
    A 3 mm thick floor-rooted connection now joins its rear end to the fixed trough
    wall (user, 2026-09-25). It spans x76.1..79.1 and y49.6..54, with a top descending
    from z29 at y49.6 to z25.6 at y53, then remaining level inside the wall. The
    1 mm wall overlap and original-stop overlap form a continuous connection;
    the lid starts at z26, retaining 0.4 mm vertical clearance over the connection.
    Battery-facing clearance, the upper cable opening and the lid itself are unchanged.
  - LEO-AC1 supplies the measured Ø32.5 x 71.6 mm cell and the approximate 20 mm wide, 4 mm thick
    protection board along its full length. Here the BMS faces up: x4..75.6, y25..45,
    z30.125..42.25 in the conservative bought-part envelope. LEO's body/back halves close three
    rings around its upright cell; its shelf stops axial motion. Those positive stops, rather than
    foam adhesion, are the reference. The subsequent direct-tie change is described below; it does not retain the old BMS load-isolation claim.
  - **Two cable ties through base-floor loops** replace the head-mounted shoulder retainers
    (user, 2026-09-25). Their axes are x26/54, between the existing saddles. Each loop has a
    4 x 1.8 mm tunnel, 2 mm side walls, 1.6 mm roof and 1.85 mm remaining floor underneath.
    The roof ends at z5.25, 0.5 mm below the nominal cell. Four-millimetre ramps expose the
    tunnel mouths for threading before inserting the battery. The cell's position is unchanged.
    The two ties retain the battery even while the base is open; cut them before removing it.
  - The user removed the two loose battery bridges on 2026-09-25. Two cable ties now
    run directly around the shrink-wrapped pack and through the existing floor loops.
    Their envelope includes both the cylindrical cell and the measured full-length
    side BMS (approximately 20 mm wide, 4 mm thick). The model has 0.05 mm nominal
    fit clearance, not an engineered pressure-free space over the electronics.
    Tighten gently by hand; no rigid printed spacer or new substitute part is fitted.
    Removing the head does not release the battery; cut and replace the ties for service.
  - Existing base geometry and the two shallow head-floor reliefs are retained so the
    current printed housing stays compatible. Their parameters are now independent
    of the removed bridge dimensions (`bat_tie_head_clearance`). The bridge print part,
    assembly body, plate instances, STL and viewer item are removed.
  - Battery checks retain the floor-rooted axial stop, closed strap loops, actual
    tunnels and threading ramps, anchor material, strap/pack capture and clear service
    paths. The direct straps no longer have the earlier bridge-to-BMS load isolation.
    Geometric capture does not prove clamp force, wrap integrity or pressure on the BMS.
  - The USB front stop is a **central removable keeper on the ballast lid**, 4 mm wide at x104..108.
    Its stem spans y53.2..57.22; the arm ends at y59.42, 0.2 mm before the PCB, and begins at z42.75,
    below the actual underside at z42.85. A separate 0.1 mm thin central edge probe prevents the
    component envelope from faking insertion-stop contact. A 1 mm upper return now catches the
    module when it is lifted or tilted by the USB cable. Its roof is 1.6 mm thick with a 1.25:1
    underside slope and 0.2 mm nominal clearance at the front upper edge. The 4.3 mm module
    height includes components, so an actual bare PCB bearing patch is not established by this
    envelope. Both lateral wire routes remain open: x101.5..103.5
    and x108.5..110.5, checked at the end and above/below the board with the lid installed.
    Two low triangular cheeks reinforce its root (user, 2026-09-25). They span
    x102..104.2 and x107.8..110, overlap the stem by 0.2 mm and grow 8 mm above
    the z29 lid. Their feet run from y53.2 to y61.2; their top edges slope down
    towards the rear. The wider and longer attachment supports bending from USB
    insertion while the upper 4 mm keeper and both cable exits remain unchanged.
    They print as part of the lid without supports and also appear in the fit coupon.
  - Two narrow 2 mm side-guide gussets carry the USB channel from the rear wall, at
    x98.87..100.87 and x111.13..113.13. The old broad inner right gusset is removed; the rear
    seat now bridges 10.26 mm for the user's measured 10.06 mm PCB. The **lid has no USB slots or seat recess**. Both support undersides
    follow z = 104 - y, ending at z33 at the inner rear wall y71: 4 mm above the continuous z29 lid.
    The guides start at y58.72, with underside z45.28 and top z47.35; their lead is 0.9 mm ahead
    of the PCB. `check_usb_support()` measures the actual slopes, empty space below, complete guide
    material and lid clearance. The previous low gussets and slotted-lid lift/roll route are superseded.
  - Fit the USB board before the lid. With the head and loaded lid removed, the checked bare-base
    route moves it 20 mm forwards into the bay, then 30 mm upwards; reverse that route for insertion.
    The continuous swept-mesh check reaches a position fully above the base. A base printed with
    the former fixed front stop still traps the receptacle; replacing its lid alone cannot fix that.
    Keep real wires loose enough for servicing.
  - `usbc_fit_base` and `usbc_fit_lid` are quantity-zero crops of the real parts on the separate
    `fumex_usb_fit.3mf` plate. The base crop includes the complete trough step, avoiding a thin cut
    remnant. Two fixture-only pads supplement the retained right screw-post seat and hold the test lid at
    z26. Physical board, receptacle and wire fit still require this test print.
  - Remove the head, battery, rocker switch and both lid screws before servicing the loaded lid;
    retain the charge module, heatsink and tie as one moving group. The complete route is straight
    translations: +Z3.4, -Y4, +Z3, -Y16, +X0.2, then +Z60 mm. The targeted mesh check samples
    392 poses with at least 0.200 mm clearance; the final upward segment has 0.2703 mm minimum.
    The switch can first leave +X35 mm with the battery and lid still fitted (351 checked poses).
    The historical 11.4 mm lift / 5.9-degree roll belongs to the earlier side-stop/slotted-lid revision.
    Use the matching-source verification report for release results. Remove the loaded lid before
    withdrawing the PWM controller. Wiring and finger access are not represented by these paths.
- The housing bends: `base` stands upright, `head` leans `tilt` = 15° forward above it, so the intake looks down at the work (user: "erst senkrecht nach oben, und dann nach vorne im Winkel"). Head modules are written in an untilted frame and placed by `head_at()`; `print_project.py` mirrors that transform in `_tilt()` for the probes.
- The base has a nominal 145 × 74 footprint; its upper loft meets the projected head outline at the joint, so the head's floor closes the electronics bay without an extra cover. The joint is one flat plane cut by `joint_halfspace()`. The 145 mm width was originally set by the former Ø10 magnet pockets. The screw conversion retains that outline and the four corner axes.
- **The fan is screwed to the back cover, not to the head** (user asked 2026-09-23: "kann man den luefter
  nich mit der rueckwand verschrauben?"). Four `fan_post_d` = 8 spacer posts on the cover bridge the plenum
  to the fan's back face and hold its inserts; the M3 x 30 go in from the *front* of the fan. Fan and cover
  are screwed together on the bench, where that face is reachable, and the pair goes into the head as one -
  which is why `ALLOWED_OVERLAPS` lets `driver_fan` pass through the head, the cassette and the mat.
  The cover prints outer-face-down, so the posts grow straight up and their insert pockets open at the top.
  The exhaust grid gets a solid pad of `fan_post_d + 6` under each post, and the cover's clip cube now
  reaches forward to `head_y[3]` or the posts get cut off at the lip.
  - The fan bears on the end face of the filter tube: `mat_stop()` runs the rear lip on to `head_y[2]`, so
    the tube ends as a ring the frame sits on. No flat plate, no overhang - the ring's end face points up
    in print.
  - What this replaced: four 45 degree corner gussets in the chamber, carrying the inserts in the head. The
    fan's mounting holes are 52.5 mm from the axis, inside the 60.75 mm bore, so a boss for them has to
    stand in the filter chamber, and printed intake-face-down it has to grow from the intake face at 45
    degrees - 38.9 mm legs over 27.5 mm of depth, no smaller (21.6 would have held the insert). They
    pressed 6.6 cm3 out of the mat. Removing those gussets reduced `mat_squashed_percent`
    to 0.0; the current front screw seats intentionally raise it to 0.11%, confined to
    the local flexible contacts described below.
- The cassette stands 4 mm proud of the intake face, with a 1.2 mm final-contour
  bevel and 2.8 mm of straight rim. Four Ø3.4 mm through-holes replace its enclosed
  magnet cavities. M3 x 8 button heads sit fully in flat Ø6.4 x 1.9 mm counterbores,
  leaving 2.1 mm of bearing material and the head tops 0.25 mm below the cassette face.
  There are no enclosing collars. The earlier 4.5 mm and 5.6 mm magnetic cassette
  versions are historical. The head intake face stays 5.6 mm thick to preserve its
  internal component positions and compatibility with the current back cover.
- `head_outline(inset, square_bottom)`: the head shell keeps the square bottom corners
  so its side walls meet the base rim without a step; `head_back` passes false to keep
  its rounded outline. The cassette no longer derives its perimeter by clipping an
  inset head profile. Its final 138 x 143 mm outline is constructed directly with
  tangent R6 arcs at all four corners, matching the head's upper radius. Only then is
  its 1.2 mm front bevel applied, giving R4.8 visible-face corners. The former width
  clipping erased the lower arcs and truncated the upper R5 arcs, leaving a roughly
  60-degree tangent break; that construction is superseded (user, 2026-09-29).
  Neither cover nor cassette lands on the base rim: the head carries the silhouette
  behind the cover, and the cassette lies on the intake face.
- The joint plane rises 15 degrees to the back and therefore meets the vertical back face of the base at 75
  degrees: an acute edge across the full width, right where the back cover lands (user, 2026-09-23: "die
  scharfe kante weg wo die rueckwand aufliegt"). It is cut at 45 degrees to the joint plane, placed with
  `head_at()` so it mirrors the chamfer on the cover's lower edge; both sit behind `head_y[4]`, where the rim
  carries no head wall. The cover's lower edge had only 0.9 mm of the rim chamfer left on it, because the
  joint plane cuts that chamfer off `cover_gap` above the outline's own bottom edge; now it is the full 1.2.
- **Filter cassette: four M3 x 8 screws and four Ruthex RX-M3x5.7 inserts**
  replace the magnets (user, 2026-09-29, insufficient stability of the magnetic closure).
  Axes remain at untilted-head x10/135 and z58/183, normal to the intake face. Head
  bosses are Ø8.4 x 9 mm with front-open Ø4 x 7 mm pockets and 2 mm blind ends.
  Cassette holes are Ø3.4 mm. The 4 mm cassette has Ø6.4 x 1.9 mm flat counterbores,
  with the bearing plane at local y-2.1; its 1.65 mm button heads lie 0.25 mm below the face.
  The 8 mm screws pass through 2.1 mm of bearing material and enter 5.9 mm into the
  7 mm pockets, leaving 1.1 mm reserve. There are no enclosed
  magnet cavities, magnet bodies or insertion pauses (`PAUSES = {}`).
  The matching head and cassette must both be reprinted; this is not a retrofit to
  magnetic printed parts. Base, back cover and other current parts keep their interfaces.
  The head is now grey like the cassette. Production plates and coating groups stay
  unchanged. Two 45° side finger scoops help lift the cassette after removing its screws;
  the intake lip remains continuous and the redundant half-round notches remain removed.
- **The chamber has a rear lip too** (`mat_stop()`, user asked 2026-09-23 what stops the mat falling into the
  fan - nothing did). The mat's back face rested on the four gusset corners only, 7.8 % of it, with 10.5 mm
  of clear air to the fan frame, while the fan pulls it that way with about 1 N at 69 Pa. The lip closes the
  bore from `chamber_sq` to `open_sq` on a flank of `mat_stop_rise` = 1.5 mm of depth per mm inwards - at 45
  degrees `analyze.py overhangs` counts it, the head prints intake-face-down and the lip hangs inwards. It
  merges into the chamber tube so it grows out of the bore wall instead of starting as a knife edge.
  `checks()` reports `mat_free_travel_mm` = 1.62 and asserts it stays under a quarter of the way to the fan.
  - Historical finding before adding the support cross: this rigid-envelope check did not prove that the flexible mat could not reach the rotor. A direct
    mesh measurement on source SHA `544894c9fc4dc5176798e87bd9ad6000a1cbd028eab20a550ffad9b17326cd1d`
    (2026-09-23) gives 10.50 mm from the nominal mat rear face to the fan frame's front plane; first rear-lip
    contact after about 1.76 mm of rigid translation leaves 8.74 mm. The simple 1.62 mm formula is an
    approximation to the actual hull/tessellation. At that revision the central 117 x 117 mm opening had
    no backing grid. The current support cross below supersedes that geometric finding; bowing and loose
    fibres remain unmodelled, and `fan_visual()` is not a measured blade envelope.
- **A separate reinforced support cross backs the mat** (`filter_support`, user, 2026-09-23). It is the eighth
  print type, making eleven physical printed pieces including the four feet: grey PETG, 123 x 123 x 9.8 mm,
  printed with the mat-facing side flat on the bed and the four end posts upright, at 100% infill.
  Integrating the cross into the intake-face-down head would create long unsupported bridges.
  - `mat_support` defines 4 mm wide, 5 mm deep bars (formerly 2.4 x 3.2). Four concave R4 corners
    round the centre; a 6 mm smoothstep flare meets each 8 mm end pad tangentially. Both cross faces
    retain 0.4 mm chamfers. The front is y23.1, 0.5 mm behind the nominal mat rear face at y22.6;
    the back is y28.1, 5 mm before the fan frame at y33.1. With 0.2 mm axial play, the worst nominal
    clearances are 0.3 mm to the mat and 4.8 mm to the fan. The checker tests both reserves.
  - Actual projected obstruction is 981.941 mm² of the rounded throat's 13,681.093 mm², or 7.177%,
    leaving 12,699.152 mm² open. The strengthened profile intentionally raises the area gate from
    5% to 8%. This is an area measurement, not a pressure-drop prediction.
  - The nominal pads remain 8 mm across and 3 mm long radially. Rear-open head pockets start at
    y22.9, extend radially 58.3..61.7 and remain 8.4 mm wide; printed heads are compatible.
    The cross span is 123 mm, retaining the front bearing and the y32.9 rear tips. The head
    and fan stops still bound axial travel to 0.2 mm each way, but do not themselves clamp.
  - **Fan-independent spring grip (user, 2026-09-28):** the former loose cross did not grip the
    open head. Each pad now has two 2.1 mm tangentially thick cheeks, a 3.8 mm central slot
    and a 0.9 mm radial relief separating it from the 5 mm cross bar. A full 1.6 mm front
    foot joins both cheeks to the arm. Slot-root radii are 0.6 mm centrally and 0.45 mm radially.
    The eight side ribs reach a free width of 8.7 mm at y31.9..32.1, giving 0.15 mm nominal
    compression per cheek in the unchanged sockets. Their 1.4 mm leading and 0.8 mm trailing
    ramps allow insertion and removal. These are friction springs, not undercut snap hooks.
  - Insert from the rear before the fan/cover, mat-facing cross forwards. Align all four pads
    and press evenly; verify grip with the open head turned over. Pull evenly to remove after
    taking the fan/cover off. The fan remains a secondary rear stop; its real contact patches
    at radial positions 58.5..60 mm are still unmeasured. Ordinary mat changes are from the front.
    Nominal interference and geometric deformation checks do not prove friction force or PETG creep.
    Only the new cross needs printing for this grip; no change to the existing head sockets is needed.
  - The cross reduces the unsupported mat span but its PETG bars and the mat can still bend. No
    physical strength, long-term creep, loose-fibre or maximum-speed rubbing test has been performed.
    Do not turn the nominal 5 mm central-bar/frame gap into a guarantee of rotor clearance.
- The mat is held by the intake lip (opening 117 in a 121.5 chamber, 2.25 mm per side). It is pressed in and pulled out past that lip — a rigid-body path check cannot show this, so `filter_out` is not a checked path but a documented limitation.
- **Head screws: four M3 x 8, all straight down into the base in the same direction**
  (user, 2026-09-25). In the untilted head frame every axis is (0,0,-1), normal to the
  joint plane; the shared housing tilt is unchanged. Front insert entries are
  (25.5,6.5,60) and (119.5,6.5,60), behind the front wall. Rear entries remain
  (25,66,48) and (131,66,48). All seats bear directly against the base. Front seats have 1.6 mm material,
  6.4 mm screw penetration and 0.6 mm pocket reserve; rear seats retain 2.3 mm
  material, 5.7 mm penetration and 1.3 mm reserve in the 7 mm insert pockets.
  This supersedes the previous 40-degree outward front axes and M3 x 16 screws.
  - Front base bosses retain Ø9.2 and Ø4 x 7 mm Ruthex pockets. The original compact
    cylinder/root profile is swept 6 mm farther down, with its new underside trimmed
    at world z = 31.2 + 1.1 y for support-free printing and PWM clearance. The deeper
    narrow wall attachment has no broad pedestal feet; the slope shortens the extension
    locally, so this is not a full extra 6 mm of cylinder everywhere.
    Its additional wall link is clipped to the actual curved `base_joint_envelope()`
    so it cannot project beyond the front face. Only the link is clipped; the working
    post and downward sweep retain their complete geometry.
    The original head clearance template is unchanged; its 15 mm downward sweep
    encloses the extension. Rear bosses remain Ø10 x 9 mm with existing cover notches.
  - The head has short Ø12.2 mm caps from local z59.5 to z62.3,
    connected to the lower filter tube. A Ø9.7 mm guide opening below the insert face
    leaves 1.25 mm radial material around each boss and 0.25 mm guide clearance.
    The front bearing plane is z61.6, with a flat Ø6.4 x 0.7 mm counterbore: the
    same shallow recess depth as at the rear (user, 2026-09-25). The 1.65 mm
    button heads remain 0.95 mm proud of the caps. The cap edges retain the
    0.3 mm bevel. The intake cutter excludes the cap bodies so their pocket rims
    stay complete, without a thin remnant where the two cuts would meet. Independent
    mesh probes check pocket depth, complete bearing/rim material, and clearance
    above the caps.
    Two rectangular reliefs below local z57.5 open the boss-root windows through
    the front, removing accidental 0.3–1.2 mm skins. Above the reliefs, the front
    wall retains at least 1.254 mm and the filter-tube floor remains closed.
  - The nominal mat begins at z60.5. Its user-authorised local bending is bounded to
    the two front fastener regions: 1.8 mm over the caps and 2.75 mm over the partly recessed
    screw heads. The export checks the actual overlap volume, depth and location;
    arbitrary head/mat collisions remain errors. This is no force or stiffness model.
  - Front fastening uses the Wera 8001 A / Zyklop Mini 1 from Tool-Check PLUS 1
    (05049055001), with a 25 mm TX10 bit directly in the ratchet. Wera specifies 87 mm
    overall length and 6-degree return angle. The head is assumed Ø22 x 14 mm, handle
    14 mm wide, and bit engagement 2 mm; these dimensions are not measured. The checked
    envelope includes the complete bit, front entry, seating motion and ±6-degree swing.
    Remove cassette and mat for front fastening. Rear screws require the fan/cover off.
  - `head_off` moves the head and support cross along the tilted normal after
    the cassette, mat, fan/cover and screws are removed; battery ties remain.
  - PWM service first pitches the released PCB to 20 degrees, withdraws it 7.9 mm,
    then pitches it to 35 degrees before the remaining lift and sideways extraction.
    This staged route clears the raised front boss; pitching directly to 35 degrees
    at the previous position does not. The full actual-mesh route includes the PCB,
    potentiometer and tab, with separate removal checks for both PCB screws and knob.
- **Driver access is checked in the applicable assembly stage.** Most screws use a
  straight Torx-bit/holder envelope. Front head screws use the conservative ratchet
  above. Assembly-stage exclusions only cover parts removed for that operation; fixed
  housing and electronics remain obstacles. Tool geometry is not a physical-fit test.
- **The ballast lid now uses exactly two M3 x 8 screws and two Ruthex RX-M3x5.7 inserts** (user,
  2026-09-23). The Ø10 posts stand at (x, y) = (10, 63) and (117, 56.8), with Ø4 x 7 mm insert pockets
  opening upwards. This replaces all four plastic-forming screws and their core holes. With the
  3 mm lid and 1.2 mm head pockets, nominal thread reach is 6.2 mm. Total current hardware is 22 inserts,
  18 M3 x 8 (including four cassette screws) and four M3 x 30 fan screws. The right post moved inwards and forwards on 2026-09-24 so
  the screwdriver clears the head-mount bosses; the intermediate (130,63) position did not.
  Earlier positions at x30/115, 45/90, 12/40 and (135,63), including the G3 rear-row adjustment
  to y66.2, are historical. The head vent slots remain 14 mm long.
- `head_outline()` is rounded `corner_r` = 6 at the top and `corner_rb` = **0.5** at the two corners on the
  joint plane, and `joint_neck()` carries that arc on into the base rim, so head and base meet without a
  step. The cutter's top corners are an arc of `neck_r` whose centres sit `corner_rb` in from the housing
  edge and `neck_r` below the joint plane: at the joint both parts are exactly as wide and both arcs are
  tangent to the horizontal, so the rounding continues through the edge instead of breaking into a chamfer.
  Do not build it by mirroring `head_outline()` - widening that contour moves its bottom edge with it and
  the arc lands half a millimetre off, which is exactly what the user saw first.
  - 0.5, not 2: at 2 the elevation arc and the 3.5 arc of the vertical edge met in the same corner together
    with the chamfers around the joint, and the pile of different radii looked bad (user, 2026-09-23:
    "diese rundungen hinten sehen einfach beschissen aus"). At 0.5 the joint is a straight parting line
    running into the rounded vertical edge, and that edge carries the corner on its own.
  - The radius at the joint is limited by the wall, and this was built and measured before it was dropped.
    At `corner_r` 6 the neck removes the whole 3 mm side wall of the base over its top 3 mm - the export
    came back with 7 bodies - and the head's bottom face would be 133 mm wide against a 139 mm bay opening,
    so it would bear on the front and back rim only. R6 needs side walls of 7 mm over the top 12 mm and the
    cell moved 4 mm right. The user chose R2 instead (2026-09-23).
  - Two details in `joint_neck()` are about the export, not the shape: the run-out ends `body_w + 2` wide so
    it is not tangent to the outer face of the side wall, and the cut reaches 1 mm above the joint plane so
    its top face is not coplanar with the one `joint_halfspace()` leaves. Either coincidence left a
    zero-volume four-triangle shell and a second body in the export.
- **The four vertical edges: `plan_r` = 3.5, shared.** `plan_prism()` is `base_outline()` extruded over the
  head's height and intersected with the head, the back cover and the cassette, so the head's footprint is
  the base's and the vertical edges run through the joint without a step. Before this the head was a sharp
  145 x 74 rectangle in plan against the base's R6 and stood 2.5 mm proud at all four corners (user,
  2026-09-23: "die rundungen sind immer noch falsch").
  - Historical constraint before the screw conversion: 3.5 was capped by the magnet pockets
    in the intake face. The pocket had to clear the
    rounded plan corner by 1.2 mm and the intake opening by 1.2 mm, which at R6 leaves an empty window
    (inset >= 12.35 and <= 10.39). At 3.5 the window is 9.85 to 10.39 and `mag_off` 62.5 puts the magnets
    at inset 10: 1.3 mm to the corner, 1.8 mm to the opening.
  - The cassette stands `cass_t` in front of the footprint, so `cass_prism()` runs the prism on forward at
    the width the footprint has at y = 0 rather than rounding a second time in the wrong place.
- The back cover runs the full height of the head (user, 2026-09-22); the head floor stops at its inner face. Its lower edge keeps `cover_gap` = 0.3 mm off the joint plane, otherwise the two coplanar faces grind along each other on the way off and `cover_off` fails on facet-level overlap. Four screws, not six (user).
- Feet: four TPU pads, one M3 × 8 each plus a Ø3 peg against turning. A keying pocket in the bottom face was 275 mm² of flat overhang per foot, so it went.
- Tipping: `checks()` computes the centre of mass from mesh volumes and part masses and requires ≥ 15 mm to every foot edge. Use the current verification report for results. An early layout gave 30.6 mm at the front, 23.3°, 1.02 kg (13.8° when this started).
  - Feet fully under the housing (user, 2026-09-22: pads sticking out past the rounded corners looked wrong), x 16/129, front pair at y = 8 so the pads end flush with the front face. Tipping edge y = 0.
  - Historical first trough behind the cell: x 3–96, y 53–71, rim 35, 39 cm³ and about 184 g of loose iron at an assumed 4.7 g/cm³ (60 % packing). The later full-width trough supersedes it. The cell moved forward to make room (user: "du kannst die batterie einfach nach vorne rücken und hinten ne größere wanne machen"). `ballast_env()` remains the trough volume minus `base()` itself, so foot boss, posts and rounded corners are cut out of it and the reported mass is what really fits.
  - Historical battery-position constraint: the earlier tilted front screw-boss run-outs reached the cell shoulder; y35 cleared them while y34 overlapped by 0.14 mm³. The current raised front bosses replace those earlier run-outs; the battery position remains unchanged.
  - Historical four-post layout: each Ø10 corner post lay 3.5 mm off the adjacent walls; at Ø8 it left a sealed sliver void and a second exported body. `ball_rim` = 0.4 kept the walls below the posts to avoid coplanar unions. The current lid instead uses the two insert posts listed above.
  - The 2026-09-22 choice of plastic-forming screws and Ø2.5 core holes was superseded by the user's two-screw, heat-set-insert mounting on 2026-09-23.
  - The lid has a plain top without the former Ø16 mm finger dish (removed at the user's request,
    2026-09-23). The axial battery stop is rooted in the base; there is no lid tongue. The head's
    shoulder holders release the cell when the head is removed, preserving `battery_out`.
    The loaded lid uses the straight staged route listed above with the switch removed; use the
    matching-source verification report rather than the former slotted-lid route.
  - The free space in front of the cell (about 50 cm³) is the wrong side of the centre of mass and is deliberately left empty.
- Charge module upright on the ballast lid, directly below the plenum slots (user, 2026-09-23: both sides of the board should get air; subsequently, "Wie LEO: Seite mit Kühlkörper frei"). Components face forwards, heatsink backwards. A single holder and cable tie retain only the cool OUT end; the heatsink end stays free. See Electrics below for dimensions and physical-fit limits. The earlier pair of edge holders, flat tray and bay-floor brackets are no longer built.
  - **The air route starts in the plenum:** the five slots and rear-open cable notch in the head floor connect the fan's filtered outlet side to the component and heatsink passages, which lead to the back-wall slots. The surrounding 5.75 mm channel between filter tube and shell also remains open to the plenum. Geometric corridors are checked; flow rate, natural convection and cooling performance are not measured.
  - The vent is a row of five slots beside the wider rear-open cable notch: printed intake-face-down the head floor is a vertical wall, and a single 38 mm opening left a 113 mm² flat bridge at its far edge.
  - Ventilation slots in the back wall (user: slots, not honeycomb, and not staggered) sit above the ballast
    lid - an assert keeps them there, below it they would let the offcuts out. Aligned they export clean
    here (12 slots, 2 mm wide, 5 mm pitch); the collinear-corner trap that hit the old slot rows did not
    reappear, so `vent[4]` is 0. If it ever does come back, stagger before reaching for anything else.
- Ballast trough over the full width, lower, with the USB-C socket above it (user, 2026-09-22): nominal x 3–142, y 53–71, rim 26. Its initial 44.5 cm³ / 209 g estimate and 24.5° tip angle at 1.04 kg predate later cut-outs, posts and tipping corrections; use current exports for the usable volume and stability results.
  - The final switch-side contour and relocated right insert post give 40.29766 cm³ in the targeted
    mesh, about 189.4 g of loose iron at the assumed 4.7 g/cm³. Full-export mass and stability values
    belong in the matching-source verification report.
  - The USB-C channel remains at z45 on two narrow 45-degree side-guide gussets from the back wall.
    Their underside is z33 at y71, 4 mm above the unslotted lid, and the guides begin at y58.72.
    The rear seat spans 10.26 mm between them. The broad inner right gusset and earlier low gussets
    that filled rear-open lid slots are superseded.
  - The removable central 4 mm L-stop catches the lower PCB edge; two lateral wire corridors stay
    free. `usbc_in` remains required with the lid fitted. Neither guide may close these corridors or
    restore the former fixed front stop. The two back-wall cable-tie loops remain removed.
  - The final switch recess uses `ball_step=[118.5,64]`, with its diagonal from (128,64) to
    (142,78) clipped by the rear wall. The right screw ear and Ø10 post now centre on (117,56.8),
    leaving the screw and insert-tool approach clear of the head-mount bosses. The left stays at
    (10,63). Keep trough and lid contours matched; enlarging only the lid would reopen the ballast
    escape path. The targeted top-cover residual is 0.000480 mm² within the unchanged seam probe;
    final assembly clearances belong in the matching-source verification report.
  - Early switch positions at y 37 / z 34 were superseded. The current upright switch centre is
    y 50 / z 26, behind the PWM board; its body depth remains an inherited hardware assumption.
  - `lid_off` and `check_loaded_lid_removal()` use the loaded group (`ball_lid`, `chg_module`,
    `chg_sink`, `chg_tie`) after removing the head, battery, switch and lid screws. The unslotted lid
    follows +Z3.4/-Y4/+Z3/-Y16/+X0.2/+Z60 mm; consult the matching-source report for release results.
- The switch well flanks rise 1.25 mm per mm instead of 1.0: at exactly 45° `analyze.py overhangs` counted them.
- The rocker switch stands upright in the right wall (long side vertical): the base prints bottom down, so its panel cut-out is a sideways hole and the bridge over it is 12.2 mm instead of 19.2 mm.
- **Both LED holders sit behind closed 1.8 mm front skins** (user, 2026-09-24: move them 1 mm
  deeper because the internal holes showed through the printed front). This supersedes the former
  0.8 mm LEO-AC1-style skins. `led_cut()` makes two Ø3.2 mm blind bores at (x,z) = (90,21) and (78,21),
  open only to the bay, from y1.8 to the rear of their Ø7 bosses. The second holder was requested on
  2026-09-23; its electrical function is unspecified.
  The boss rear face is y6.8; the LED flange rests there, and the nominal lens starts at y2.1,
  leaving 0.3 mm before the skin. Insert and glue the LED from inside. This replaces the former
  through-hole and the claim that the front must be open because black PETG cannot transmit light.
  Visibility with the chosen filament still needs a physical check.
  - The pockets and flange seats move together by +Y1 mm, preserving the physical LED envelope and
    lens clearance. The bosses remain rooted at the inside front wall. The former 0.8 mm optical
    thickness exception is retired: the new skins exceed the normal 1.2 mm threshold and the current
    checker lists no expected thin-wall findings. Light transmission still needs a physical check.

## Electrics — two things that belong in the README and in the build

1. **0.32 A against 0.33 A.** The LFUPSMA charge/boost module is specified for 0–0.32 A at 12 V, the P12 Pro draws 0.33 A at full speed. The top of the knob range is therefore at the module's limit: it gets warm and starting at 100 % may brown out. Start slow, then turn up.
2. **Charger heat — upright board with open air passages.** The CN3058E is a linear charger: at 1 A
   from 5 V it turns about 1.6 W into heat while charging. The earlier closed-bay, external-heatsink and
   flat-tray arrangements have been replaced. The user asked to turn the board so air can reach both
   its components and its heatsink; the current holder is on the **ballast lid**, under the six plenum slots.

   - The measured 32.2 × 11 × 1 mm PCB now spans x 53.9–86.1, y 59.5–60.5 and z 32.2–43.2. Its
     components face forwards to y 56.8. The 14 × 14 × 6 mm heatsink and 1 mm pad face backwards,
     spanning x 76.6–90.6, y 60.5–67.5 and z 30.7–44.7. The heatsink clears the lid surface by 1.7 mm.
   - A single holder supports the cool OUT end at its end, bottom and rear. The former holder at the
     heatsink end has been removed: PETG ends 4.7 mm before the heatsink. This supersedes the former
     two-guide design and its 0.2 mm pad-to-right-guide clearance. There is no support against the hot end.
     The 4 mm wide central rear bearing spans 9–18 mm from OUT; the pedestal stays 1.5 mm behind the
     jumper region. The lower-edge seat spans 3–11 mm from OUT, keeping both OUT wire corners open.
   - One 2.5 x 1.2 mm cable tie passes through the holder and around the PCB in the LEO-AC1 band
     11.25–13.75 mm from the OUT end. The shared layout was read from photos with approximately ±0.3 mm
     uncertainty: OUT wire pads occupy both end corners over 0–2.8 mm, solder jumpers 6.8–8.2 mm,
     BAT pads 17–22 mm and the metal thermal pad 21.8–29.5 mm. The tie band crosses the ends of the
     inductor and diode; verify actual component, solder and wire clearances before tightening. The
     component envelope is not a detailed model of the real board or its soldered wiring. The tie
     envelope omits its buckle and elastic tightening; keep the real buckle clear of the hot end,
     wiring, air passages and lid service path.
   - Cut and replace the tie to remove the board. `chg_off` must include the actual one-sided holder
     and evaluate the board/heatsink path after releasing the tie; rigid envelopes cannot prove tie
     strength or clamping pressure. `lid_off` and `check_loaded_lid_removal()` move the loaded lid
     with the board attached through the straight staged route above. Leave wire slack for service
     and remove the head, battery, rocker switch and both lid screws first.
   - `check_charger_air()` checks free volumes in front of the components and behind the heatsink, anchored
     to the actual mesh faces. Continuous Ø1.2 mm probe corridors connect each space through an existing
     head-floor slot to the plenum and through a rear vent to the outside. The component-side route passes
     round the board's left end; the heatsink route exits directly behind it. These are geometric access
     checks, **not CFD, an airflow measurement or proof of adequate cooling**. Check closed-housing charging
     temperatures with the actual wiring, both with the fan running and stopped.
   - The two lid screws are at (10,63) and (117,56.8), outside the holder. Earlier posts at x12/40,
     (135,63), the rejected (130,63) and the former two-guide lid height of 12.4 mm are historical;
     use the current exported bounding box for the final print size.

   Still available if it is not enough: swapping the ISET resistor (marked 122, 1.2 kΩ) for 2.4 kΩ halves the charge current to 0.5 A and the heat to about 0.85 W, at 12–13 h for a full charge. The user chose the heatsink route alone for now.

## Support-free printability (reviewed 2026-09-23 on the user's request)

The current design has eight production print types and eleven physical printed pieces, plus two
optional USB test types, all intended to print without supports. The support cross lies flat and its end posts grow upwards; its rear-open head
pockets add no chamber-wide bridge. The following completed checks predate the support-cross addition,
two-insert lid, OUT-end holder, USB support ribs, wider switch recess and closed LED window:

- `analyze.py islands`, `overhangs` (100 mm²), `fins` and `thickness` are all CLEAN on all seven parts.
- `analyze.py overhangs --min-area 5` lists 27 small downward faces, all of them understood: four Ø3.3 foot peg holes and four Ø4 insert pockets in the bay floor (circular bridges, 6–10 mm²), the six vent slots in the head floor (10.8 mm² each), the two finger scoops in the intake face (45 mm² flat cone ends 2 mm above the bed), the USB-C channel floor (85 mm², a 5.8 mm ledge off the back wall) and the two cable tie loops (28 mm² each, 6 mm off the back wall). None is a floating island; every one of them grows out of a wall or bridges a hole under 15 mm.
- Before the support-cross addition, the Bambu CLI sliced all seven parts and all four plates without support. The individual `base` and `head` slices each report "floating cantilever", also present before the G2/G3 changes. The base candidates are the USB-C channel ledge and the tie loops. The warning locations have not been conclusively isolated; keep these warnings visible in the report and inspect the small bridges on the first print.
- Historical decision: gussets under the USB-C floor and former tie loops would eat the lid's lift clearance. A later revision removed the loops and used floor ribs, then low gussets through rear-open lid slots with a 7.85 mm seat bridge. That support layout is also superseded by the elevated narrow guides and unslotted lid described above.
- At the enclosed-magnet revision, the tall bridges were the rocker switch panel cut-out (12.2 mm, which is why the switch stands upright) and the magnet cavities (then Ø10.3). The screw conversion removes the latter cavities and their insertion pauses.

## Audit of 2026-09-23 (`docs/audit-2026-09-23.md`)

An external audit of commit `a90c581`. What it found and what happened to it:

| ID | Finding | Status |
|---|---|---|
| A1 | The switch notch in the ballast lid opened the trough into the electronics, 9 x 3.5 mm | initially fixed by `ball_switch_fill()`; the current enlarged contoured recess keeps the trough wall and lid outline matched around the switch |
| A2 | The USB-C board could be pushed 15 mm into the bay by a cable | the fixed end wall and later side stop are superseded by a removable central lid L; it catches the PCB edge while two lateral wire routes remain open; `usbc_in` remains required |
| A3 | Assembly step named the wrong fan direction, and "fleece side first" contradicts the parts list | fixed in README: blowing towards the cover, and the mat's end position is named instead of the order |
| A4 | The tab over the charge module made both straight insertion and straight removal impossible; `chg_off` did not include the lid | tab removed; the current OUT-end holder uses a cable tie that is cut for removal, and `chg_off` must include `ball_lid` after cutting the tie |
| A5 | M3 x 12 reached 0.9 mm past the core hole and the head bore on a 1.1 mm ring | initial fix: 1.2 mm counterbore and M3 x 10 plastic screws; current mounting supersedes those screws with two M3 x 8 into Ø4 x 7 mm heat-set-insert pockets, preserving 1.8 mm under the heads |
| G1 | The cassette's side bevel was cut off by the plan prism - 4.5 mm of square wall on both long sides | fixed: `cass_face()` is the finished contour and the bevel comes off THAT. `cass_c` 2.0 -> 1.2, because the bevel now starts at `plan_r` and has to clear the magnet pockets |
| S1 | Tip angle ignored the foot height and used the full pad outline | fixed: lever arm from the sole, contact patch inset by `foot_chamfer`. 23.5 -> 21.4 degrees |
| V1 | `cover_off` left the fan behind although it is bolted to the cover; `filter/head` exception was left over from the gussets | fixed: `cover_off` and `fan_out` move fan and screws with the cover; exception dropped, mat displacement is 0.0 anyway |
| D1 | README and AGENTS carried stale numbers | fixed: part sizes, insert count, ballast volume, masses, tip angle, footprint |
| G2 | Intersecting R3.5 plan and R6 elevation arcs left a 38–46 degree crease | fixed: local compact C1 blends at the four upper corners; unchanged radii and magnet positions, 1.21 mm radial pocket skin verified |
| G3 | The tilted footprint left a 1.26 mm base lip front and back | fixed: outer and inner upper-base contours loft onto the projected head footprint over 8 mm; the intentional 15 degree housing bend remains |

### G2/G3 implementation and regression checks

- `top_corner_blends()` removes about 1.8 mm³ from each of the head and back cover. For the plan/elevation circle insets `a,b`, the old boundary was `max(a,b)`. The new boundary tends to `sqrt(a*a+b*b)` where both contribute, with a smooth cutoff from a 5% to 15% secondary contribution. The analytic patch is C1; the STL is its faceted approximation. Intentional rim bevels remain sharp.
- The 28-step corner grid, compact cutoff and 0.001 mm CSG overlap avoid float32 zero-volume shells at tangencies. Do not replace this with an unregularized norm without validating both exported meshes. No mesh repair is applied.
- `base_joint_envelope()` uses 32 loft intervals over 8 mm measured normal to the joint. The outer contour moves inward by `body_d/2 * (1-cos(tilt))` at front and back. It joins the original vertical wall smoothly below the joint and meets the tilted head in position; it deliberately does not erase the 15 degree housing bend.
- The inner transition starts `wall*sin(tilt)` earlier, with up to 0.15 mm extra wall reserve. Front-wall normal samples stay at 2.999 mm or more (numerical tolerance around nominal 3 mm). The loft vertex count is fixed from the nominal inset, even when its intermediate inner radius changes.
- At the G3 revision, the rear ballast-lid screws and posts moved from y 67.5 to 66.2, preserving access for the existing 6.35 mm driver and leaving a 1.3 mm web to adjacent head pockets. That four-post pattern was subsequently replaced by insert posts at (10,63)/(135,63). The current right post is at (117,56.8); base, lid and screw bodies continue to derive positions from `ball_posts()`.
- The base uses the export tool's existing CGAL fallback; the resulting binary STL is closed, one body and has zero degenerate faces. Do not force an invalid fast-backend result or repair it after export.
- At the magnetic revision, `check_top_corners()` rejected the previous crease in all four outer corner regions and probed a complete 1.21 mm radial material ring around each head magnet pocket. The screw conversion keeps the corner-surface checks and replaces the obsolete magnet ring probes with cassette insert material checks. Face-normal comparisons exclude numerical triangles below 0.001 mm altitude; full mesh validity remains independently mandatory. This is a targeted mesh regression, not a global C1 proof.
- `check_joint_profile()` compares actual base/head silhouette spans in five cross sections, 2 mm either side of the joint. Old excess: 2.58–2.61 mm; new: 0.403–0.408 mm, reflecting the remaining transition below the joint. The accepted band is -0.1 to +0.6 mm. This guards the shoulder; it does not certify every surface tangent or erase the intentional seam chamfers.
- Follow-up evidence and images: `docs/rounding-2026-09-23.md`. Fresh full checks: seven mesh types, ten physical parts, 394 coaxial feature pairs, eight paths, 435 assembly pairs; all four analyses CLEAN. Estimated assembled mass 1008.4 g and tip angle 21.4 degrees. Slicer: 470.5 g / 15.4 h across four plates; 470.9 g / 16.1 h as individual part jobs.

The audit’s physical checks remain open where their features are retained: knob press fit, switch body depth, the charge module's soldered connections and tie against its OUT-end holder, insert pull-out, bridge quality on the small overhangs, and every thermal and airflow figure. Magnet-force checks are retired with the magnetic interface; cassette clamp strength and printed fit remain unmeasured.

## Open items

- Cassette screws: verify actual insert fit, cassette seating, tightening feel and retention on the printed parts. Geometric bearing and engagement checks do not establish pull-out strength or PETG creep. The former magnet-force and magnet-fit items are retired.
- Part masses for the tipping check are data-sheet or estimated values, not weighed (reported by `print_tools.py` as an OPEN item).
- The knob bore is nominal 5.8 mm with zero clearance, as in LEO-AC1 — validate the push fit on the real knurled shaft with a test print.
- Rocker switch body depth behind the panel is still the assumed value from LEO-AC1.
- LED: verify visibility through the closed 1.8 mm skin with the chosen PETG and actual LED. The former 0.8 mm thin-wall exception is retired; flange fit and light transmission through the deeper windows remain untested.
- Charge module: verify solder joints, wire exits, the tie band and clamping pressure at the cool OUT-end holder, the free heatsink end and wire slack for the loaded lid's service path. Check temperatures while charging in the closed housing, with the fan on and off; free geometric air corridors do not establish cooling performance.
- Filter support: check all four post contacts against the real fan frame, pocket fit, bar stiffness and creep, and mat bowing or loose fibres at maximum speed. The sparse cross does not establish that rubbing is impossible.
- Filter pressure drop and capture distance are not modelled. The P12 Pro is pressure-optimised (6.9 mmH₂O), which is why it suits a mat, but the working point is unknown.

## Verification and known limits

`docs/verification.json` holds the full report and the current check counts. Checks cover closed meshes and body counts, bed placement and build envelope, assembly pairs with documented assembly-stage or intentional-fit exceptions, coaxial round features, contacts, stops, assembly paths, heat-set insert pockets, the intake lip, mat displacement, and the centre of mass over the foot polygon. The dated results below describe their respective earlier revisions; their 0.8 mm LED-window exceptions do not apply to the current 1.8 mm skins. Likewise, previous
lid tongues, side-mounted USB stops, low gussets, lid slots and loaded-lid path numbers remain evidence
only for their stated revisions. The active design description above takes precedence; never treat a
report as current until its source SHA matches `fumex.scad`. All dated magnet-cavity,
insertion-pause, polarity and 18-insert results below are historical and superseded by the
2026-09-29 cassette-screw conversion; retain them as evidence of their own revisions only.

Not checked: flexible deformation (the mat and the TPU feet are rigid bodies here), strength, thermal behaviour, airflow, and anything about the real hardware that has not been measured.

## BOSL2 and upright-charger verification (2026-09-23)

- Final report: `docs/bosl2-charger-2026-09-23.md`; source SHA `544894c9fc4dc5176798e87bd9ad6000a1cbd028eab20a550ffad9b17326cd1d`.
- Seven valid print meshes / ten physical parts, 394 coaxial feature pairs, 435 assembly pairs and eight paths. All four printability analyses are CLEAN. The head thickness sampler retains its pre-existing numerical Trimesh warnings (64,906 valid samples of 65,060); this is not a complete wall-thickness proof.
- `check_rim_chamfers()` measures 24 exported profiles; maximum error 0.00020 mm. Both charger stops engage at 0.25 mm. `check_charger_air()` confirms two unobstructed connected passages at the real board/heatsink faces. These regressions reject the old chamfer and flat-board layouts respectively.
- Slicer: all seven parts and four plates pass with supports disabled; 469.7 g / 15.3 h as arranged plates, 470.0 g / 16.1 h as individual jobs. Existing base/head floating-cantilever warnings remain. The upright charger lid adds no warning. Estimated assembled mass 1007.6 g, tip angle 21.4 degrees.
- STLs, 3MF, README images and viewer are regenerated. No physical print or thermal/airflow test has been performed.

## Filter support and hardware follow-up (2026-09-23)

- Earlier hardware follow-up: `docs/hardware-2026-09-23.md`, before the wider switch recess, USB support ribs and closed LED window. That revision had eight print types / eleven physical pieces, 340 coaxial feature pairs, 496 assembly pairs and nine sampled linear paths; all four printability analyses were CLEAN.
- At that revision `ball_step[0]` was 122.5 rather than 126: 126 left the lid and trough tangent to the switch terminal envelope at y53. The intermediate lid and isolated trough-step probes measured 1.5 mm. The subsequent 118.5/60 step and radius-4.6 mm lid ear gave 5.50 mm before the terminals, 2.002 mm to the switch body and 2.402 mm from lid to switch. Those interim values predate the current 118.5/64 contour and relocated right post.
- The rear lid corner reliefs are 0.5 mm. The old 5 mm cuts depended on the removed corner posts to close the trough. `check_ballast_cover()` compares actual near-rim contents and lid sections, allowing only the intentional seam; the maximum measured normal gap is 0.2 mm. New insert bores are excluded from `ballast_env()`.
- `check_charger_holder()` probes each of the three seats, the hot-side exclusion and connected tie passages. `check_usb_wire_access()` includes the inner terminal face itself; probes above and below the board alone also passed with the old blocking end wall and were insufficient.
- At that earlier hardware revision ballast capacity was 44.0 cm3 / about 207 g of loose iron at the assumed packing density. Estimated assembled mass is 1020.5 g, tip angle 21.8 degrees, front margin 28.9 mm. Printed lid envelope is 138.6 x 17.8 x 13.7 mm.
- Only the loaded lid's 10 mm vertical lift is established. Sampled X/Y/Z tilts and coupled forward moves did not establish a complete extraction sequence; that remains unproven, not certified impossible. The head and battery are removed before the checked lift.
- General corner-post/cover dependency documented in the shared skill's PITFALLS.md, commit `41a0b0d`. Project scripts remain identical to the skill.

- Slicer at that earlier hardware revision: all eight types and four plates passed without supports; 468.9 g / 15.3 h on arranged plates, 469.3 g / 16.3 h as individual jobs. Existing base/head floating-cantilever warnings remain; lid and support cross have none. Head thickness sampling returns 64,941 valid points of 65,128 with the known numerical Trimesh warnings.


## Lid, switch, USB and front-detail verification (2026-09-23)

- Earlier detail follow-up: `docs/detail-refinements-2026-09-23.md`, before the subsequent plain-lid and mount updates. Source SHA `6bf5fd11fdefd249b418a3faa7921d67a7f2b9f68ec29cc29cbbd020050e2df5`.
- Exactly two M3 x 8 lid screws remain at (10,63) and (135,63), centred between the trough's inner front and back faces at y55/71. Both engage Ruthex RX-M3x5.7 inserts through Ø4 x 7 mm pockets. Actual seat material and enclosure fill are 100%; full 5.7 mm insert engagement leaves 0.8 mm to the pocket bottom. The right lid ear keeps its screw pocket enclosed beside the wider switch recess.
- USB support ribs run from the floor to the channel, verified by full solid probes. Both rear-open lid slots clear their ribs, the PCB contacts its seat at z42.85 and the three wire corridors remain open. The loaded lid's checked service motion is still only 10 mm vertically; full extraction remains unproven.
- Eight closed print types / eleven pieces; 337 coaxial feature pairs, 496 assembly pairs, nine general sampled paths and the additional 15 mm LED inside-access path pass. Islands, overhangs (100 mm² threshold) and fins are CLEAN. Thickness reports exactly one intended 0.8 mm region at the closed LED window (estimated sampled area 20 mm²); the 1.2 mm threshold is unchanged elsewhere. The head's existing Trimesh numerical warnings leave 65,088 of 65,277 usable samples.
- All eight individual slices and four arranged plates pass with supports disabled. The base's floating-cantilever warning is gone; the existing head warning remains on its individual and arranged slice. Arranged plates: 472.9 g / 15.4 h; individual jobs: 473.4 g / 16.4 h.
- At that detail revision ballast volume was 40.97 cm³, about 193 g at the assumed packing density. Estimated assembled mass 1009.8 g, front tipping margin 28.6 mm and tip angle 21.3 degrees. These supersede the previous revision's values above.
- All eight documentation views, the STLs, 3MF and both viewer copies are rebuilt. `07_ballast_mount` makes the two fasteners visible; `08_usb_mount` shows the floor-connected channel ribs.


## Plain lid, gussets and additional mounts (2026-09-23, historical revision)

The following dimensions and results describe that revision. Its rear-row head fasteners, lower USB
gussets and lid slots are superseded by the current design state above.

- The redundant Ø16 x 1.5 mm ballast-lid finger dish is removed at both construction levels. The top is plain there.
- The user requested 45-degree USB-C supports instead of floor-length ribs. `usbc_gusset()` clips the lower support profile to a 45-degree slope from the back wall. `check_usb_support()` measures both actual mesh slopes and the empty space below; the board seat, side stop, wire corridors and rear-open lid slots retain their previous positions.
- The user requested four head/base screws, with three as a minimum. Four accessible rear-row positions are used: x25/45/118/127, y66. A front row would be covered by the permanent filter tube. x48 was rejected because its boss blocked the loaded lid lift; x129 blocked the right lid screwdriver. All four use Ø10 bosses and Ruthex RX-M3x5.7 inserts. Head-floor openings must preserve a complete bearing pad around every screw, including the old x25 position beside the cable opening.
- A second matching LED pocket at x80, z21 accompanies the existing charge-indicator pocket at x88, z21. Both retain 0.8 mm front skins. The additional holder has no specified electrical function; do not silently wire it to a signal in the documentation.
- The PWM anti-rotation-tab cut-out now has `pot_tab_cl=0.4` mm per side instead of 0.2 mm, increasing its width from 2.5 to 2.9 mm. Hardware dimensions are unchanged.
- The speed knob diameter is 26 mm instead of 28 mm (user, 2026-09-23); the shaft fit, inner sleeve and installed depth are unchanged.
- The four head screws bear on the actual 0.6 mm counterbore floors, with 2.4 mm of solid bearing material, 5.6 mm thread penetration and 1.4 mm to the pocket bottom. Ø9 mm material pads protect the seats from cable/vent cuts; the shallow 0.6 mm pocket has a closed 0.8 mm rear lip at the head edge. The left pad has a run-out to the cable-opening edge so it grows continuously in the intake-face-down print.
- The user also owns a small Wera ratchet (2026-09-23). Its exact head/bit dimensions are unspecified. The chosen four head screws retain checked straight-bit access; do not infer that the roughly 4 mm gap under the front filter tube accommodates the ratchet.
- Final source SHA: `ef984926c92907ff6b44ab8dca544594ecc9b8692bdbae2d17ccce483a763e5b`. The complete export passes eight closed print types, eleven pieces, 374 coaxial pairs, 496 assembly pairs, nine standard sampled paths and the combined 15 mm LED access path. All four head-screw seat/contact/insert-access probes pass. Islands, overhangs and fins are CLEAN; thickness reports only the two intended 0.8 mm LED windows (sampled regions 16 and 12 mm²). The known Trimesh head warning leaves 65,204 of 65,404 valid samples.
- Current ballast capacity: 42.42 cm³ / about 199 g. Estimated assembled mass: 1019.3 g; front tipping margin: 28.9 mm, angle: 21.7 degrees. The shared skill now records the screw-seat/cut-out pitfall (`6c9b8ec`); project scripts remain unchanged.
- Final slicing: all eight types and all four plates pass with supports disabled and **no warnings**. The previous head floating-cantilever warning is gone. Arranged plates: 472.3 g / 15.5 h; individual jobs: 472.8 g / 16.5 h. Nine documentation views and both viewer files are regenerated. Evidence and the current change summary are in `docs/mount-updates-2026-09-23.md`.


## PWM PCB floor fastening (2026-09-23)

- User now fastens the PWM PCB with two **2.5 x 8 mm thermoplastic screws**, an explicit exception to the M3 insert hardware rule. Measured: PCB holes Ø3.2 mm; their centres are 3 mm from the front (potentiometer) edge and 3 mm from each side, hence 26 mm apart. Screw heads have flat undersides and Ø4.5 mm diameter. The user confirmed sufficient clearance on both PCB faces. Head height is unmeasured; the collision envelope conservatively uses 2.5 mm.
- Two Ø6 mm floor-connected bosses carry the PCB at z13.1, centred at (103,5.55) and (129,5.55). Existing long-edge pads support its rear. The screw goes through 1.6 mm FR4 and penetrates 6.4 mm into the boss; a Ø2.0 x 7.4 mm blind pilot provides 1 mm tip reserve and 2.5 mm of material above the 3.2 mm floor. The mouth has a 0.7 mm deep lead-in to Ø2.7.
- Ø2.0 is a starting pilot, not a measured fit for the unidentified screws in printed PETG. It follows the nominal 0.8D relation in the [EJOT DELTA PT thermoplastic design guide](https://www.ejot.com/medias/sys_master/Industry_Flyer/Industry_Flyer/h11/hc7/9331662782494/EJOT-DELTA-PT-Flyer-08.23-en.pdf); do not infer the user's screws are EJOT. Confirm drive torque and retention on a printed sample before fastening the PCB.
- The potentiometer has no front nut or washer. Its shoulder remains at y1.8 because moving the PCB rearwards would collide with the switch. `pot_shoulder_y` now expresses placement independently of removed fastening hardware. The knob is Ø24 instead of Ø26; shaft engagement and axial projection stay unchanged. Its sleeve clearance derives from the bushing end.
- `driver_pwm` requires a slim Ø4 mm shaft for 25 mm above the head before the wider shank/handle. A normal short 1/4-inch bit would strike the front wall. Two Ø4.6 vertical reliefs remove only the inside of the curved upper rim for shaft access. The user's small Wera ratchet is not certified by these unspecified dimensions.
- PCB and component/pin envelopes now distinguish the real holes and the user-confirmed clear mounting pads. `base/screws_pwm` is an intentional thread-forming interference, bounded separately in the mounting check; it must not hide contact outside the pilot annuli. PCB fasteners are driven before installing the head.

- The concealed front opening, tab slot and inner PCB edge slot allow 3.5 mm upward travel for installation. The inner housing recess is capped at z32 and reaches through the actual lofted inner wall; an uncapped R10 sweep left a thin region near z34. The outside remains covered by the Ø24 knob. The actual anti-rotation tab is now part of `pot_env()`, so the motion check includes it.
- `check_pwm_removal()` checks a complete sampled lift/retract/pitch/extract sequence. For the current 2026-09-25 layout, remove the head group, battery and rocker switch before the loaded ballast lid, then remove the knob and PCB screws; the LEDs and USB board remain. The older sequence with the loaded lid still fitted is superseded because the new keeper obstructs withdrawal. After `clear_rim`, shift the freed controller 6.5 mm left (negative x) before the final 60 mm lift, clearing the rear-right mounting area. The new `side_clear` phase has 66 samples at 0.1 mm; the final lift retains that lateral offset. Reverse the movement to install the PWM controller before fitting the lid and rocker switch. Translation samples are 0.1 mm, rotation 0.5 degrees, final lift 0.5 mm; this remains a sampled rigid-body path with no wires. Both screws have independent 60 mm extraction checks in 0.25 mm steps. Only their intended thread-forming regions are exempted.
- The shared skill records the loft/recess cutter pitfall in `PITFALLS.md`, commit `e72f129`; scripts are unchanged.

- Final source SHA `b21de4cee404bf7ec0729d4387ee1f67255d2660a494efb6897dea5861848cb0`. Eight closed print types / eleven pieces, 443 coaxial pairs and 528 assembly pairs pass. Both PCB/boss bearing rings have full material; individual contacts and pilot/thread/tool checks pass. The complete 465-pose PCB service path passes with maximum 0.000052 mm³ numerical overlap.
- Final analyses: islands, overhangs and fins CLEAN. Thickness finds only the two intentional 0.8 mm LED skins (20/12 mm²); head sampling retains 65,204/65,404 valid rays. All eight parts and four plates slice without supports and with no warnings. Arranged: 471.9 g / 15.6 h; individual jobs: 472.3 g / 16.6 h. Estimated assembled mass 1017.2 g, front margin 29.0 mm and tip angle 21.7 degrees. Report: `docs/pwm-mount-2026-09-23.md`.

- The knob is assembled as a removable press fit; the previous mandatory CA-gel instruction is removed because controller service requires pulling it off. The geometric path does not establish the force needed on the real knurled shaft.


## Public GitHub repository and LED spacing (2026-09-23)

- User requested publication on GitHub with the 3D viewer on GitHub Pages, following LEO-AC1. Repository: https://github.com/fhirschmann/fumex; Git remote `github`. Pages serves `main:/docs` at https://fhirschmann.github.io/fumex/. Keep `docs/.nojekyll` and regenerate `docs/index.html` with the shared viewer builder before publishing model updates. The README viewer button and assembly image link to this public URL.
- The second LED holder moves from x80 to x78, and the charge LED from x88 to x90, both at z21. The pair remains centred at x84. A one-sided move to x76 was rejected because its 15 mm inside insertion path intersected the battery. Centre spacing is now 12 mm instead of 8 mm (user requested more space). Both closed 0.8 mm skins and inside flange seats remain.
- The project licence header and third-party notice now name FUMEX and ARCTIC; BOSL2 is explicitly excluded from the project's CC BY-NC-SA grant and retains its BSD-2-Clause licence. This corrects leftover LEO-AC1 names without changing the intended project or tool licences.
- Final publication model SHA `b6aff7a9f9fa3554201d193ca9fee87963f8a676dbf34cea3bda2e38d5a54595`: eight valid print types / eleven pieces, 443 coaxial pairs, 528 assembly pairs, standard and PWM service paths all pass. Islands, overhangs and fins are CLEAN; thickness finds only the two authorised 0.8 mm LED skins (sampled areas 18/10 mm²). All eight parts and four plates slice without supports or warnings; arranged totals remain 471.9 g / 15.6 h. The viewer and all ten documentation views are rebuilt for this revision.


## Reinforced filter cross (2026-09-23)

- User found the original cross too flimsy. Arms are now 4 x 5 mm with R4 centre blends, smooth 6 mm end flares and 8 mm pads. `FULL_INFILL` includes `filter_support`; both individual slicing and the arranged 3MF use 100% zig-zag infill for it. Total support mass is 7.047 g in the slicer. The tipping estimate now uses solid PETG at 1.27 g/cm³ from the actual Generic PETG @BBL H2S profile, giving 7.333 g from the mesh volume, rather than the effective 20%-infill density of 0.90 g/cm³.
- Eight straight-arm sections from the old and new print STL, including the 0.4 mm bevels, give 7.3594 -> 19.6794 mm² area and 5.8612 -> 39.8682 mm⁴ second moment for bending normal to the mat (6.80 times). This compares solid geometry only, not measured printed stiffness or breaking load. No physical load or creep test was performed.
- The earlier front position required the span increase to 123 mm; at 122 mm the chamfer missed the front stop and export correctly failed. The accepted geometry passes all four head/fan stop probes, all 528 assembly pairs, 443 coaxial pairs and the existing service paths, including the complete sampled PWM path. Nominal fan gap remains 5 mm; air blockage is 7.177%.
- Final model SHA `8034ad1cff9f06f27993dd120a1819eda7b857e5f79558baf87808050042fc5a`. Eight watertight print types / eleven pieces. Islands, overhangs and fins are CLEAN. Thickness returns only the two deliberate 0.8 mm LED skins (18/16 mm²); head sampling retains 65,223/65,399 valid rays with the known Trimesh numerical warnings.
- All eight types and four plates slice with supports disabled and no geometry warnings. Arranged plates: 475.9 g / 15.7 h; individual jobs: 476.3 g / 16.7 h. Estimated assembled mass: 1022.2 g; front margin 28.9 mm, tipping angle 21.6 degrees. Ten documentation views and the public viewer are rebuilt.


## Printed battery and USB fit correction verification (2026-09-24, previous design state)

This completed revision predates the base-mounted battery wall, head shoulder holders, deeper LED
pockets, central USB stop and unslotted lid. Its saved report and source SHA remain historical evidence;
they do not validate the subsequent geometry.

- Final model SHA256 `a05f927b9d51141d7d27e9c4f06de12cda11b39044b67b257b1b7135bd99a771`: ten closed meshes, eight production types / eleven pieces and two optional test pieces. All 528 assembly pairs, 443 coaxial pairs, ten standard paths, PWM service path and 497-pose loaded-lid removal pass. Minimum loaded-lid clearance after lifting is 0.15755 mm. Only base and lid production geometry changed; the other six production STLs are byte-identical.
- Islands, overhangs and fins CLEAN on all ten meshes; thickness flags only the authorised two 0.8 mm LED skins. Estimated assembled mass 1023.1 g, front tipping margin 28.9 mm, angle 21.6 degrees.
- Ten individual slices, four production plates and one fit plate pass without supports or warnings. Production: 477.1 g / 15.8 h as plates, 477.5 g / 16.8 h as individual jobs. USB test: 11.8 g / 1.2 h (plate 1.17 h), using the same four-wall, 20% gyroid profile.
- Report and saved analyses: `docs/print-fit-2026-09-24.md`. The shared skill records positive battery retention, removable USB stops and lost bearing planes in cropped fit tests (`866f690`).
- Shared slicer fix `70ce515` preserves real `_base`/numeric suffixes and resolves copy numbers only against known source names; five regression tests and the complete skill template pass. Installed project scripts match the shared skill. Both viewer files and all eleven views are rebuilt; browser policy blocked reloading the open local `file://` viewer tab.


## Final base-retention follow-up (2026-09-24)

- The right lid post at (117,56.8) has a front flat at y52.95: 1.85 mm remains ahead of its Ø4 insert bore, and the complete Ruthex material ring out to radius 3.6 remains present. This gives the PWM board its checked withdrawal space while the insert tool clears the head boss by 0.271 mm. A cylindrical post at (114,54) blocked PWM removal; (130,63) blocked both screwdriver and insert-tool access. Neither intermediate position is used.
- The whole head group, including the fan, is removed before lid service. `ALLOWED_OVERLAPS` therefore permits `fan`/`driver_lid`, just as it already permits the head and back cover; the fixed base, USB board, charger and installed switch remain real obstacles for the tool check.
- Shared print-project skill commit `21cc1cc` records that a combined battery/BMS envelope must not count contact on the fragile board as battery retention. The new check separates body and board and includes diagonal escape along the cradle wall.

- Final source SHA256 `edbaddc6a11a0139257ecf6defe52e571f14585859154e7e769e51c90340af35`: ten valid meshes, eight production types / eleven pieces, 449 coaxial pairs, 528 assembly pairs and ten general paths. Complete PWM, loaded-lid and continuous USB/coupon paths pass. Islands/overhangs/thickness/fins are CLEAN on all ten meshes; the former LED exception is retired. Head thickness keeps 65,500/65,672 usable rays with the known numerical warnings. Assembled estimate 1012.6 g, front margin 28.5 mm, tip angle 21.2 degrees.
- Coincident faces in the new screw post and coupon were corrected in the source, without mesh repair: the D-post front sits at y52.95 rather than exactly on the y53 trough face, and the redundant middle fixture pad is removed. The coupon is supported by two pads and its actual cropped right post; `check_usb_fit()` verifies all three supports at z26, the board stop and continuous insertion.
- All ten individual slices, four production plates and the optional fit plate pass without supports or slicer warnings. Production totals: 476.8 g / 15.8 h as arranged plates, 477.2 g / 16.8 h as individual jobs. USB fit plate: 10.3 g / 1.09 h. Final report and saved analyses: `docs/base-retention-2026-09-24.md`.
- Both viewer copies are rebuilt from the final assembly exports and are byte-identical; affected documentation views are regenerated. Browser policy still prevents refreshing the open local `file://` tab, which requires a manual reload. Project scripts remain identical to the shared skill.


## Battery ties, four-corner joint and USB upper return (2026-09-25, previous joint arrangement)

- This snapshot used four horizontal head screws. Its rear tongues/windows and the front axial
  gap were subsequently superseded by the directly contacting front seats and two downward rear
  screws described in the active design block above. The recorded SHA, checks and measurements
  below remain evidence for that earlier revision, not the current joint.
- Final source SHA256 `e2618ebbf2db47b545d2ba26b4e51981ecd32fe97618b2e99e35e175a1ecc460`. See `docs/tie-corners-2026-09-25.md` for geometry, actual dimensions, assembly sequence and limitations. Updated production parts: base, head, head_back, ball_lid and two new battery_bridge pieces; both USB coupons also change. The base/head/back cover must be used as a matching set.
- Floor loops retain two ties up to 3.6 x 1.2 mm, nominally 150 mm long. The two loose bridges transfer tie load to the cell shoulders instead of the full-length BMS. Their 25 mm openings have 0.5 mm nominal overhead clearance and 0.3 mm after 0.2 mm settling onto the cylindrical shoulders. The measured head gaps are 0.4 mm to bridges and 0.23707 mm to ties; the local head floor remains 1.3 mm thick. Cushioning is optional and must not raise the cell. Buckle envelope 6 x 4 x 5 mm, in front of the cell. Physical tightening, buckle fit, bridge deflection and PETG creep are unverified.
- The 4 mm central USB keeper has a 1 mm upper return with a 1.6 mm roof. Upward motion is free at 0.1 mm and captured at 0.6 mm; front-edge lever rotation is captured at 2.9 degrees. Both wire corridors and the complete loaded-lid path remain clear. Real PCB bearing area and cable-lever force need the updated fit print.
- Final export: eleven closed, single-body print meshes (nine production types / thirteen pieces plus two optional test types), zero degenerate faces, 435 coaxial feature pairs, ten standard paths and 595 assembly pairs PASS. Battery ties/bridges, USB anti-lift, all four head seats and tools, complete PWM and loaded-lid service checks PASS. The 60 mm head-removal path keeps the mat, support cross and magnets with the head while the battery ties and bridges stay fitted.
- Islands, overhangs, thickness and fins are CLEAN on all eleven meshes at the configured thresholds. CGAL fallback resolves the base, head and base-coupon exports without mesh repair. All eleven individual slices, four production plates and one USB test plate pass with support disabled and no warnings. Production: 481.3 g / 16.1 h as plates, 481.9 g / 17.5 h as individual jobs. USB fit: 9.9 g / 1.04 h. Static assembled estimate 1018.6 g, front margin 28.2 mm and tip angle 21.0 degrees; ballast remains 40.3 cm3 / 189.4 g.
- Both viewer copies and all twelve documentation views are regenerated. Browser policy still prevents reloading the open local file tab; it needs a manual reload. Shared scripts remain identical. Shared skill improvement `208aae9` documents settled bridge-to-BMS clearance, complete tie/buckle routes and the distinction between geometric capture and unmeasured clamp loads.


## Direct rear head-to-base screws and clamped backing (2026-09-25, previous front arrangement)

- User rejected the rear horizontal tongue fastening and requested screws down into the base. Current dimensions and results: `docs/head-clamp-2026-09-25.md`. The head-fastener geometry in the earlier same-day tie/corners report is superseded; battery and USB changes remain.
- The old screw heads did have 1.15 mm radial overlap and about 16.44 mm2 bearing area. However, 0.25 mm clearance behind each seat required deformation before clamping. `check_head_fasteners()` now checks a full base material ring directly behind the seat, the matching head-side material and less than 0.01 mm nominal interface gap. All four report zero gap and full material. The new front probes reject the previous published base (0% material) and accept the revised base (100%); saved mesh hashes are in `docs/head-clamp-2026-09-25/backing-regression.json`.
- Source SHA256 `fd7bafbd62166f591abb133d0b37a50bc666eee8350e060e27a03c67f91f983d`. Base/head/head_back production geometry changes; four M3 x 8 and four head inserts remain. Rear floor seats have 2.3 mm backing and 5.7 mm engagement; front seats 2.05/5.95 mm. Base print envelope is 145 x 74.7589 x 65.6772 mm; its floor footprint is unchanged.
- Full export PASS: eleven closed single-body print meshes, no degenerate faces, 429 coaxial feature pairs, 595 assembly pairs and ten paths. The cover removal now treats the head screws as fixed obstacles. All four print analyses CLEAN. Eleven individual meshes, four production plates and one USB test plate slice without supports or warnings. Arranged production 479.3 g / 16.0 h; individual 479.8 g / 17.4 h; USB test 9.9 g / 1.04 h. Static mass estimate 1016.5 g, front margin 28.2 mm, tip angle 21.0 degrees.
- Both viewer copies and all twelve documentation views are rebuilt. View09 now keeps the head and screws assembled; previously lifting only the head made the screw heads appear detached. Shared scripts match; skill commit `a3823d0` records direct backing checks and clear fastener illustrations. Physical preload, PETG creep, pull-out and ultimate strength remain untested.


## Angled front head screws and local mat bending (2026-09-25, historical)

- Source SHA256 `168a78f6f4feee21a4a681cc80e19e1eff23b0a5b94902d21c74bd88b72ffc9a`. Final dimensions and evidence: `docs/front-clamp-2026-09-25.md`. Both front fasteners now point 40 degrees outwards into the base. A 30-degree candidate obstructed the PWM service path; the final right boss starts beyond PCB x132 throughout its length, restoring the unchanged full service route. The head's guide windows sweep downwards so the head can lift straight off while its angled clamping faces retain direct contact.
- All four head bearing rings, backing rings, insert walls and blind floors have 100% material in the independent probes; all nominal clamp gaps are zero. Engagement is 5.7 mm for both front M3 x 16 and rear M3 x 8 screws. Front total mat overlap is 290.818 mm3, bounded to two local zones and 2.7 mm maximum deflection. The user authorises local mat bending; no flexible-force model is claimed.
- The ratchet's complete assumed body and 25-mm bit pass continuous entry/seating sweeps. Its ±6-degree swing has 0.442 mm sampled clearance and a conservative 0.376 mm lower bound between samples. Tool dimensions remain assumptions as listed above. The cassette and mat are removed for this operation. Head screws and their tools are also absent during PWM fastening; the two new stage exclusions reflect that actual assembly order.
- Full export PASS: eleven closed single-body print meshes, zero degenerate faces, 445 coaxial feature pairs, 595 assembly pairs and ten standard service paths. All four print analyses are CLEAN. All eleven individual slices, four production plates and one USB fit plate pass without supports or warnings. Production: 478.8 g / 15.9 h as arranged plates, 479.4 g / 17.3 h as individual jobs. USB fit: 9.9 g / about 62 min. Static mass 1015.5 g, front margin 28.2 mm, tipping angle 21.0 degrees.
- Base envelope is 145 x 74 x 57.2657 mm; head is 145 x 145 x 70 mm in print orientation. Both production parts need the current matching versions. All twelve views and both viewer copies are rebuilt. The local file tab still requires manual reload. Shared scripts match; skill pitfall update `32581a6` is published.


## Straight exposed front head screws (2026-09-25, before the shallow recesses)

- Source SHA256 `b45799ece7eedaee3dce09ec6baf3b646c45baf648104f66f1b36f7e49f55787`. Current dimensions and evidence: `docs/straight-front-clamp-2026-09-25.md`. All four head screws are M3 x 8, parallel to the same downward joint normal. Front entries are (25.5,6.5,60) and (119.5,6.5,60), with seats at z62.3; no printed shroud remains above the seats. This supersedes the angled front pair in the preceding section.
- Full export PASS: eleven closed single-body meshes, no degenerate faces, 427 coaxial feature pairs, 595 assembly pairs and ten standard service paths. All bearing, direct backing, insert-wall and blind-floor probes have 100% material. Each screw engages 5.7 mm with 1.3 mm pocket reserve. The staged 532-pose PWM route passes with at most 0.000052 mm3 numerical overlap. Ratchet translations are clear and the continuously bounded swing retains at least 0.902039 mm clearance, subject to the assumed tool dimensions.
- Mat contact is 313.068840 mm3 for the caps (1.8 mm depth) and 108.391642 mm3 for bare screw heads (3.45 mm depth), total 421.460483 mm3. Only the two local zones are allowed, with a 450 mm3 volume gate. The flexible-mat allowance does not prove force, sealing or durability.
- Islands, overhangs, thickness and fins are CLEAN on all eleven meshes. The initial root clearance left broad 0.3–1.2 mm front membranes; rectangular reliefs below local z57.5 eliminate them while preserving the caps and sealed tube floor. All eleven individual slices, four production plates and the USB fit plate pass without warnings or supports. Arranged production: 477.3 g / 15.8 h; individual jobs: 477.9 g / 17.2 h; fit plate: 9.9 g / 62 min. Static assembled estimate 1013.9 g, front margin 28.3 mm and tipping angle 21.0 degrees.
- Base/head are the changed production pair; their print envelopes remain 145 x 74 x 57.2657 mm and 145 x 145 x 70 mm. All twelve views and both viewer copies are rebuilt. The local file tab requires manual reload. Shared scripts match; skill pitfall update `00197d8` is published.


## Shallow front screw recesses (2026-09-25, current)

- User requested shallow front recesses like the rear pair. The two front pockets are Ø6.4 x 0.7 mm, with bearing faces at local z61.6 and unchanged cap tops at z62.3. The screw heads remain 0.95 mm proud. Front bearing thickness is 1.6 mm; M3 x 8 penetration is 6.4 mm with 0.6 mm pocket-bottom reserve. Base axes, roots and inserts remain unchanged. The intake cutter now excludes the cap bodies, preserving their full pocket rims and outer bevels instead of leaving a 0.09 mm sliver beside the pocket.
- Source SHA256 `fd2fbc0cf9d9d500c3e94c05c317dcb5912706031bdcfc5565e9813130792e07`; report `docs/recessed-front-screws-2026-09-25.md`. Full export PASS: eleven closed single-body meshes, zero degenerate faces, 445 coaxial feature pairs, 595 assembly pairs and ten standard paths. Measured front pocket depth is 0.699999 mm on both sides. All bearing/rim/backing/insert probes pass; PWM service and the ratchet route pass, with at least 0.902039 mm continuously bounded swing clearance for the assumed tool.
- Local nominal mat overlap is 379.548611 mm3 (head 280.800581, screws 98.748029), maximum depths 1.8/2.75 mm, gate 400 mm3. All four print analyses are CLEAN on all eleven meshes. All eleven individual slices, four production plates and the USB fit plate pass without warnings or supports. Production 477.3 g / 15.9 h arranged, 477.8 g / 17.2 h individually; USB fit 9.9 g / 62 min. Assembled estimate remains 1013.9 g, front margin 28.3 mm and tip angle 21.0 degrees.
- Only the head production geometry changes; the base matches commit `39c6441` with 0 mm3 Boolean difference. Both 3MF files, all twelve views and both viewer copies are rebuilt. Local file tab still needs manual reload. Shared scripts match the skill.


## Reinforced lid-mounted PD keeper (2026-09-25)

- User requested angled reinforcement at the keeper foot. Two triangular cheeks at x102..104.2 and x107.8..110 add 2 mm side extensions with 0.2 mm overlap into the stem. They run 8 mm rearwards from y53.2 and rise 8 mm above the z29 lid, with their toes embedded 0.01 mm into it. Both are integral, support-free features below the wire corridors. The upper PCB stop/return and base channel remain unchanged.
- Source SHA256 `7e90185f184b1b34f1a70f9b1028df8e681000716e65b3594a7d6f6cf688a46d`; report `docs/pd-keeper-braces-2026-09-25.md`. Changed print geometries: ball_lid and usbc_fit_lid. Full export PASS: eleven closed single-body meshes, zero degenerate faces, 445 coaxial feature pairs, 595 assembly pairs and ten standard paths. Both rib foot/web/stem-junction/deck probes contain 100% material and reject the previous bare stem. The isolated keeper clearance includes the whole ribs through y61.2. All six wire corridors, the lower/upper board capture, coupon insertion and complete loaded-lid removal remain clear; service clearance after the first lift is at least 0.20 mm.
- Islands, overhangs, thickness and fins are CLEAN on all eleven meshes. All eleven slices, four production plates and the USB fit plate pass without warnings or supports. Lid mass 8.43 g; arranged production 477.4 g / 15.9 h; individual jobs 478.0 g / 17.2 h; USB fit 10.0 g / 62 min. Static estimate 1014.0 g, front margin 28.3 mm, tip angle 21.0 degrees. Physical strength/creep remain unmeasured.
- Both 3MFs, all twelve documentation images and both viewer copies are rebuilt. The local file tab needs manual reload. Shared scripts remain identical to the skill.


## Direct battery cable ties (2026-09-25)

- The user removed the two loose pressure bridges. Both ties now run directly around the shrink-wrapped cell/BMS pack through the unchanged floor loops. No replacement spacers are fitted. Tighten gently by hand; the geometry does not isolate the BMS from strap pressure. The removed bridge STL, print registrations, plate instances and viewer item are gone.
- Source SHA256 `b918a76215a4885e8c215c0fe97e16c3aa9fbab6748c803e2b0783f3ac3178f7`; report `docs/direct-battery-ties-2026-09-25.md`. Full export PASS: ten closed single-body meshes, zero degenerate faces, 443 coaxial pairs, 561 assembly pairs and ten standard service paths. Direct band/head clearance 2.70913 mm; centreline length 120.448 mm, leaving 29.552 mm on each 150 mm tie. Anchor tunnels/material and the battery cable corridor pass. Separate pack-lift contact measurements explicitly identify initial BMS contact, without retaining the old pressure-isolation claim.
- Islands, overhangs, thickness and fins are CLEAN on all ten meshes at configured thresholds. Head thickness retains 65,253/65,414 rays with the known numerical warnings. All ten individual slices, four production plates and the USB fit plate pass without supports or slicer warnings. Arranged production 475.8 g / 15.8 h; individual jobs 476.2 g / 16.8 h; USB fit 10.0 g / 62 min. Static estimate 1012.6 g, front margin 28.3 mm, tip angle 21.0 degrees.
- All remaining printed geometries match commit `2beb14ea21e3c4499f302b4efcb3e42927a42121`; base and fit-base Boolean differences are zero, all other STLs are byte-identical. Existing head reliefs remain, parameterized independently as `bat_tie_head_clearance`. No housing reprint is needed for this change. Both 3MFs, all twelve views and both viewer copies are rebuilt. The local file tab requires manual reload. Shared scripts remain identical to the skill.


## Battery stop tied into the trough (2026-09-25)

- User requested the battery end stop be connected to the ballast trough for stability. A 3 mm full-width, floor-rooted web joins the existing rounded stop to the trough front wall; its rearward top slopes 45 degrees from z29 down to z25.6 and overlaps the wall by 1 mm. Only the base production geometry changes. The battery-facing stop, axial play, ties and removable lid stay as before.
- Source SHA256 `152bdde96866f33b4eff4f85b12d2b582b43e39602d3c16a702fa8b487168946`; report `docs/battery-stop-link-2026-09-25.md`. Full export PASS: ten closed single-body meshes, zero degenerate faces, 443 coaxial pairs, 561 assembly pairs and ten standard paths. Probes find 100% material across the former gap and both junctions, rejecting the preceding unconnected base. Installed local lid clearance is 0.282844 mm across the diagonal top (0.4 mm vertically); the complete loaded-lid path still passes. Battery gap stays 0.5 mm and the upper cable corridor remains clear. This geometry check does not measure strength or creep.
- Islands, overhangs, thickness and fins are CLEAN on all ten meshes at configured thresholds. All ten individual slices, four production plates and the USB fit plate pass without supports or slicer warnings. Base 119.472 g; arranged production 475.9 g / 15.8 h; individual jobs 476.3 g / 16.8 h; USB fit 10.0 g / 62 min. Static estimate 1012.8 g, front margin 28.3 mm, tip angle 21.0 degrees.
- Both 3MFs, all twelve views and both viewer copies are rebuilt. The local file tab requires manual reload. Shared scripts remain identical to the skill.


## Pre-print audit (2026-09-25, revision 4a11856)

- Consolidated user-facing audit: `docs/preprint-audit-2026-09-25.md`; immutable report snapshots, artifact hashes and supplementary mesh probes are in its sibling directory. No model, print profile or production artifact was changed during this audit. Additional review found no new confirmed geometric print/assembly blocker.
- Before using the user's Extrudr XPETG Matt spool, reconcile the exported profile: both PETG slots still use Generic PETG at 255 C for all layers and normal cooling 40–90%, whereas the current manufacturer page recommends 210–240 C and 20–50%. Bed 70 C and the 12 mm3/s cap match its guidance. Keep material family PETG as requested, but select the actual spool profile and reslice. The audit does not claim that the exported profile was corrected or that the open Bambu session uses the same settings.
- Pair-count precision: 34 assembly bodies give 561 possible pairs; 28 documented exceptions leave 533 generic pairwise collision tests. The important thread/mat exceptions have bounded dedicated probes. A lower overhang threshold 5 mm2 finds 31 production patches plus 2 repeats in the USB coupon; the largest is the 10.75-mm USB-seat bridge. This is compatible with the standard 100-mm2 gate and warning-free slices, not an absence of small bridges.
- Additional rigid-path checks confirm USB insertion with PWM/pot/LEDs already fitted and left battery capture across nine shifted poses. Real-fit limits remain: 0.20–0.27 mm loaded-lid clearance, early PWM gaps around0.192 mm and a tiny conservative pin-envelope intersection 0.0000517 mm3, actual USB upper bearing, omitted wiring/charger tie buckle/switch clips, assumed ratchet dimensions, and approximate potentiometer axis height 6.0 mm in LEO versus model 6.3 mm with 0.2 mm radial bushing play. None is a confirmed new CAD obstruction; use the USB coupon and dry assembly to resolve them.
- The tipping model's effective printed density gives 1012.8 g/21.0 degrees. Substituting current slicer part masses at unchanged mesh centroids gives 1090.1 g/20.2 degrees and 27.5 mm front margin; both use estimated hardware and unmeasured mass distributions. The audit records this uncertainty instead of silently presenting the original density estimate as a weighed result.


## Embedded magnets and fan cable opening (2026-09-26)

- Physical print feedback supersedes the previous audit at these two locations: the head's
  3.2 mm pocket depth equalled its 3.2 mm intake-face thickness, so the cavities opened
  through their backs. Radial skin checks did not establish an axial stop. The original
  10 x 10 mm cable hole also lacked any plug-envelope or threading-path check.
- Both head and cassette now have four closed Ø10.3 x 3.2 mm cavities with 1.2 mm skins
  on both axial sides. Head cavities are local Y1.2..4.4; cassette cavities Y-4.4..-1.2.
  Both print with cavity floors at Z1.2 and roofs starting at Z4.4. At 0.2 mm layer height,
  `PAUSES` requests a pause before Z4.6, the first closing layer. Each part has its own
  plate; the other black parts share the base/back plate, followed by knob and TPU plates.
  Project 3MF stores the pauses; bare STLs do not. Nominal 3 mm discs sit 0.2 mm below the
  cavity roof. Confirm size, flat seating and polarity before resuming each print.
- The entire head intake face grows to 5.6 mm, moving mat, support cross and fan 2.4 mm
  rearwards without intruding into the filter corners. Rear plenum and fan posts shorten
  to 11.9 mm; the outside head depth remains 70 mm. The support cross has the same printed
  geometry. Use the matching new head, cassette and back cover; the base is reusable.
- The cable notch is 16 x 13.3 mm, local X32..48 / Y56.7..70, open through the rear edge.
  Removing the neighbouring first vent leaves a 5.5 mm web to the next slot. The remaining
  slots retain Y56.7..66.7 independently of the fan position, leaving a checked 3.3 mm
  rear floor web. Place the connector into the bay with the fan/cover assembly held back before closing the cover.
  The unchanged rear-left bearing retains its complete ring. Connector test dimensions
  are a conservative assumed envelope, not a measurement of the user's Arctic plug.
- New independent mesh checks cover cavity clearance, both planar axial skins on all
  eight pockets, magnet containment, the open cable gate, connector insertion with the
  cover held back, final cable clearance and cover movement. The former meshes are
  negative regression fixtures. Material-body validation now distinguishes four cavity
  boundary shells from disconnected printed parts, with generic nesting regressions in
  the shared skill. See `docs/fan-cable-magnets-2026-09-26.md` for release evidence.

- Final source SHA256 `d2d21113b80c1214a133452ce8b9820178cb5de3a1354b2a165ddce98acb4137`:
  ten valid single-material-body print meshes; head and cassette each contain four
  correctly oriented closed cavity shells. Export PASS with 431 coaxial pairs, ten
  standard paths, full magnetic axial skins and the continuously swept connector route.
  There are 561 possible assembly pairs and 29 documented assembly-stage/intentional
  exceptions (532 generic pair tests); PWM fastening removes the head and cassette,
  including their enclosed magnets. All four standard analyses CLEAN. Ten individual
  slices, five production plates and the USB test plate pass without geometry warnings
  or supports. Saved head/cassette pauses are verified before extrusion at layer 4.6.
  Independent G-code ROI checks at all eight cavities confirm floor extrusion through
  Z1.2, no crossing extrusion from Z1.4 through Z4.4, then first roof bridges at Z4.6.
  Production totals: 491.4 g/16.5 h arranged; 491.7 g/17.4 h individually. The generic
  body/cavity checker is shared-skill commit `9fedfc0`, covered by 13 regressions and
  the full template pipeline. Actual magnetic force, disc dimensions, plug dimensions
  and flexible wiring remain physical-fit checks. Material profiles were not changed.


## First-layer wall count (2026-09-26)

- User requested one wall on the first layer. `PROCESS["settings"]` enables Bambu's
  `only_one_wall_first_layer = "1"`; the normal `wall_loops = 4` stays unchanged.
  This applies to every production plate and the USB fit plate. Magnet pauses remain
  before Z4.6. No model dimensions or plate layouts changed; regenerate both project
  3MFs through the complete slicer check and rebuild the viewer for publication.
- Both 3MFs retain this key in `different_settings_to_system` so Bambu Studio keeps
  the override when loading. All ten individual slices, five production plates and
  the USB fit plate pass without warnings. Production estimate: 491.5 g / 16.5 h
  arranged, 491.9 g / 17.4 h individually; rounded README totals are unchanged.

## Cross spring grip and tighter magnet fit (2026-09-28)

- User confirmed that the loose support cross was being tried in the open head and requested
  grip before fitting the fan. The new cross uses eight spring cheeks on its four end pads;
  the existing head sockets stay 8.4 mm wide. Do not enlarge `mat_support[5]` to change the
  grip, because that would also enlarge `filter_support_pockets()` and lose retrofit compatibility.
  `mat_clip` independently sets the 8.7 mm free width and 0.15 mm interference per cheek.
- The full 1.6 mm front foot remains connected to the arm. A 3.8 mm central slot leaves
  2.1 mm cheeks; the separate 0.9 mm radial slot releases them from the 5 mm cross bar.
  Root fillets are 0.6 / 0.45 mm. The gross root-to-tip length is 8.2 mm, but the effective
  lever to the rib is approximately 6.6–7.4 mm once its position and root transitions are
  considered. Neither this geometry nor its kinematic clearance check predicts holding force.
- The user supplied Ø10.04 mm as the successful Tinkercad magnet-pocket diameter. Both head
  and cassette adopt it; depth 3.2 mm, 1.2 mm axial skins and the Z4.6 insertion pauses stay.
  Nominal magnets remain independent Ø10 x 3 mm envelopes. Radial rays on three cavity
  planes reject the old Ø10.3 mm holes; separate disc probes reject accidental shrinking of
  the hardware envelope. The user has not supplied actual magnet measurements.
- Reprint only the cross to add spring grip to an existing head. Tighter magnet cavities
  require the new head and cassette. The base, back cover, ballast lid, knob, feet and USB
  fit coupons have no intended geometry change. First-layer wall count remains one; normal
  walls remain four; the cross stays solid PETG and all supports remain disabled.
- Shared skill note `97d6937` distinguishes captured loose parts from retention in the open
  assembly stage, explains the radial relief required for the real spring length, and requires
  bounded interference plus a locally deflected insertion envelope. The project also adopts
  the current shared slicer, retaining the requested first-layer setting in diagnostic/test jobs.
- Final verification source SHA256 `c4930f45065ccac14310cadf64c1cdb1deac2b4ec8c2bfcc79207e58f7872851`: ten valid print meshes,
  431 coaxial feature pairs, nine standard service paths plus the continuous compressed-cross
  path, and 531 generic collision pairs out of 561 (30 bounded/stage exclusions).
  All four analyses are CLEAN on the three changed meshes. Spring overlap is 2.094856 mm3
  confined to eight contact ribs; each penetrates nominally 0.15 mm. The kinematic proxy moves
  each rib inward 0.17 mm, keeps the roots fixed and clears the complete 30 mm withdrawal;
  it does not represent physical spring stiffness. Old loose-cross and oversized-magnet-hole
  regression fixtures are rejected. Current estimated mass is 1034.8 g with a 20.4-degree
  front tipping angle and 27.7 mm front margin.
- All ten individual slices, five production plates and the USB fit plate pass without geometry
  warnings or supports. Production totals are 491.0 g / 16.5 h arranged and 491.4 g / 17.4 h
  individually. The replacement cross is 6.554 g / 0.367 h at 100% infill. First-layer one-wall,
  normal four-wall settings and both Z4.6 pauses persist in the 3MF files. Head and cassette
  remain on separate plates (user reconfirmed due to the black/grey colour change).
- Both viewer copies and all fifteen views have been regenerated. Source changes affect only
  the head/cassette magnet bores and the removable cross; printed socket dimensions are retained.

## Magnet-pause bed clearance (2026-09-28)

- User requested more hand clearance for inserting magnets and asked to retain the preference
  in the shared printing skill. `PAUSE_LIFT_MM = 30` now wraps the stock H2S `M400 U1` pause
  in a relative +30 / -30 mm Z pair at F600 (10 mm/s), with motion waits and explicit G90/M83
  restoration. Positive Z lowers the H2S bed. No extra XY parking or homing is added.
- The pause still occurs before extrusion on the Z4.6 closing layer, on separate head and
  cassette plates. The actual pre-pause position is Z4.4, not the new layer's marker: the
  added moves are Z4.4 -> Z34.4 -> Z4.4. The native firmware parking/resume routine remains
  responsible for its own movements. Its physical behavior has not been tested here.
- Shared slicing checks track actual linear and arc Z moves, reject lifts within 2 mm of
  the machine's Z limit, verify the exact balanced block and extrusion mode, and require
  an explicit feed rate on the first following move. Bambu may remove the redundant F600
  from the return move; the check verifies its inherited modal feed rate instead.
- `machine_pause_gcode` is stored in the project printer profile and listed in
  `different_settings_to_system`, so opening the 3MF retains it. The multiline layer-pause
  XML is escaped. Plain STLs and individual diagnostic slices do not carry the saved pauses.
  No model geometry or plate layout changes in this revision.
- Shared skill commit `5fe7325` includes the 30 mm default, mode-aware pause detection,
  17 new pause regressions (32 unit tests total), and a successful complete template run
  with a real insertion pause. FUMEX's ten diagnostic slices, five production plates and
  USB test plate pass without slicer warnings; both actual magnet pauses verify the
  Z4.4 -> Z34.4 -> Z4.4 movement. Estimates remain 491.0 g / 16.5 h arranged.
  Both viewer copies were rebuilt; their unchanged hash reflects unchanged geometry.


## Historical front insert reinforcement (2026-09-28; subsequently removed)

- The user reports that the printed front head-mount posts break at the connection to the
  base front wall, not around the inserts. The original 9.2 mm wide hull started from only
  a 2 mm high wall patch in the head frame (z46..48). The Ø4 x 7 mm pockets, 2.6 mm radial
  post wall and 2 mm blind floors retain their original dimensions.
- The user measured 10 mm of free space above the PWM controller and reports ample room
  on the opposite side. `rim_front_base_brace()` therefore uses a 24 mm wide, deeper left
  foot and an 18 mm wide right foot, both kept 0.1 mm below the tilted joint. In installed
  coordinates their undersides follow z = 21.8 + 1.1 y (left) and z = 31.2 + 1.1 y (right),
  about 47.7 degrees above horizontal, growing out of the existing wall without supports.
  The left foot uses 9.4 mm more depth and ends at y12, ahead of the battery and tie buckles.
  The right foot retains the verified controller envelope and service clearance rather than
  inferring new absolute component heights from the user's clearance measurement.
  Their width spreads the post load laterally along the wall.
  The existing `rim_front_base_raw()` remains the exact head-clearance template; changing
  that shared module would change the already printed head's mating geometry too.
- The base's existing PWM screwdriver relief trims the right foot locally. All earlier
  controller removal stages stay unchanged, but the final lateral shift grows from 6.5
  to 9 mm left before lifting. The previous path clipped the new right foot. The wider
  offset retains about 0.6 mm nominal clearance at this feature; physical wiring and
  assembly tolerance remain outside the rigid geometry check.
- This is a geometric load-spreading improvement, not a measured breaking-load or PETG
  creep result. Reprint only the base for this change; all screw axes, head seats and
  upper insert-post surfaces retain their fitted geometry.
- Final source SHA256: `61f4dff845d1437bf6ce3110dd4a673716e2964726ece6d9483f60394f5637aa`.
  All ten print meshes export correctly; 431 coaxial feature pairs, nine assembly paths
  and 561 assembly pairs pass. Independent Boolean comparison against `2357a6d` finds
  2049.726 mm³ added only at the two front roots, with no meaningful removal or changes
  above the joint; the head and all other print meshes are geometrically unchanged.
  At local z47, measured root section grows from 85.556 to 250.537 mm² on the left and
  from 82.914 to 117.696 mm² on the right. The new connected-stock probes reject the old
  base. The deeper left foot clears the battery by 10.171 mm and its ties by 8.535 mm;
  the revised PWM final lift has at least 0.604 mm clearance near the right foot.
- Islands, overhangs, thickness and fins are CLEAN on the changed base. All ten individual
  slices, five production plates and the USB test plate pass without supports or slicer
  warnings. Base: 120.863 g / 3.789 h; production: 492.4 g / 16.6 h arranged, 492.8 g /
  17.4 h individually. Both 4.6 mm magnet pauses retain the 30 mm bed clearance; the first
  layer retains one wall. Both viewer files and affected documentation images are rebuilt.
- Shared-skill commit `4bfbb89` records checking the wall connection independently of
  insert-pocket wall thickness and verifying the complete service path after reinforcement.
  Project scripts remain identical to the shared skill.

## Grey covers and closer USB side fit (2026-09-28; historical plate layout)

- The user requests a grey back cover and ballast lid, matching the cassette and knob.
  Both use `PETG-grey` (filament 2) in production, with matching OpenSCAD assembly colours,
  lifted-grey viewer colours and documentation images. Plate 2 now holds the black base
  and support cross; plate 4 holds the grey back cover, ballast lid and knob. The head
  and cassette retained their separate magnet-pause plates 1 and 3 at this revision.
  The later shared-cover plate below supersedes this layout. USB fit coupons remain
  a single-colour test on filament 1. The cover and lid geometry is unchanged.
- The user measured this USB PCB as 10.06 mm wide and reported excessive lateral play.
  That measurement supersedes the inherited LEO-AC1 width of 10.35 mm for this project.
  The previous 10.75 mm guide channel left 0.69 mm total nominal play. The new channel
  and rear wall recess are 10.26 mm wide: 0.10 mm clearance on each side. Dedicated
  `usbc_side_cl` keeps the existing 0.2 mm vertical and receptacle allowances unchanged.
  Both 2 mm guide walls move inward by 0.245 mm. A 0.8 mm lead-in opens each inner edge
  by about 0.2 mm at the mouth and finishes 0.1 mm ahead of the installed PCB front.
- `check_usb_side_fit()` measures the actual inner and outer faces at the tapered entry,
  front/middle/rear of the seated PCB and the rear wall recess. It checks the independently
  measured PCB envelope, free lateral movement at 0.08 mm and stop contact at 0.13 mm
  in both directions. Front and upper keeper capture remain effective at both 0.1 mm
  lateral limits. The old 10.75 mm channel fails this check. Existing wire, support,
  loaded-lid and continuous board insertion checks remain active; real printed friction
  and dimensional tolerance still require the matching USB fit coupon.
- Shared-skill commit `22d62e9` records measuring lateral PCB play independently from
  insertion-stop capture and separating guide, vertical and connector clearances.
- Final source SHA256: `dd8a0f902c218ef0dc0a7108f2577ca003be1c5fa861cfa293b20470bb0be6cf`.
  Full export passes with ten print meshes, 431 coaxial feature pairs, nine standard
  assembly paths and the new lateral USB checks. Independent comparison against `5f84b11`
  finds geometry changes only in the base USB region and its matching fit coupon; all
  eight other print meshes are unchanged, including the head, back cover and ballast lid.
  Base and coupon pass islands, overhangs, thickness and fins. All ten individual slices,
  five production plates and the test plate pass without supports or slicer warnings.
  Production remains 492.4 g / 16.6 h arranged and 492.8 g / 17.4 h individually; base
  120.859 g / 3.789 h, USB test 10.0 g / 1.04 h. README rounded estimates remain valid.
  Both viewer files and all affected images are regenerated. The two pause plates retain
  their 4.6 mm insertion layer and 30 mm bed movement; first-layer walls remain one.


## Superseded removal of complete front platforms (2026-09-28; corrected below)

- The user requests complete removal of the faulty front base insert platforms for now.
  Both posts, their short hull roots, the later broad reinforcement feet, front insert
  holes, two screws and their tool envelopes are removed. Only the two original rear
  M3 x 8 head fasteners remain. This is an intentional temporary state, superseding
  the earlier minimum-three/four-corner request for this revision; complete joint
  strength has not been established. Hardware now totals 16 Ruthex inserts, 12 M3 x 8
  and four M3 x 30 screws, plus the two existing thermoplastic PWM screws.
- The existing head stays geometrically unchanged: its front bearing caps and windows
  remain unused. `rim_bosses()` retains all four historical references for those head
  features; `rim_fasteners()` selects only the rear pair for base posts, holes, active
  screws, tools and metrics. `rim_front_base_raw()` survives solely as the old head
  clearance template. The removed reinforcement is no longer a source module.
- `check_removed_front_mounts()` independently checks empty front post, foot, screw
  and tool regions. The prior base fails its post probes. Both rear clamps retain
  complete bearing, insert wall and blind-floor checks, 5.7 mm screw penetration and
  1.3 mm pocket reserve. Mat overlap is limited to the retained front head seats
  (201.140253 mm3, at most 1.8 mm); head screws have no mat overlap.
- The grey cassette, back cover and ballast lid share production plate 3. Their
  placement must pass the actual H2S plate slice. The cassette's 4.6 mm magnet pause
  pauses all three parts, with the same checked 30 mm bed lowering and return. The
  black head remains on its separate magnet plate 1; base/cross are on plate 2.
- The grey knob has a flush dark pointer matching the housing filament, filling the
  former 1.6 x 7.5 x 0.8 mm groove. Its outside, shaft sleeve, bore and print pose stay
  unchanged. The pointer occupies the first four 0.2 mm layers, 9.6 mm3 in one body.
  Knob colour coverage has zero overlap and zero union difference. Plate 4 holds
  only this two-colour knob and its prime tower; TPU feet remain on plate 5.
  Logical filament 4 uses the same dark PETG profile and colour as slot 1, which
  remains an untagged base slot. Map both to the same physical AMS spool. Viewer
  colours retain the established lifted greys, including the housing-colour pointer.
- Shared-skill commit `6c77d6d` documents that logical base and inlay slots need
  separate roles even when using the same spool, and permits explicitly requested
  same-colour mixed pause plates when their actual pause/resume movements are checked.
- Final source SHA256: `948738a7fa2b685da7ceb4431a0e5d048dce1e5e6e1a5d4457f2481eeaeb63d6`.
  Export passes for ten print meshes, one multicolour part, 397 coaxial feature
  pairs, nine standard paths and 561 assembly pairs. Islands, overhangs, thickness
  and fins are CLEAN for the changed base and knob; the pointer inlay is CLEAN.
  Static tipping estimates are 27.9 mm front margin and 20.5 degrees at 1030.2 g.
- All ten individual slices, five production plates and the USB test plate pass
  without supports or slicer warnings. The grey cover layout occupies 285 x 165.3 mm
  on the 340 x 320 mm H2S bed. Actual slices preserve both insertion pauses before
  4.6 mm, with the bed moving from print Z4.4 to Z34.4 and back. The knob plate uses
  6.37 g grey and 0.68 g dark PETG, including purge/prime material, in 0.55 h.
  Base: 117.552 g / 3.602 h. Production: 491.2 g / 16.6 h on arranged plates;
  single-colour individual diagnostics total 489.5 g / 17.3 h. The USB test remains
  10.02 g / 1.04 h. All plates preserve one first-layer wall and four later walls.
- Independent comparison against `4248800` finds 3779.850 mm3 removed only at the
  two former front platforms and roots; outside them the Boolean delta is numerical
  noise below 0.001 mm3. Head, back cover and ballast lid are byte-identical, and
  every other unchanged part is geometrically identical. The grey knob base is
  exactly the old grooved knob; only its dark pointer fills that groove.
  Both viewer files and affected documentation images are rebuilt. Browser policy
  blocks refreshing the local file URL; the open local tabs require a manual reload.


## Restored narrow front insert posts with deeper wall roots (2026-09-28; before front-face cleanup)

- The source measurements and five-plate release results in this section describe the
  preceding revision. The later front-face cleanup and six-plate layout below supersede
  its wall-connector detail, black support-cross colour and shared cassette/cover plate.

- The user's correction clarifies that only the broad reinforcement feet were unwanted.
  Removing the insert posts and their screws was an incorrect interpretation. Restore
  all four M3 x 8 head fasteners and both front Ruthex pockets, matching the already
  printed head; do not reintroduce the 24/18 mm wide pedestal feet. The preceding
  rear-only release is superseded. Current totals: 18 Ruthex inserts, 14 M3 x 8
  and four M3 x 30 screws, plus the two thermoplastic PWM screws.
- The user additionally requests longer cylinders that continue into the wall.
  `rim_front_base_extension()` sweeps the original narrow post/root profile down
  by 6 mm, retaining its 9.2 mm width. A narrow additional wall overlap below the
  joint prevents the tilted sweep from starting behind the vertical front wall.
  The new underside is cut at world z = 31.2 + 1.1 y (47.7 degrees), keeping it
  support-free and above the PWM controller and its initial service lift. This
  trims the nominal 6 mm extension locally; do not describe it as 6 mm of full
  extra cylindrical length everywhere. The original upper root is retained.
  Insert entries, 4 x 7 mm pockets, screw seats and outer upper diameters stay fixed.
- The original `rim_front_base_raw()` remains unchanged for the head windows. Their
  existing 15 mm downward clearance sweep encloses the new 6 mm extension. No head
  geometry is changed, so the user's printed head remains compatible. The knob
  pointer, closer USB fit, grey covers and shared cover plate remain as released.
- This changes geometric embedment, not a measured breaking-load or creep result.
  Preserve the earlier physical root failure as history; do not claim proven strength.
- The untrimmed tilted prototype left two small floating starting strips and
  overlapped the PWM envelope by 0.109 mm3. The final wall overlap and sloping
  underside remove both problems. Redundant unions of identical cylinder facets
  also caused zero-volume shells; the final single swept body and narrower wall
  link export as one watertight base with no degenerate faces or extra shells.
- Final source SHA256: `8af777e4b417c29a9750ecd9a2564c5d60e102417ac7bac0df69d412be3ff7d0`.
  Full export passes: ten print meshes, one multicolour part, 431 coaxial feature
  pairs, nine standard paths and 561 assembly pairs. All four clamping stacks,
  the front ratchet route and the complete PWM service path pass. Four connected
  material probes per front root are completely filled; measured width is
  9.1914 mm on the faceted surface. Independent underside rays measure 47.726
  degrees. Islands, overhangs, thickness and fins are CLEAN for the changed base.
- Shared-skill commit `6f3972b` records preserving functional insert bosses and
  existing printed mating interfaces when removing reinforcement feet.
- Independent comparison preserves the complete original compact bosses and roots
  (removed stock is only 0.000101 mm3 numerical noise), adding 190.591 mm3 solely
  within the two 9.2 mm wide corridors. The finished underside extends about
  0.56–0.73 mm farther down at sampled local y3.5/6.5/10 after the clearance slope
  trims the sweep. Head, back cover, lid and knob remain byte-identical to `d3bdba2`;
  all other print parts remain geometrically identical. The PWM overlap is zero.
- All ten individual slices, five production plates and the USB test plate pass
  without supports or slicer warnings. Base: 119.654 g / 3.728 h.
  Production: 493.3 g / 16.7 h arranged; 491.6 g / 17.4 h as individual single-colour
  diagnostics. The shared grey plate, dark knob pointer and both magnet pauses
  with 30 mm bed movement remain unchanged. Both viewer files and affected
  documentation images are rebuilt; local file-URL tabs require a manual reload.


## Front-face cleanup, separate cassette plate and grey support cross (2026-09-28)

- The user requests removal of the small protruding pedestal left at the front-wall
  attachment. This is a local surface correction: retain the functional front insert
  posts, their pockets and seats, and all four M3 x 8 head fasteners. The earlier
  instruction to remove the broad reinforcement feet does not authorize removing
  the working fastening interface or changing the already printed head.
- The added wall link had been bounded by a vertical extrusion of `base_outline()`.
  That footprint reaches y0, but the actual curved `base_joint_envelope()` begins
  at y1.2505 at world z38. The mismatch left 74.354 mm3 of exterior stock across
  the two links. Clip only the added link to the true curved housing envelope;
  preserve the functional bosses, their downward sweeps and the existing head.
  This diagnosis comes from an independent geometry comparison, not a wall-thickness
  failure. Check the local silhouette against the neighbouring unmodified wall as
  well as the retained attachment material and complete assembly path.
- The cassette returns to its own production plate 3. The head remains alone on
  plate 1; both keep their 4.6 mm magnet-insertion pauses and 30 mm bed lowering.
  This supersedes the shared cassette/back-cover/ballast-lid pause plate.
- The support cross changes from black to grey PETG, retaining its geometry, spring
  grip and 100% infill. It now shares plate 4 with the grey back cover and ballast lid.
  The base prints alone on plate 2. Plate 5 holds the grey knob and dark pointer with
  its prime tower; plate 6 holds the TPU feet. There are six production plates.
- Filament slots remain 1 dark PETG, 2 grey PETG, 3 TPU and 4 dark PETG for the knob
  pointer. Slots 1 and 4 use the same dark spool. The non-magnet grey plate has no
  insertion pause. Retain the existing print orientations and first-layer wall rule.
- Shared-skill commit `ad70b4f` records clipping root connectors to the actual curved
  housing envelope and independently checking the exterior silhouette, while preserving
  functional above-joint posts and the already printed mating part.
- Final source SHA256: `7f72614137f5de59d5c862275ab7e72ba9a5a2b3b75d14c428e4877bb0866d31`.
  Full export passes for ten print meshes, one multicolour part, 431 coaxial feature
  pairs, nine standard paths and 561 assembly pairs. All four head fasteners,
  ratchet access, retained root material and complete PWM service route pass.
  The front silhouette check compares 378 rays per post against the neighbouring
  wall; maximum profile error is below 0.000001 mm. The preceding protruding
  revision fails this check with a 1.250523 mm outward step.
- Independent final-mesh comparison removes exactly 74.351513 mm3 of exterior
  stock, adds none and leaves the complete above-joint geometry unchanged.
  Interior difference is 0.0000031 mm3 numerical noise. All nine other print
  meshes are geometrically unchanged; head, back cover, lid and knob remain
  byte-identical. The base is one watertight body with no degenerate faces.
  Islands, overhangs, thickness and fins are CLEAN for the changed base.
  These are geometric checks, not a measured breaking-load result.
- All ten individual slices, six production plates and the USB fit plate pass
  without supports or slicer warnings. Base: 119.569 g / 3.714 h. Production:
  493.3 g / 16.8 h arranged, or 491.5 g / 17.4 h as individual single-colour
  diagnostics. The grey cover/support plate occupies 201.3 x 239.5 mm and uses
  74.24 g / 3.23 h. The support cross remains 100% infill with filament slot 2.
  Only plates 1 and 3 pause before 4.6 mm; their actual G-code moves from
  z4.4 to z34.4 and restores z4.4. First-layer single walls and later four-wall
  settings are retained on all plates. The USB fit plate remains 10.02 g / 1.04 h.
- Rebuilt `build/viewer.html`, `docs/index.html` and affected assembly/detail images.
  Source, STL, slicer and project-file hashes agree; both viewer copies are identical.
  Local file-URL browser tabs require a manual reload because browser automation
  blocks that URL scheme. The published HTTPS viewer is checked after deployment.

## Reuse of the coated Engineering Plate (2026-09-29)

- The user's preferred surface is a fully 3DLAC-sprayed Engineering Plate. Preserve
  all six virtual production groups, but place successive jobs on distinct physical
  bed areas so they share a coating. This is not sequential-object printing: remove
  completed parts, brims, towers and purge remnants before starting the next job.
- `BED_REUSE` assigns plates 1/2/3 to the first coating and 4/5/6 to the second.
  Group lower-left positions in bed-local millimetres are Head (15,160), Base
  (15,45), Cassette (180,160), Grey covers and support (15,35), Knob (265,35),
  and TPU feet (255,220). The knob's tower origin is (245,90). Keep these saved
  positions when opening or slicing the 3MF; Auto Arrange would defeat this plan.
- The shared slicer checks actual first-layer deposition, including extrusion arcs,
  brims, skirts and prime towers, with 5 mm separation between different jobs in
  each coating group. Group bounds alone are not the final contact measurement.
  Preserve ordinary start code and calibration. The H2S load line at x250..290,
  y-0.5 and firmware-controlled wiping/probing are reused machine operations;
  this footprint check does not claim those areas remain untouched.
- Installed H2S Generic PETG and Generic TPU profiles provide Engineering Plate
  temperatures of 70/70 and 35/35 degrees C respectively (initial/subsequent).
  No custom temperature, adhesion setting or start-code change is required.
  The model source and all part geometry are unchanged by this layout update.
- Shared-skill commit `6ae00e4` adds the Engineering Plate preference, reusable-bed
  placements and actual contact verification. Its 40 regression tests and complete
  fresh template loop pass, including the template's three-job coating group and
  multicolour tower. The project's `scripts/` is installed from that exact tool state.
- The complete FUMEX slicer run passes: ten diagnostic parts, six production plates
  and the USB fit plate, without warnings or supports. Both coating groups pass
  the conservative 1 mm contact-grid check with 5 mm clearance. Saved and sliced
  archives retain Engineering Plate and the requested bed-local object bounds.
  Magnet pauses remain on plates 1 and 3 at 4.6 mm with 30 mm extra clearance;
  the grey cross keeps 100% infill, and the knob retains its separate dark pointer.
  Totals remain 493.3 g / 16.8 h; the USB fit plate is 10.02 g / 1.04 h.
  Both viewer copies are rebuilt from the unchanged assembly exports.


## Screw-fastened cassette and grey head (2026-09-29)

- The user found the magnetic cassette unstable and requested M3 screws with heat-set
  inserts, then changed the head to grey to match the cassette. Four M3 x 8 ISO 7380
  Torx screws now use the existing corner axes. The cassette is 4 mm thick, with
  Ø3.4 mm through-holes and flat Ø6.4 x 1.9 mm counterbores. These leave 2.1 mm of
  bearing material and fully recess the 1.65 mm button heads 0.25 mm below the face,
  as explicitly requested by the user. The 1.2 mm edge bevel leaves 2.8 mm of straight
  rim. The head's Ø8.4 x 9 mm bosses contain Ø4 x 7 mm Ruthex RX-M3x5.7 pockets,
  opening towards the intake and retaining 2 mm blind ends. Nominal screw penetration
  is 5.9 mm with 1.1 mm pocket reserve. The
  head intake thickness remains 5.6 mm, preserving the fan/filter positions.
- Both magnetic printed parts need replacing with this matching head and cassette.
  The base and current back cover remain compatible. Existing support-cross sockets,
  head-to-base screws, fan mounting and outside contours are preserved.
- Remove magnet cavities, hardware bodies and obsolete overlap exceptions/checks;
  replace them with actual screw bearing, insert-wall/floor, axis alignment, tool
  access and cassette-removal checks. Clear the project insertion-pause configuration
  and verify that the produced 3MF and sliced jobs contain no scheduled magnet pauses.
  The general 30 mm extra-clearance preference remains available for future insertion
  jobs; it is not an active action in these pause-free plates.
- Total bought fasteners: 22 Ruthex RX-M3x5.7 inserts, 18 M3 x 8, four M3 x 30
  and the two 2.5 x 8 thermoplastic PWM-board screws. Magnets are removed
  from the BOM and mass accounting. Head uses grey filament slot 2; only the base uses
  dark slot 1 as its main material, with the knob pointer retaining dark inlay slot 4.
- Keep six production plates and the existing Engineering Plate/3DLAC coating groups:
  Head → Base → Cassette, then Grey covers and support → Knob → TPU feet. The support
  cross remains grey with 100% infill. Preserve bed-reuse positions and recheck actual
  first-layer printed areas after the new slices.
- Shared skill commit `e197b5a` documents retiring obsolete embedded-hardware pauses and
  sliced-job metadata when switching to post-print fasteners, without disabling
  unrelated insertion jobs or promising an unvalidated retrofit.
- Final source SHA256: `97a7b945c5bd19014dd3c990a333d07f953c85834c60fa1913c5289233602f46`.
  Full export passes: ten print meshes, one multicolour part, 595 assembly pairs,
  459 coaxial feature pairs, ten removal paths and 22 insert probes. Head and
  cassette are each one closed body with no cavity shells. Both changed parts pass
  islands, overhangs, thickness and fins with zero findings. G2's maximum sampled
  normal step remains 7.827 degrees.
- Independent checks confirm all four heads are 0.25 mm below the face, the complete
  2.1 mm cassette bearings and 2 mm insert-pocket floors remain present, and the
  fasteners clear the filter envelope by at least 0.57881 mm. Straight driver and
  insert-tool access pass. Comparing the head outside the four fastening regions
  changes only 0.0000875 mm³ of numerical mesh noise. A negative fixture using the
  former sealed-magnet head fails the new bore check, as intended.
- Tool-presence probes are inset by up to 0.026 mm to account for the OpenSCAD
  circles' facet sag; the independent full-size bit/holder clearance envelopes and
  exact straight approach sweeps retain their nominal dimensions.
- All ten diagnostic slices, six production plates and the USB fit plate pass
  without warnings or supports. The production project totals 478.7 g / 16.2 h;
  the head and cassette account for 271.9 g / 8.1 h. The USB fit plate remains
  10.02 g / 1.04 h. Head uses grey slot 2, the cross remains solid, and the knob
  retains its separate two-colour plate. Both coating groups pass the actual
  first-layer contact check with 5 mm clearance, including the knob's prime tower.
  Engineering Plate and the existing bed-local placements remain saved.
- Independent release inspection matches both project 3MF hashes, the embedded
  production meshes and the source/STL hashes. Neither project carries custom
  per-layer pause metadata, and all seven actual sliced archives (six production
  plates plus USB fit) contain zero manual pause commands. The regenerated base,
  support cross and USB base coupon have zero geometric difference from the
  preceding release despite binary STL ordering changes.
- Revised estimated assembly mass is 1005.6 g; the modelled front tipping margin
  is 29.2 mm and the angle is 21.7 degrees. These retain the documented estimated
  hardware masses and effective print density, not physical load testing.
- Both `build/viewer.html` and `docs/index.html` are rebuilt from this assembly and
  are byte-identical: 27 viewer items, including four M3 x 8 cassette screws and
  no magnet bodies. Head and cassette use the same lifted grey viewer colour.
  The assembly, exploded, back, head-mount, cassette-fastener section and fan-cable
  images are regenerated. The older magnet section remains only as evidence for
  its explicitly superseded dated report.


## Rounded cassette corners (2026-09-29)

- User requested cassette corners rounded like the head. The cassette now starts from
  its actual 138 x 143 mm bounding outline with four tangent R6 corners, then receives
  the existing 1.2 mm front bevel. Visible-face radii are R4.8. This supersedes the
  clipped inset-head contour: clipping removed the lower rounds and cut the upper
  R5 arcs before they reached a tangent side edge, producing an approximately
  60-degree direction change.
- Cassette thickness remains 4 mm; the Ø6.4 x 1.9 mm head pockets, Ø3.4 mm bores,
  M3 x 8 screws, all fastening axes and grey material remain unchanged. The head
  and its insert pockets are unchanged. Existing screw-version heads need only the
  new cassette for this refinement; upgrading the former magnetic interface still
  requires both the screw-version head and cassette.
- Retain all six production plates and both Engineering Plate/3DLAC coating groups.
  Recheck corner tangency, complete screw-bearing material, printability and the
  actual first-layer contact areas before publishing the updated 3MF and viewer.
- Final source SHA256: `0baee0059d26471f6d7717826be5ad933764aecceca64b63d2efd2cb25b46526`.
  Full export passes ten print meshes, one multicolour part, 595 assembly pairs,
  459 coaxial feature pairs, ten removal paths and all 22 insert probes. Existing
  cassette clamps pass unchanged, including their fully recessed screw heads.
- The new actual-mesh corner check measures 888 radial rays over six depths,
  including the bevel, and inspects the four tangent transitions. Maximum radius
  error is 0.007353 mm, with 5.627-degree maximum facet steps around the arcs and
  approximately 2.812-degree turns at the eight straight-to-arc endpoints. These
  are the intended polygon sampling, not the former roughly 60-degree crease.
  The old clipped cassette fails this regression.
- Independent comparison with `31d6f0c` removes 113.564945 mm³ only inside four
  7 x 7 mm corner regions and adds no material. Bounds, thickness, grid and screw
  bores/bearings are unchanged. The four corner centres are (9.5/135.5, 55/186)
  in local XZ. The front bevel remains 1.200195 mm after BOSL2 quantization.
- Islands, overhangs, thickness and fins pass with zero findings on the changed
  cassette. The estimated assembly mass is 1005.5 g; the modelled front tipping
  margin remains 29.2 mm and the angle 21.7 degrees.
- Shared skill commit `a8efb7b` records the general lesson: construct rounded
  corners inside the final outline bounds before beveling; a later width clip
  can truncate the arcs and remove tangency even when a radius parameter exists.
- All ten diagnostic slices, all six production plates and the USB fit plate pass
  without warnings or supports. Production totals are 478.6 g / 16.2 h, including
  the cassette at 46.19 g / 2.25 h. Both Engineering Plate coating groups retain
  their saved positions and pass the actual first-layer contact check. No insertion
  pauses are scheduled. Source, all slicer input STL hashes and both 3MF hashes match
  the generated verification reports.
- Both viewer copies are rebuilt and byte-identical, with 27 current items.
  Assembly, exploded, rear and cassette-fastener detail renders are regenerated.
