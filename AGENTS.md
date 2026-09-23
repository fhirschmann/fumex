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
- The base has a nominal 145 × 74 footprint; its upper loft meets the projected head outline at the joint, so the head's floor closes the electronics bay without an extra cover. The joint is one flat plane cut by `joint_halfspace()`. The 145 mm width is set by the Ø10 magnet pockets in the corners of the intake face, not by the fan.
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
- Filter cassette held by four magnet pairs in open pockets (skill rule: glue one side in, place the counterparts on them, then glue — polarity is then automatic). Two 45° finger scoops in the side edges of the intake face get a finger behind the flange. The redundant half-round mat notches were removed at the user's request on 2026-09-23; the intake lip is continuous.
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
- **A separate support cross now backs the mat** (`filter_support`, user, 2026-09-23). It is the eighth
  print type, making eleven physical printed pieces including the four feet: black PETG, 122 x 122 x 8 mm,
  printed with the mat-facing side flat on the bed and the four end posts upright. Integrating the cross
  into the intake-face-down head would create long unsupported bridges across the chamber.
  - `mat_support` defines 2.4 mm wide, 3.2 mm deep central bars. In the untilted head frame their front
    is y 22.5, 2.3 mm behind the nominal mat rear face at y 20.2; their back is y 25.7, 5 mm before the
    fan frame front at y 30.7. Both cross faces have 0.4 mm edge chamfers. The four remaining open
    fields are about 57.3 x 57.3 mm; this is sparse support, not a full backing grid.
    Its measured projected obstruction is 561.039 mm² out of the rounded opening's 13,681.093 mm²,
    or 4.101 %, leaving 13,120.054 mm² open. This is an area measurement, not a pressure-drop prediction.
  - Four widened end pads are 5 mm across and 3 mm long radially. Their pockets open to the rear:
    front y 22.3, radial extent 57.8..61.2, width 5.4 mm. The posts extend to y 30.5, so the pocket
    fronts and fan frame allow 0.2 mm nominal movement in each axial direction. The outer tube wall
    beyond each pocket remains 2.55 mm thick. There are no added fasteners or snap tabs.
  - Insert it from the rear before the fan-and-cover assembly, mat-facing cross forwards and posts
    backwards. The fan frame traps the posts; verify actual frame contact at radial positions
    58.5..60 mm on all four sides. The full fan envelope cannot prove that these local surfaces exist.
    Removing the fan and cover releases the cross; ordinary mat changes remain through the front.
  - The cross reduces the unsupported mat span but its PETG bars and the mat can still bend. No
    physical strength, long-term creep, loose-fibre or maximum-speed rubbing test has been performed.
    Do not turn the nominal 5 mm central-bar/frame gap into a guarantee of rotor clearance.
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
- **The ballast lid now uses exactly two M3 x 8 screws and two Ruthex RX-M3x5.7 inserts** (user,
  2026-09-23). The Ø10 posts stand at (x, y) = (10, 63) and (135, 63), with Ø4 x 7 mm insert pockets
  opening upwards. This replaces all four plastic-forming screws and their core holes. With the
  3 mm lid and 1.2 mm head pockets, nominal thread reach is 6.2 mm. Total hardware is 16 inserts,
  12 M3 x 8 and four M3 x 30 screws. Earlier lid-post positions at x 30/115, 45/90 and 12/40,
  including the G3 rear-row adjustment to y 66.2, are historical. The head vent slots remain 14 mm long.
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
- Tipping: `checks()` computes the centre of mass from mesh volumes and part masses and requires ≥ 15 mm to every foot edge. Use the current verification report for results. An early layout gave 30.6 mm at the front, 23.3°, 1.02 kg (13.8° when this started).
  - Feet fully under the housing (user, 2026-09-22: pads sticking out past the rounded corners looked wrong), x 16/129, front pair at y = 8 so the pads end flush with the front face. Tipping edge y = 0.
  - Historical first trough behind the cell: x 3–96, y 53–71, rim 35, 39 cm³ and about 184 g of loose iron at an assumed 4.7 g/cm³ (60 % packing). The later full-width trough supersedes it. The cell moved forward to make room (user: "du kannst die batterie einfach nach vorne rücken und hinten ne größere wanne machen"). `ballast_env()` remains the trough volume minus `base()` itself, so foot boss, posts and rounded corners are cut out of it and the reported mass is what really fits.
  - `bat_cy` is limited by the **tilted** run-outs of the front head screw bosses: built at y 4–14 they reach world y ≈ 18 at z ≈ 30 after the tilt, which is where the cell's shoulder is. 35 clears it, 34 does not (0.14 mm³).
  - Historical four-post layout: each Ø10 corner post lay 3.5 mm off the adjacent walls; at Ø8 it left a sealed sliver void and a second exported body. `ball_rim` = 0.4 kept the walls below the posts to avoid coplanar unions. The current lid instead uses the two insert posts listed above.
  - The 2026-09-22 choice of plastic-forming screws and Ø2.5 core holes was superseded by the user's two-screw, heat-set-insert mounting on 2026-09-23.
  - The lid has no lip over the front wall: the cell has to lift past it (`battery_out`). The current `lid_off` check moves the lid together with its charge module and heatsink 10 mm up after the head and battery have been removed; complete extraction still needs a tilt.
  - The free space in front of the cell (about 50 cm³) is the wrong side of the centre of mass and is deliberately left empty.
- Charge module upright on the ballast lid, directly below the plenum slots (user, 2026-09-23: both sides of the board should get air; subsequently, "Wie LEO: Seite mit Kühlkörper frei"). Components face forwards, heatsink backwards. A single holder and cable tie retain only the cool OUT end; the heatsink end stays free. See Electrics below for dimensions and physical-fit limits. The earlier pair of edge holders, flat tray and bay-floor brackets are no longer built.
  - **The air route starts in the plenum:** the six slots in the head floor connect the fan's filtered outlet side to the component and heatsink passages, which lead to the back-wall slots. The surrounding 5.75 mm channel between filter tube and shell also remains open to the plenum. Geometric corridors are checked; flow rate, natural convection and cooling performance are not measured.
  - The vent is a row of six slots, not one opening: printed intake-face-down the head floor is a vertical wall, and a single 38 mm opening left a 113 mm² flat bridge at its far edge.
  - Ventilation slots in the back wall (user: slots, not honeycomb, and not staggered) sit above the ballast
    lid - an assert keeps them there, below it they would let the offcuts out. Aligned they export clean
    here (12 slots, 2 mm wide, 5 mm pitch); the collinear-corner trap that hit the old slot rows did not
    reappear, so `vent[4]` is 0. If it ever does come back, stagger before reaching for anything else.
- Ballast trough over the full width, lower, with the USB-C socket above it (user, 2026-09-22): nominal x 3–142, y 53–71, rim 26. Its initial 44.5 cm³ / 209 g estimate and 24.5° tip angle at 1.04 kg predate later cut-outs, posts and tipping corrections; use current exports for the usable volume and stability results.
  - The USB-C channel remains at z 45 and now rests on two vertical ribs from the trough floor.
    The right rib is wider and reaches inward to x 108.475, supporting the side stop as well as the
    channel wall. The remaining floor bridge between the ribs spans 7.85 mm. The lid has matching
    slots open to the back, so it can move around the fixed ribs; retain and recheck its 10 mm lift.
    This replaces the unsupported channel ledge. The two former back-wall cable-tie loops remain removed.
  - The USB-C channel stays open towards the board's wire end inside the bay. A side stop takes
    insertion load, retaining `usbc_in` without the old continuous end wall across the wiring route.
    The ribs must not close that opening or the connected cable corridors. Do not restore the removed
    back-wall tie loops. The former shallow `usbc_floor` ledge and rejected 45° gusset describe earlier
    unsupported layouts, not the current load path through the vertical ribs.
  - The wider switch recess uses `ball_step=[118.5,60]` and the existing diagonal through (137,60)
    to (142,65). Measured prototype clearances are 5.50 mm before the terminal envelope, 2.002 mm
    minimum to the body and 2.402 mm from lid to switch. The unchanged Ø10 right insert post limits
    the body gap locally; the rest of the straight recess lies 4 mm behind the body envelope.
    A radius-4.6 mm lid ear at (135,63) preserves a full rim around the Ø6.4 mm head pocket. The two
    M3 x 8 axes and Ruthex inserts stay at (10,63)/(135,63). Keep the trough and lid contours matched;
    enlarging only the lid would reopen the old ballast escape path. Probe evidence is in
    `build/switch-room/evidence.json`; final assembly results belong in the verification report.
  - Early switch positions at y 37 / z 34 were superseded. The current upright switch centre is
    y 50 / z 26, behind the PWM board; its body depth remains an inherited hardware assumption.
  - `lid_off` checks the loaded group (`ball_lid`, `chg_module`, `chg_sink`, `chg_tie`) 10 mm up.
    Complete withdrawal and tilting remain unproven; the matching switch recess and rear-open USB
    rib slots must stay clear throughout the checked lift.
- The switch well flanks rise 1.25 mm per mm instead of 1.0: at exactly 45° `analyze.py overhangs` counted them.
- The rocker switch stands upright in the right wall (long side vertical): the base prints bottom down, so its panel cut-out is a sideways hole and the bridge over it is 12.2 mm instead of 19.2 mm.
- **The LED now sits behind a closed 0.8 mm front skin**, matching LEO-AC1 (user, 2026-09-23).
  `led_cut()` is a Ø3.2 mm blind bore open only to the bay, from y 0.8 to the rear of the Ø7 boss.
  The boss rear face is y 5.8; the LED flange rests there, and the nominal lens starts at y 1.1,
  leaving 0.3 mm before the skin. Insert and glue the LED from inside. This replaces the former
  through-hole and the claim that the front must be open because black PETG cannot transmit light.
  Visibility with the chosen filament still needs a physical check.
  - The 0.8 mm optical skin is an intentional local exception to the usual 1.2 mm wall-thickness
    threshold. Report it separately when `analyze.py thickness` flags it; do not describe the current
    design as unconditionally CLEAN, lower the global threshold, or enlarge the exception beyond
    this light window to hide unrelated thin walls.

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
     strength or clamping pressure. `lid_off` moves the loaded lid 10 mm up with the board attached;
     subsequent withdrawal and tilting are not checked. Leave wire slack for service and remove the
     head and battery first.
   - `check_charger_air()` checks free volumes in front of the components and behind the heatsink, anchored
     to the actual mesh faces. Continuous Ø1.2 mm probe corridors connect each space through an existing
     head-floor slot to the plenum and through a rear vent to the outside. The component-side route passes
     round the board's left end; the heatsink route exits directly behind it. These are geometric access
     checks, **not CFD, an airflow measurement or proof of adequate cooling**. Check closed-housing charging
     temperatures with the actual wiring, both with the fan running and stopped.
   - The two lid screws are at (10, 63) and (135, 63), outside the holder. Earlier posts at x 12/40 and
     the former two-guide lid height of 12.4 mm are historical; use the current exported bounding box
     for the final print size.

   Still available if it is not enough: swapping the ISET resistor (marked 122, 1.2 kΩ) for 2.4 kΩ halves the charge current to 0.5 A and the heat to about 0.85 W, at 12–13 h for a full charge. The user chose the heatsink route alone for now.

## Support-free printability (reviewed 2026-09-23 on the user's request)

The current design has eight print types and eleven physical printed pieces, all intended to print
without supports. The support cross lies flat and its end posts grow upwards; its rear-open head
pockets add no chamber-wide bridge. The following completed checks predate the support-cross addition,
two-insert lid, OUT-end holder, USB support ribs, wider switch recess and closed LED window:

- `analyze.py islands`, `overhangs` (100 mm²), `fins` and `thickness` are all CLEAN on all seven parts.
- `analyze.py overhangs --min-area 5` lists 27 small downward faces, all of them understood: four Ø3.3 foot peg holes and four Ø4 insert pockets in the bay floor (circular bridges, 6–10 mm²), the six vent slots in the head floor (10.8 mm² each), the two finger scoops in the intake face (45 mm² flat cone ends 2 mm above the bed), the USB-C channel floor (85 mm², a 5.8 mm ledge off the back wall) and the two cable tie loops (28 mm² each, 6 mm off the back wall). None is a floating island; every one of them grows out of a wall or bridges a hole under 15 mm.
- Before the support-cross addition, the Bambu CLI sliced all seven parts and all four plates without support. The individual `base` and `head` slices each report "floating cantilever", also present before the G2/G3 changes. The base candidates are the USB-C channel ledge and the tie loops. The warning locations have not been conclusively isolated; keep these warnings visible in the report and inspect the small bridges on the first print.
- Historical decision: gussets under the USB-C floor and former tie loops would eat the lid's lift clearance. The tie loops have since been removed and vertical ribs now support the USB channel through rear-open slots in the lid. Verify the remaining 7.85 mm bridge between ribs on the first print.
- The two tall bridges in the design are the rocker switch panel cut-out (12.2 mm, which is why the switch stands upright) and the magnet pockets in the intake face (Ø10.3, in the bed face).

## Audit of 2026-09-23 (`docs/audit-2026-09-23.md`)

An external audit of commit `a90c581`. What it found and what happened to it:

| ID | Finding | Status |
|---|---|---|
| A1 | The switch notch in the ballast lid opened the trough into the electronics, 9 x 3.5 mm | initially fixed by `ball_switch_fill()`; the current enlarged contoured recess keeps the trough wall and lid outline matched around the switch |
| A2 | The USB-C board could be pushed 15 mm into the bay by a cable | initially fixed with an end wall; now a side stop retains insertion-load support while the wire end stays open; `usbc_in` remains required |
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
- At the G3 revision, the rear ballast-lid screws and posts moved from y 67.5 to 66.2, preserving access for the existing 6.35 mm driver and leaving a 1.3 mm web to adjacent head pockets. That four-post pattern has since been replaced by the two insert posts at (10, 63) and (135, 63); base, lid and screw bodies continue to derive positions from `ball_posts()`.
- The base uses the export tool's existing CGAL fallback; the resulting binary STL is closed, one body and has zero degenerate faces. Do not force an invalid fast-backend result or repair it after export.
- `check_top_corners()` rejects the previous crease in all four outer corner regions and probes a complete 1.21 mm radial material ring around each head magnet pocket. Face-normal comparisons exclude numerical triangles below 0.001 mm altitude; full mesh validity remains independently mandatory. This is a targeted mesh regression, not a global C1 proof.
- `check_joint_profile()` compares actual base/head silhouette spans in five cross sections, 2 mm either side of the joint. Old excess: 2.58–2.61 mm; new: 0.403–0.408 mm, reflecting the remaining transition below the joint. The accepted band is -0.1 to +0.6 mm. This guards the shoulder; it does not certify every surface tangent or erase the intentional seam chamfers.
- Follow-up evidence and images: `docs/rounding-2026-09-23.md`. Fresh full checks: seven mesh types, ten physical parts, 394 coaxial feature pairs, eight paths, 435 assembly pairs; all four analyses CLEAN. Estimated assembled mass 1008.4 g and tip angle 21.4 degrees. Slicer: 470.5 g / 15.4 h across four plates; 470.9 g / 16.1 h as individual part jobs.

Everything the audit lists as "verify on the real part" stays open: magnet force, knob press fit, switch body depth, the charge module's soldered connections and tie against its OUT-end holder, insert pull-out, bridge quality on the small overhangs, and every thermal and airflow figure.

## Open items

- Magnets Ø10 × 3 not measured; holding force through the printed faces not tested. Print the fit test before committing to the full print.
- Part masses for the tipping check are data-sheet or estimated values, not weighed (reported by `print_tools.py` as an OPEN item).
- The knob bore is nominal 5.8 mm with zero clearance, as in LEO-AC1 — validate the push fit on the real knurled shaft with a test print.
- Rocker switch body depth behind the panel is still the assumed value from LEO-AC1.
- LED: verify visibility through the closed 0.8 mm skin with the chosen black PETG and actual LED. Keep this optical thickness exception local; flange fit and light transmission have not been tested on a printed FUMEX base.
- Charge module: verify solder joints, wire exits, the tie band and clamping pressure at the cool OUT-end holder, the free heatsink end and wire slack for the loaded lid's service path. Check temperatures while charging in the closed housing, with the fan on and off; free geometric air corridors do not establish cooling performance.
- Filter support: check all four post contacts against the real fan frame, pocket fit, bar stiffness and creep, and mat bowing or loose fibres at maximum speed. The sparse cross does not establish that rubbing is impossible.
- Filter pressure drop and capture distance are not modelled. The P12 Pro is pressure-optimised (6.9 mmH₂O), which is why it suits a mat, but the working point is unknown.

## Verification and known limits

`docs/verification.json` holds the full report and the current check counts. Checks cover closed meshes and body counts, bed placement and build envelope, assembly pairs with documented assembly-stage or intentional-fit exceptions, coaxial round features, contacts, stops, assembly paths, heat-set insert pockets, the intake lip, mat displacement, and the centre of mass over the foot polygon. The dated results below describe their respective earlier revisions; none establishes an unconditional thickness pass for the current 0.8 mm LED window.

Not checked: flexible deformation (the mat and the TPU feet are rigid bodies here), strength, thermal behaviour, airflow, and anything about the real hardware that has not been measured.

## BOSL2 and upright-charger verification (2026-09-23)

- Final report: `docs/bosl2-charger-2026-09-23.md`; source SHA `544894c9fc4dc5176798e87bd9ad6000a1cbd028eab20a550ffad9b17326cd1d`.
- Seven valid print meshes / ten physical parts, 394 coaxial feature pairs, 435 assembly pairs and eight paths. All four printability analyses are CLEAN. The head thickness sampler retains its pre-existing numerical Trimesh warnings (64,906 valid samples of 65,060); this is not a complete wall-thickness proof.
- `check_rim_chamfers()` measures 24 exported profiles; maximum error 0.00020 mm. Both charger stops engage at 0.25 mm. `check_charger_air()` confirms two unobstructed connected passages at the real board/heatsink faces. These regressions reject the old chamfer and flat-board layouts respectively.
- Slicer: all seven parts and four plates pass with supports disabled; 469.7 g / 15.3 h as arranged plates, 470.0 g / 16.1 h as individual jobs. Existing base/head floating-cantilever warnings remain. The upright charger lid adds no warning. Estimated assembled mass 1007.6 g, tip angle 21.4 degrees.
- STLs, 3MF, README images and viewer are regenerated. No physical print or thermal/airflow test has been performed.

## Filter support and hardware follow-up (2026-09-23)

- Earlier hardware follow-up: `docs/hardware-2026-09-23.md`, before the wider switch recess, USB support ribs and closed LED window. That revision had eight print types / eleven physical pieces, 340 coaxial feature pairs, 496 assembly pairs and nine sampled linear paths; all four printability analyses were CLEAN.
- At that revision `ball_step[0]` was 122.5 rather than 126: 126 left the lid and trough tangent to the switch terminal envelope at y53. The intermediate lid and isolated trough-step probes measured 1.5 mm. The current 118.5/60 step and radius-4.6 mm lid ear supersede that contour, providing the clearances recorded above.
- The rear lid corner reliefs are 0.5 mm. The old 5 mm cuts depended on the removed corner posts to close the trough. `check_ballast_cover()` compares actual near-rim contents and lid sections, allowing only the intentional seam; the maximum measured normal gap is 0.2 mm. New insert bores are excluded from `ballast_env()`.
- `check_charger_holder()` probes each of the three seats, the hot-side exclusion and connected tie passages. `check_usb_wire_access()` includes the inner terminal face itself; probes above and below the board alone also passed with the old blocking end wall and were insufficient.
- At that earlier hardware revision ballast capacity was 44.0 cm3 / about 207 g of loose iron at the assumed packing density. Estimated assembled mass is 1020.5 g, tip angle 21.8 degrees, front margin 28.9 mm. Printed lid envelope is 138.6 x 17.8 x 13.7 mm.
- Only the loaded lid's 10 mm vertical lift is established. Sampled X/Y/Z tilts and coupled forward moves did not establish a complete extraction sequence; that remains unproven, not certified impossible. The head and battery are removed before the checked lift.
- General corner-post/cover dependency documented in the shared skill's PITFALLS.md, commit `41a0b0d`. Project scripts remain identical to the skill.

- Slicer at that earlier hardware revision: all eight types and four plates passed without supports; 468.9 g / 15.3 h on arranged plates, 469.3 g / 16.3 h as individual jobs. Existing base/head floating-cantilever warnings remain; lid and support cross have none. Head thickness sampling returns 64,941 valid points of 65,128 with the known numerical Trimesh warnings.


## Lid, switch, USB and front-detail verification (2026-09-23)

- Current follow-up: `docs/detail-refinements-2026-09-23.md`. Source SHA `6bf5fd11fdefd249b418a3faa7921d67a7f2b9f68ec29cc29cbbd020050e2df5`.
- Exactly two M3 x 8 lid screws remain at (10,63) and (135,63), centred between the trough's inner front and back faces at y55/71. Both engage Ruthex RX-M3x5.7 inserts through Ø4 x 7 mm pockets. Actual seat material and enclosure fill are 100%; full 5.7 mm insert engagement leaves 0.8 mm to the pocket bottom. The right lid ear keeps its screw pocket enclosed beside the wider switch recess.
- USB support ribs run from the floor to the channel, verified by full solid probes. Both rear-open lid slots clear their ribs, the PCB contacts its seat at z42.85 and the three wire corridors remain open. The loaded lid's checked service motion is still only 10 mm vertically; full extraction remains unproven.
- Eight closed print types / eleven pieces; 337 coaxial feature pairs, 496 assembly pairs, nine general sampled paths and the additional 15 mm LED inside-access path pass. Islands, overhangs (100 mm² threshold) and fins are CLEAN. Thickness reports exactly one intended 0.8 mm region at the closed LED window (estimated sampled area 20 mm²); the 1.2 mm threshold is unchanged elsewhere. The head's existing Trimesh numerical warnings leave 65,088 of 65,277 usable samples.
- All eight individual slices and four arranged plates pass with supports disabled. The base's floating-cantilever warning is gone; the existing head warning remains on its individual and arranged slice. Arranged plates: 472.9 g / 15.4 h; individual jobs: 473.4 g / 16.4 h.
- Current ballast volume is 40.97 cm³, about 193 g at the assumed packing density. Estimated assembled mass 1009.8 g, front tipping margin 28.6 mm and tip angle 21.3 degrees. These supersede the previous revision's values above.
- All eight documentation views, the STLs, 3MF and both viewer copies are rebuilt. `07_ballast_mount` makes the two fasteners visible; `08_usb_mount` shows the floor-connected channel ribs.
