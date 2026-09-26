# AGENTS.md — working on FUMEX

Internal notes for coding agents (Claude, Codex). The README is public and stays free of process notes, audits, assumptions and tool internals; put those here.

## Working rules

- Talk to the user in German. README, AGENTS.md, code comments, viewer labels, slicer plate/material names, check messages **and all commit messages** are English (user, 2026-09-21).
- The project follows the skill `openscad-print-project` (`~/.claude/skills/openscad-print-project`). After every model change run the full loop: `print_tools.py export` → `analyze.py islands/overhangs/thickness/fins` → `slice_check.py` → update README numbers → `build_viewer.py --copy-to docs/index.html` → commit.
- `scripts/` must stay identical to the skill (`python3 ~/.claude/skills/openscad-print-project/scripts/skill_sync.py status -C .`). Improve tools in the skill and adopt/install them; no project-local forks.
- No painted or scripted supports. Every part prints without them; `analyze.py overhangs` is CLEAN and must stay that way.
- No vendor CAD in the repo or the viewer. The fan is the simple `fan_visual()` placeholder.
- Electrically this is LEO-AC1 minus the bail, the QR code and the logo. When a measured value of a shared part is needed, take it from `~/Projects/leo-ac1/AGENTS.md` rather than re-measuring.

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
  magnet pockets are 3.2 deep and `analyze.py thickness` wants 1.2. What is left is the rim bevel, `cass_c` = 2.0;
  at `cass_inset + cass_c` it stops 0.15 mm short of the pockets, so 2.0 is the limit. Visible step 2.5 mm.
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
  - The lid has no lip over the front wall: the cell has to lift past it (`battery_out`). It slides forward 25 mm before it can come up, because the rear head screw bosses hang over the trough (`lid_off`).
  - The free space in front of the cell (about 50 cm³) is the wrong side of the centre of mass and is deliberately left empty.
- Charge module back in the bay with a vent over it (user, 2026-09-22, after outside the housing and after the plenum): the best of the three. Short wires, nothing in the fan's way out, and brackets on the bay floor are plain vertical walls in print instead of cantilevers off a wall.
  - Two grooved end brackets take the short edges of the board; the long edges are no good, the board carries parts up to them. Brackets 3.6 mm thick (at 3 the 2 mm groove left 1 mm of wall) and only as deep as parts plus PCB, because the heatsink is wider than the board and hangs free behind them. The board sits 2 mm off the floor so the heatsink, which is 1.5 mm taller than the board at each edge, clears it.
  - **The vent works because the head already has a channel:** between the filter tube (127.5) and the shell (139) a 5.75 mm gap runs all round, closed at the front by the intake face and open at the back into the plenum, under the fan. Slots in the head floor meet it, so the fan pushes filtered air down into the bay and out of the back wall slots; with the fan off the same path is a chimney. Nothing bypasses the mat.
  - The vent is a row of six slots, not one opening: printed intake-face-down the head floor is a vertical wall, and a single 38 mm opening left a 113 mm² flat bridge at its far edge.
  - Ventilation slots in the back wall (user: slots, not honeycomb, and not staggered) sit above the ballast
    lid - an assert keeps them there, below it they would let the offcuts out. Aligned they export clean
    here (12 slots, 2 mm wide, 5 mm pitch); the collinear-corner trap that hit the old slot rows did not
    reappear, so `vent[4]` is 0. If it ever does come back, stagger before reaching for anything else.
- Ballast trough over the full width, lower, with the USB-C socket above it (user, 2026-09-22): x 3–142, y 53–71, rim 26, 44.5 cm³ or about 209 g. 24.5° of tip angle at 1.04 kg.
  - Everything above the lid has to leave it 10 mm of lift: the USB-C channel went to z 45 and the cable tie loops to z 45. The channel's floor is only `usbc_floor` = 6 mm deep, because a full-length floor at that height is a 198 mm² flat overhang and a 45° gusset would stand in the trough.
  - The switch moved to y 37 / z 34: its well box reached into the trough's front wall, and higher up its bezel poked through the joint plane. Its pins in turn forced the PWM board 4 mm left (`pot_x` 108).
  - `lid_off` only proves 10 mm up and 8 mm forward. Getting the lid out of the bay after that is a tilt, which a rigid axis-aligned path cannot express; the lid's front right corner is notched so it clears the switch well.
- The switch well flanks rise 1.25 mm per mm instead of 1.0: at exactly 45° `analyze.py overhangs` counted them.
- The rocker switch stands upright in the right wall (long side vertical): the base prints bottom down, so its panel cut-out is a sideways hole and the bridge over it is 12.2 mm instead of 19.2 mm.

## Electrics — two things that belong in the README and in the build

1. **0.32 A against 0.33 A.** The LFUPSMA charge/boost module is specified for 0–0.32 A at 12 V, the P12 Pro draws 0.33 A at full speed. The top of the knob range is therefore at the module's limit: it gets warm and starting at 100 % may brown out. Start slow, then turn up.
2. **Charger heat — solved by taking it outside.** The CN3058E is a linear charger; at 1 A from 5 V it turns about 1.6 W into heat, and in LEO-AC1 it stood in the fan's intake. The first layout here put it upright in the middle of a closed bay, 4.4 mm from the cell, which the user rejected on 2026-09-22 ("wird recht warm und kriegt schlecht Luft") — and rightly so: charging a LiFePO4 cell above 45 °C costs life, and the heat appears exactly while charging.

   Now the board lies flat against the inside of the back wall and its 14 × 14 × 6 heatsink reaches through a cut-out into ambient air, 4 mm proud of the back face. The heat leaves the housing instead of entering the bay, and the cell sits 16 mm away behind the cradle instead of beside the IC. The insulating silicone pad under the heatsink keeps the fins dead, so a bare metal block on the outside is safe to touch. Rough figures: heatsink in free air about 20 K/W plus about 5 K/W through the pad, so roughly 40 K over ambient at 1 A instead of a hot box.

   Still available if it is not enough: swapping the ISET resistor (marked 122, 1.2 kΩ) for 2.4 kΩ halves the charge current to 0.5 A and the heat to about 0.85 W, at 12–13 h for a full charge. The user chose the heatsink route alone for now.

## Support-free printability (reviewed 2026-09-23 on the user's request)

All seven parts print without supports. Evidence and the remaining soft spots:

- `analyze.py islands`, `overhangs` (100 mm²), `fins` and `thickness` are all CLEAN on all seven parts.
- `analyze.py overhangs --min-area 5` lists 27 small downward faces, all of them understood: four Ø3.3 foot peg holes and four Ø4 insert pockets in the bay floor (circular bridges, 6–10 mm²), the six vent slots in the head floor (10.8 mm² each), the two finger scoops in the intake face (45 mm² flat cone ends 2 mm above the bed), the USB-C channel floor (85 mm², a 5.8 mm ledge off the back wall) and the two cable tie loops (28 mm² each, 6 mm off the back wall). None is a floating island; every one of them grows out of a wall or bridges a hole under 15 mm.
- The Bambu CLI slices all seven parts and all four plates without support and reports exactly one NON_CRITICAL warning, on `base`: "floating cantilever". The candidates are the USB-C channel ledge and the two tie loops — the same three features above. An A/B slice of the base with and without the loops was inconclusive because the standalone CLI run re-orients the part, so this is not pinned down further.
- Deliberately **not** fixed: a 45° gusset under the USB-C channel floor or under the tie loops would reach 6 mm down and eat exactly the clearance the ballast lid needs to lift out (`lid_off`). A 6 mm ledge in PETG is routine; the lid coming out is not negotiable.
- The two tall bridges in the design are the rocker switch panel cut-out (12.2 mm, which is why the switch stands upright) and the magnet pockets in the intake face (Ø10.3, in the bed face).

## Open items

- Magnets Ø10 × 3 not measured; holding force through the printed faces not tested. Print the fit test before committing to the full print.
- Part masses for the tipping check are data-sheet or estimated values, not weighed (reported by `print_tools.py` as an OPEN item).
- The knob bore is nominal 5.8 mm with zero clearance, as in LEO-AC1 — validate the push fit on the real knurled shaft with a test print.
- Rocker switch body depth behind the panel is still the assumed value from LEO-AC1.
- Filter pressure drop and capture distance are not modelled. The P12 Pro is pressure-optimised (6.9 mmH₂O), which is why it suits a mat, but the working point is unknown.

## Verification and known limits

`docs/verification.json` holds the full report. Checked: closed meshes and body counts, bed placement and build envelope, all 231 assembly pairs free of overlap (three documented exceptions), coaxial round features, contacts, stops, six assembly paths, heat-set insert pockets, the intake lip, mat displacement, and the centre of mass over the foot polygon.

Not checked: flexible deformation (the mat and the TPU feet are rigid bodies here), strength, thermal behaviour, airflow, and anything about the real hardware that has not been measured.
