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
- `profile_sweep_y()` uses BOSL2 `offset_sweep()` and `os_chamfer()` on the finished head, cover and cassette outlines. The bevels are measured from their actual end planes, so the former hull-tip thickness no longer changes their height or width. The base bottom bevel uses the same operations on `joint_plan_points(0)`.
- This is a targeted edge-profile change. The tangent R3.5 plan rounds along the long sides of the head and cover are deliberately retained; do not add a second bevel across them. The upper-corner blends and the joint loft remain the specific G2/G3 geometry described below.
- BOSL2 quantizes these offsets to 1/1024 mm, so a 1.2 mm chamfer finishes at 1.200195 mm. The cutters must extend beyond that end; the head/cover tools also offset the outside profile one grid step and add the same amount to the chamfer to avoid a vanishing cut against the native outline. Do not trim the tool at exactly `edge_c` or remove that overlap. The local helpers are named `bounds_rect` and `axis_orient` to avoid BOSL2's `rect` and `orient` names.

## User constraints and preferences

- Bench tool, no child-safety requirement. Plain and functional: no logo, no QR code, no decorative grooves (user, 2026-09-21).
- Two colours, part by part: housing parts in Bambu PETG black, the parts you touch (cassette, knob) in grey. No inlays inside a part, so no prime tower.
- **The viewer colours are deliberately not the filament colours** (user, 2026-09-22): black PETG renders as a
  silhouette on screen and the geometry disappears, so `VIEWER["parts"]` uses lifted greys. Do not "correct"
  them back to #1a1b1d; the real colours live in `FILAMENTS`, the plate names and the README.
- Screws only ISO 7380 button head Torx from the user's set (M3 × 6/8/10/12/16/25). The four fan screws M3 × 30 are a deliberate extra purchase — a 25 mm fan frame cannot be screwed with anything shorter, whichever side the screw comes from (the user first chose M3 × 25 from the set, which is geometrically impossible; corrected 2026-09-21).
- Ruthex RX-M3x5.7 per datasheet: hole 4.0, pocket depth ≥ 6.7, wall ≥ 1.6, pressable from an accessible side.
- Printer Bambu Lab H2S with AMS.

## Measured hardware

Shared parts are the ones measured for LEO-AC1 on 2026-09-15/18 (battery, PWM controller, potentiometer, charge module, USB-C module, rocker switch); the table there is the source. New here:

| Part | Value | Status |
|---|---|---|
| Fan Arctic P12 Pro (PST) | 120 × 120 × 25 mm, 185 g, 600–3000 rpm, 77 cfm / 131 m³/h, 6.9 mmH₂O, 12 V, **0.33 A**, start-up 3.3 V, 0 rpm below 5 % PWM, cable 400 + 80 mm, 0–40 °C | data sheet (ACFAN00306A) |
| Filter mat | cut by the user from a cooker hood mat to about 120 × 120 × 17 mm, white fleece with a dark carbon layer | user, 2026-09-21, hand-cut — the chamber is 121.5 mm and the lip 2.25 mm wide, so ±1 mm on the cut is fine |
| Magnets | 8 × neodymium disc Ø10 × 3 | user's part, **not yet measured**; pockets are Ø10.3 × 3.2 per the skill's glue-in rule |
| Masses for the tipping check | fan 185 g (data sheet), battery 150 g, PWM board 12 g, mat 15 g, magnets 18 g, rest estimated | **estimates**, reported as an open item |

## Current design state

- The housing bends: `base` stands upright, `head` leans `tilt` = 15° forward above it, so the intake looks down at the work (user: "erst senkrecht nach oben, und dann nach vorne im Winkel"). Head modules are written in an untilted frame and placed by `head_at()`; `print_project.py` mirrors that transform in `_tilt()` for the probes.
- Base and head share one 145 × 72 footprint, so the head's floor closes the electronics bay exactly — no extra cover, and the joint is one flat plane cut by `joint_halfspace()`. 145 mm width is set by the Ø10 magnet pockets in the corners of the intake face, not by the fan.
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
    pressed 6.6 cm3 out of the mat; `mat_squashed_percent` is now 0.0.
- The cassette stands 4.5 mm proud of the intake face and cannot be let into it: the head prints intake-face-down,
  so a recess for it would be a 5687 mm2 horizontal ceiling over the chamber. It cannot get thinner either - the
  magnet pockets are 3.2 deep and `analyze.py thickness` wants 1.2. The final-contour rim bevel is `cass_c` = 1.2 after the G1 audit fix; the narrow side contour
  limits it at the magnet pockets. Straight rim depth is 3.3 mm.
  At the joint the cassette therefore reaches 3.9 mm in front of the base face - reported to the user 2026-09-23;
  the only way to close that is a plinth on the base front, which has not been built.
- `head_outline(inset, square_bottom)`: the head shell keeps the square bottom corners so its side walls meet the
  base rim without a step; `head_back` and `cassette` pass false and keep the radius all round (user,
  2026-09-23). Neither lands on the base rim - the cover has the head wall behind it carrying the silhouette,
  the cassette lies on the intake face - so the radius costs no flushness.
- The joint plane rises 15 degrees to the back and therefore meets the vertical back face of the base at 75
  degrees: an acute edge across the full width, right where the back cover lands (user, 2026-09-23: "die
  scharfe kante weg wo die rueckwand aufliegt"). It is cut at 45 degrees to the joint plane, placed with
  `head_at()` so it mirrors the chamfer on the cover's lower edge; both sit behind `head_y[4]`, where the rim
  carries no head wall. The cover's lower edge had only 0.9 mm of the rim chamfer left on it, because the
  joint plane cuts that chamfer off `cover_gap` above the outline's own bottom edge; now it is the full 1.2.
- Filter cassette held by four magnet pairs in open pockets (skill rule: glue one side in, place the counterparts on them, then glue — polarity is then automatic). Two 45° finger scoops in the side edges of the intake face get a finger behind the flange; two half-round notches in the intake lip get a finger behind the mat.
- **The chamber has a rear lip too** (`mat_stop()`, user asked 2026-09-23 what stops the mat falling into the
  fan - nothing did). The mat's back face rested on the four gusset corners only, 7.8 % of it, with 10.5 mm
  of clear air to the fan frame, while the fan pulls it that way with about 1 N at 69 Pa. The lip closes the
  bore from `chamber_sq` to `open_sq` on a flank of `mat_stop_rise` = 1.5 mm of depth per mm inwards - at 45
  degrees `analyze.py overhangs` counts it, the head prints intake-face-down and the lip hangs inwards. It
  merges into the chamber tube so it grows out of the bore wall instead of starting as a knife edge.
  `checks()` reports `mat_free_travel_mm` = 1.62 and asserts it stays under a quarter of the way to the fan.
  - This is a rigid-envelope check, not proof that the flexible mat cannot reach the rotor. A direct
    mesh measurement on source SHA `544894c9fc4dc5176798e87bd9ad6000a1cbd028eab20a550ffad9b17326cd1d`
    (2026-09-23) gives 10.50 mm from the nominal mat rear face to the fan frame's front plane; first rear-lip
    contact after about 1.76 mm of rigid translation leaves 8.74 mm. The simple 1.62 mm formula is an
    approximation to the actual hull/tessellation. The central 117 x 117 mm opening has no backing grid:
    bowing and loose fibres are not modelled, and `fan_visual()` is not a measured blade envelope. A rear
    support grid or a physical maximum-speed test is needed before claiming that rubbing is excluded.
- The mat is held by the intake lip (opening 117 in a 121.5 chamber, 2.25 mm per side). It is pressed in and pulled out past that lip — a rigid-body path check cannot show this, so `filter_out` is not a checked path but a documented limitation.
- **Head screws: 2 × M3 × 8 in one row at x 25/120, y 66** (user asked 2026-09-23 whether every screw can
  actually be reached - four of four could not). Vertical access inside the head exists only in the plenum
  behind the fan: further forward the filter tube or the fan stands over the rim, and the 5.75 mm channel
  beside the tube takes no bit. y 66 is the minimum that lets the Ø10 base boss reach the back wall it hangs
  from. Mechanically it is also the right row - the head group's centre of mass is 22 mm in front of the joint, so
  the front of the joint is in compression and only the back needs holding down. The back cover's lip is
  notched over the screw heads. `rim_boss_bodies()` is clipped to `base_outline()`: tilted, the 45 degree
  run-out towards the back wall reached 2.4 mm past the back face.
- **Driver access is a checked property.** `drivers_*()` put a Torx bit and its holder (4/6.35/13 mm) on
  every screw head; they are ordinary assembly bodies, so the pairwise overlap check is the test. The
  ALLOWED_OVERLAPS entries for them are assembly stages, not excuses: the head screws go in before the back
  cover, the ballast lid is closed before the head goes on.
- Ballast lid posts moved to x 45/90 (from 30/115): the rim bosses now hang over the trough left and right,
  and the USB-C channel and the tie loops block everything right of x 90. Vent slots 14 mm instead of 16,
  so the rim bosses clear them.
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
  - 3.5 is capped by the magnet pockets in the intake face, not chosen freely. The pocket has to clear the
    rounded plan corner by 1.2 mm and the intake opening by 1.2 mm, which at R6 leaves an empty window
    (inset >= 12.35 and <= 10.39). At 3.5 the window is 9.85 to 10.39 and `mag_off` 62.5 puts the magnets
    at inset 10: 1.3 mm to the corner, 1.8 mm to the opening.
  - The cassette stands `cass_t` in front of the footprint, so `cass_prism()` runs the prism on forward at
    the width the footprint has at y = 0 rather than rounding a second time in the wrong place.
- The back cover runs the full height of the head (user, 2026-09-22); the head floor stops at its inner face. Its lower edge keeps `cover_gap` = 0.3 mm off the joint plane, otherwise the two coplanar faces grind along each other on the way off and `cover_off` fails on facet-level overlap. Four screws, not six (user).
- Feet: four TPU pads, one M3 × 8 each plus a Ø3 peg against turning. A keying pocket in the bottom face was 275 mm² of flat overhang per foot, so it went.
- Tipping: `checks()` computes the centre of mass from mesh volumes and part masses and requires ≥ 15 mm to every foot edge. Currently 30.6 mm at the front, 23.3°, 1.02 kg (13.8° when this started).
  - Feet fully under the housing (user, 2026-09-22: pads sticking out past the rounded corners looked wrong), x 16/129, front pair at y = 8 so the pads end flush with the front face. Tipping edge y = 0.
  - One ballast trough behind the cell, x 3–96, y 53–71, rim 35, with a screwed lid: 39 cm³, about 184 g of loose iron at an assumed 4.7 g/cm³ (60 % packing). The cell moved forward to make room (user: "du kannst die batterie einfach nach vorne rücken und hinten ne größere wanne machen"). `ballast_env()` is the trough volume minus `base()` itself, so foot boss, posts and rounded corners are cut out of it and the reported mass is what really fits.
  - `bat_cy` is limited by the **tilted** run-outs of the front head screw bosses: built at y 4–14 they reach world y ≈ 18 at z ≈ 30 after the tilt, which is where the cell's shoulder is. 35 clears it, 34 does not (0.14 mm³).
  - Lid on four Ø10 posts in the trough corners, each 3.5 mm off both walls so its circle covers the corner point — at Ø8 it left a sealed sliver void that exports as a second body. The trough walls end `ball_rim` = 0.4 mm below the posts so no two faces of the base share the plane z = 35; coplanar face unions there produced degenerate triangles.
  - **M3 plastic-forming screws straight into the posts, no inserts** (user, 2026-09-22). Core hole `pt_core` = 2.5 mm; that is a starting value, verify the holding torque on a test print.
  - The lid has no lip over the front wall: the cell has to lift past it (`battery_out`). The current `lid_off` check moves the lid together with its charge module and heatsink 10 mm up after the head and battery have been removed; complete extraction still needs a tilt.
  - The free space in front of the cell (about 50 cm³) is the wrong side of the centre of mass and is deliberately left empty.
- Charge module upright on the ballast lid, directly below the plenum slots (user, 2026-09-23: both sides of the board should get air). Components face forwards, heatsink backwards. Two narrow holders take the short edges and leave both broad faces open; see Electrics below for dimensions and the physical-fit limits. The earlier flat tray and bay-floor brackets are no longer built.
  - **The air route starts in the plenum:** the six slots in the head floor connect the fan's filtered outlet side to the component and heatsink passages, which lead to the back-wall slots. The surrounding 5.75 mm channel between filter tube and shell also remains open to the plenum. Geometric corridors are checked; flow rate, natural convection and cooling performance are not measured.
  - The vent is a row of six slots, not one opening: printed intake-face-down the head floor is a vertical wall, and a single 38 mm opening left a 113 mm² flat bridge at its far edge.
  - Ventilation slots in the back wall (user: slots, not honeycomb, and not staggered) sit above the ballast
    lid - an assert keeps them there, below it they would let the offcuts out. Aligned they export clean
    here (12 slots, 2 mm wide, 5 mm pitch); the collinear-corner trap that hit the old slot rows did not
    reappear, so `vent[4]` is 0. If it ever does come back, stagger before reaching for anything else.
- Ballast trough over the full width, lower, with the USB-C socket above it (user, 2026-09-22): x 3–142, y 53–71, rim 26, 44.5 cm³ or about 209 g. 24.5° of tip angle at 1.04 kg.
  - Everything above the lid has to leave it 10 mm of lift: the USB-C channel went to z 45 and the cable tie loops to z 45. The channel's floor is only `usbc_floor` = 6 mm deep, because a full-length floor at that height is a 198 mm² flat overhang and a 45° gusset would stand in the trough.
  - The switch moved to y 37 / z 34: its well box reached into the trough's front wall, and higher up its bezel poked through the joint plane. Its pins in turn forced the PWM board 4 mm left (`pot_x` 108).
  - `lid_off` checks the loaded group (`ball_lid`, `chg_module`, `chg_sink`) 10 mm up. Getting it out of the bay after that is a tilt, which a rigid axis-aligned path cannot express; the lid's front right corner is notched so it clears the switch well.
- The switch well flanks rise 1.25 mm per mm instead of 1.0: at exactly 45° `analyze.py overhangs` counted them.
- The rocker switch stands upright in the right wall (long side vertical): the base prints bottom down, so its panel cut-out is a sideways hole and the bridge over it is 12.2 mm instead of 19.2 mm.

## Electrics — two things that belong in the README and in the build

1. **0.32 A against 0.33 A.** The LFUPSMA charge/boost module is specified for 0–0.32 A at 12 V, the P12 Pro draws 0.33 A at full speed. The top of the knob range is therefore at the module's limit: it gets warm and starting at 100 % may brown out. Start slow, then turn up.
2. **Charger heat — upright board with open air passages.** The CN3058E is a linear charger: at 1 A
   from 5 V it turns about 1.6 W into heat while charging. The earlier closed-bay, external-heatsink and
   flat-tray arrangements have been replaced. The user asked to turn the board so air can reach both
   its components and its heatsink; the current holder is on the **ballast lid**, under the six plenum slots.

   - The measured 32.2 × 11 × 1 mm PCB now spans x 53.9–86.1, y 59.5–60.5 and z 32.2–43.2. Its
     components face forwards to y 56.8. The 14 × 14 × 6 mm heatsink and 1 mm pad face backwards,
     spanning x 76.6–90.6, y 60.5–67.5 and z 30.7–44.7. The heatsink clears the lid surface by 1.7 mm.
   - Two narrow end holders replace the surrounding tray. The left guide has a 1.4 mm groove for the
     1 mm PCB, 0.2 mm clearance per face, and grips only z 35.2–38.4, leaving the end corners exposed for
     the OUT wires. The right holder has a front cheek and end stop; a rear cheek would hit the overhanging
     heatsink and pad. Two narrow seats support the lower PCB edge. The sloped cheeks print without support.
   - The board and heatsink lower in from above; `chg_off` includes the real holder and proves their
     vertical removal. Stops check both forward and backward translation. These open-top guides do not
     prevent lifting the board by its wires. `lid_off` moves the loaded lid 10 mm up; subsequent withdrawal
     and tilting are not checked. Leave wire slack for service and remove the head and battery first.
   - The closest pad-to-right-guide clearance is only 0.2 mm. Check the real pad edge, solder joints and
     OUT/BAT/IN wire exits before final assembly. The component envelope still reserves 2 mm at each end;
     it does not model the soldered wires read from the LEO-AC1 photos.
   - `check_charger_air()` checks free volumes in front of the components and behind the heatsink, anchored
     to the actual mesh faces. Continuous Ø1.2 mm probe corridors connect each space through an existing
     head-floor slot to the plenum and through a rear vent to the outside. The component-side route passes
     round the board's left end; the heatsink route exits directly behind it. These are geometric access
     checks, **not CFD, an airflow measurement or proof of adequate cooling**. Check closed-housing charging
     temperatures with the actual wiring, both with the fan running and stopped.
   - `ball_post_x` remains 12/40 and `ball_dish` x 25, clear of the holder. The upright holder makes the
     printed ballast lid 12.4 mm tall overall.

   Still available if it is not enough: swapping the ISET resistor (marked 122, 1.2 kΩ) for 2.4 kΩ halves the charge current to 0.5 A and the heat to about 0.85 W, at 12–13 h for a full charge. The user chose the heatsink route alone for now.

## Support-free printability (reviewed 2026-09-23 on the user's request)

All seven parts print without supports. Evidence and the remaining soft spots:

- `analyze.py islands`, `overhangs` (100 mm²), `fins` and `thickness` are all CLEAN on all seven parts.
- `analyze.py overhangs --min-area 5` lists 27 small downward faces, all of them understood: four Ø3.3 foot peg holes and four Ø4 insert pockets in the bay floor (circular bridges, 6–10 mm²), the six vent slots in the head floor (10.8 mm² each), the two finger scoops in the intake face (45 mm² flat cone ends 2 mm above the bed), the USB-C channel floor (85 mm², a 5.8 mm ledge off the back wall) and the two cable tie loops (28 mm² each, 6 mm off the back wall). None is a floating island; every one of them grows out of a wall or bridges a hole under 15 mm.
- The current Bambu CLI slices all seven parts and all four plates without support. The individual `base` and `head` slices each report "floating cantilever", also present before the G2/G3 changes. The base candidates are the USB-C channel ledge and the tie loops. The warning locations have not been conclusively isolated; keep these warnings visible in the report and inspect the small bridges on the first print.
- Deliberately **not** fixed: a 45° gusset under the USB-C channel floor or under the tie loops would reach 6 mm down and eat exactly the clearance the ballast lid needs to lift out (`lid_off`). A 6 mm ledge in PETG is routine; the lid coming out is not negotiable.
- The two tall bridges in the design are the rocker switch panel cut-out (12.2 mm, which is why the switch stands upright) and the magnet pockets in the intake face (Ø10.3, in the bed face).

## Audit of 2026-09-23 (`docs/audit-2026-09-23.md`)

An external audit of commit `a90c581`. What it found and what happened to it:

| ID | Finding | Status |
|---|---|---|
| A1 | The switch notch in the ballast lid opened the trough into the electronics, 9 x 3.5 mm | fixed: `ball_switch_fill()` closes the trough under the notch, behind the switch body |
| A2 | The USB-C board could be pushed 15 mm into the bay by a cable | fixed: the channel keeps a 2 mm end wall (the inner cut starts at the board, not 3 mm in front of it) with a notch for the wires; new `usbc_in` stop |
| A3 | Assembly step named the wrong fan direction, and "fleece side first" contradicts the parts list | fixed in README: blowing towards the cover, and the mat's end position is named instead of the order |
| A4 | The tab over the charge module made both straight insertion and straight removal impossible; `chg_off` did not include the lid | fixed: tab removed; the current upright board lowers into open-top end holders, and `chg_off` includes `ball_lid` as an obstacle |
| A5 | M3 x 12 reached 0.9 mm past the core hole and the head bore on a 1.1 mm ring | fixed: `lid_pocket` = 1.2 (ring 1.8 mm), screws M3 x 10, `screws_lid` are assembly bodies now, and an assert ties the length to `pt_depth` |
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
- The rear ballast-lid screws and posts move from y 67.5 to 66.2, preserving access for the existing 6.35 mm driver. Adjacent head pockets retain a 1.3 mm web. Base, lid and screw bodies all derive these positions from `ball_posts()`.
- The base uses the export tool's existing CGAL fallback; the resulting binary STL is closed, one body and has zero degenerate faces. Do not force an invalid fast-backend result or repair it after export.
- `check_top_corners()` rejects the previous crease in all four outer corner regions and probes a complete 1.21 mm radial material ring around each head magnet pocket. Face-normal comparisons exclude numerical triangles below 0.001 mm altitude; full mesh validity remains independently mandatory. This is a targeted mesh regression, not a global C1 proof.
- `check_joint_profile()` compares actual base/head silhouette spans in five cross sections, 2 mm either side of the joint. Old excess: 2.58–2.61 mm; new: 0.403–0.408 mm, reflecting the remaining transition below the joint. The accepted band is -0.1 to +0.6 mm. This guards the shoulder; it does not certify every surface tangent or erase the intentional seam chamfers.
- Follow-up evidence and images: `docs/rounding-2026-09-23.md`. Fresh full checks: seven mesh types, ten physical parts, 394 coaxial feature pairs, eight paths, 435 assembly pairs; all four analyses CLEAN. Estimated assembled mass 1008.4 g and tip angle 21.4 degrees. Slicer: 470.5 g / 15.4 h across four plates; 470.9 g / 16.1 h as individual part jobs.

Everything the audit lists as "verify on the real part" stays open: magnet force, knob press fit, switch body depth, the charge module's soldered connections against the upright end holders, insert pull-out, bridge quality on the small overhangs, and every thermal and airflow figure.

## Open items

- Magnets Ø10 × 3 not measured; holding force through the printed faces not tested. Print the fit test before committing to the full print.
- Part masses for the tipping check are data-sheet or estimated values, not weighed (reported by `print_tools.py` as an OPEN item).
- The knob bore is nominal 5.8 mm with zero clearance, as in LEO-AC1 — validate the push fit on the real knurled shaft with a test print.
- Rocker switch body depth behind the panel is still the assumed value from LEO-AC1.
- Charge module: verify solder joints and wire exits at the two end holders, the 0.2 mm pad/right-guide clearance, and wire slack for the loaded lid's service path. Check temperatures while charging in the closed housing, with the fan on and off; free geometric air corridors do not establish cooling performance.
- Filter pressure drop and capture distance are not modelled. The P12 Pro is pressure-optimised (6.9 mmH₂O), which is why it suits a mat, but the working point is unknown.

## Verification and known limits

`docs/verification.json` holds the full report. Checked: closed meshes and body counts, bed placement and build envelope, all 435 assembly pairs checked (14 documented assembly-stage or intentional-fit exceptions), coaxial round features, contacts, stops, eight assembly paths, heat-set insert pockets, the intake lip, mat displacement, and the centre of mass over the foot polygon.

Not checked: flexible deformation (the mat and the TPU feet are rigid bodies here), strength, thermal behaviour, airflow, and anything about the real hardware that has not been measured.

## BOSL2 and upright-charger verification (2026-09-23)

- Final report: `docs/bosl2-charger-2026-09-23.md`; source SHA `544894c9fc4dc5176798e87bd9ad6000a1cbd028eab20a550ffad9b17326cd1d`.
- Seven valid print meshes / ten physical parts, 394 coaxial feature pairs, 435 assembly pairs and eight paths. All four printability analyses are CLEAN. The head thickness sampler retains its pre-existing numerical Trimesh warnings (64,906 valid samples of 65,060); this is not a complete wall-thickness proof.
- `check_rim_chamfers()` measures 24 exported profiles; maximum error 0.00020 mm. Both charger stops engage at 0.25 mm. `check_charger_air()` confirms two unobstructed connected passages at the real board/heatsink faces. These regressions reject the old chamfer and flat-board layouts respectively.
- Slicer: all seven parts and four plates pass with supports disabled; 469.7 g / 15.3 h as arranged plates, 470.0 g / 16.1 h as individual jobs. Existing base/head floating-cantilever warnings remain. The upright charger lid adds no warning. Estimated assembled mass 1007.6 g, tip angle 21.4 degrees.
- STLs, 3MF, README images and viewer are regenerated. No physical print or thermal/airflow test has been performed.
