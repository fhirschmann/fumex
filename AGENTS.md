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
- **No fan seat plate.** A flat plate with a round bore would have been a 4453 mm² flat overhang over the filter chamber (found by `analyze.py overhangs`). Instead four corner gussets grow at 45° from the intake face back to the fan (`fan_lugs()`): nothing overhangs, the remaining opening (11 700 mm²) is wider than the fan's swept annulus (8 800 mm²), the fan bears on their back faces and its four inserts sit in them. The fleece mat is pressed into the gussets; `checks()` bounds that at 5 % of the mat volume (currently 2.3 %).
- Filter cassette held by four magnet pairs in open pockets (skill rule: glue one side in, place the counterparts on them, then glue — polarity is then automatic). Two 45° finger scoops in the side edges of the intake face get a finger behind the flange; two half-round notches in the intake lip get a finger behind the mat.
- The mat is held by the intake lip (opening 117 in a 121.5 chamber, 2.25 mm per side). It is pressed in and pulled out past that lip — a rigid-body path check cannot show this, so `filter_out` is not a checked path but a documented limitation.
- Head screws (4 × M3 × 8) sit along the side walls at x 9/136, y 9/60: their bosses merge into those walls and their undersides drop 45° towards them, so nothing starts in the air. x keeps them clear of the back cover bosses inside the head, y of its back cover lip. There is no register between head and base — the screws locate it, which is what `stops` checks.
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
- Charge module on the inside of the back cover, in the plenum, heatsink towards the fan (user, 2026-09-22: nothing may stick out of the housing, put the board in the airflow). `plenum` grew to 14.3 and with it `body_d` to 74. Two ledges carry the board's long edges, but only from 13 mm off the OUT end: closer in, the inductor and the SS34 sit 0.7–1.0 mm from the edges (LEO-AC1 board survey), so `chg_module_env()` carves those two edge strips out of the parts block exactly where the ledges bear. One cable tie through loops above and below holds it; `exhaust_grid_2d()` leaves a solid patch in the grid for all of it. Six wires now cross the head/base joint through the widened floor notch.
- The bay has no vents any more: with the charger's heat gone there is no source worth venting, and the trough's back wall is the housing's back wall — slots there would just let ballast out.
- The switch well flanks rise 1.25 mm per mm instead of 1.0: at exactly 45° `analyze.py overhangs` counted them.
- The rocker switch stands upright in the right wall (long side vertical): the base prints bottom down, so its panel cut-out is a sideways hole and the bridge over it is 12.2 mm instead of 19.2 mm.

## Electrics — two things that belong in the README and in the build

1. **0.32 A against 0.33 A.** The LFUPSMA charge/boost module is specified for 0–0.32 A at 12 V, the P12 Pro draws 0.33 A at full speed. The top of the knob range is therefore at the module's limit: it gets warm and starting at 100 % may brown out. Start slow, then turn up.
2. **Charger heat — solved by taking it outside.** The CN3058E is a linear charger; at 1 A from 5 V it turns about 1.6 W into heat, and in LEO-AC1 it stood in the fan's intake. The first layout here put it upright in the middle of a closed bay, 4.4 mm from the cell, which the user rejected on 2026-09-22 ("wird recht warm und kriegt schlecht Luft") — and rightly so: charging a LiFePO4 cell above 45 °C costs life, and the heat appears exactly while charging.

   Now the board lies flat against the inside of the back wall and its 14 × 14 × 6 heatsink reaches through a cut-out into ambient air, 4 mm proud of the back face. The heat leaves the housing instead of entering the bay, and the cell sits 16 mm away behind the cradle instead of beside the IC. The insulating silicone pad under the heatsink keeps the fins dead, so a bare metal block on the outside is safe to touch. Rough figures: heatsink in free air about 20 K/W plus about 5 K/W through the pad, so roughly 40 K over ambient at 1 A instead of a hot box.

   Still available if it is not enough: swapping the ISET resistor (marked 122, 1.2 kΩ) for 2.4 kΩ halves the charge current to 0.5 A and the heat to about 0.85 W, at 12–13 h for a full charge. The user chose the heatsink route alone for now.

## Open items

- Magnets Ø10 × 3 not measured; holding force through the printed faces not tested. Print the fit test before committing to the full print.
- Part masses for the tipping check are data-sheet or estimated values, not weighed (reported by `print_tools.py` as an OPEN item).
- The knob bore is nominal 5.8 mm with zero clearance, as in LEO-AC1 — validate the push fit on the real knurled shaft with a test print.
- Rocker switch body depth behind the panel is still the assumed value from LEO-AC1.
- Filter pressure drop and capture distance are not modelled. The P12 Pro is pressure-optimised (6.9 mmH₂O), which is why it suits a mat, but the working point is unknown.

## Verification and known limits

`docs/verification.json` holds the full report. Checked: closed meshes and body counts, bed placement and build envelope, all 231 assembly pairs free of overlap (three documented exceptions), coaxial round features, contacts, stops, six assembly paths, heat-set insert pockets, the intake lip, mat displacement, and the centre of mass over the foot polygon.

Not checked: flexible deformation (the mat and the TPU feet are rigid bodies here), strength, thermal behaviour, airflow, and anything about the real hardware that has not been measured.
