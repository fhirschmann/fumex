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
- The head floor runs the full depth and the back cover ends `cover_gap` above it. Without that the cover's lower edge was flush with the joint plane and scraped along the base rim on its way off (`cover_off` path).
- Feet: four TPU pads, one M3 × 8 each plus a Ø3 peg against turning. A keying pocket in the bottom face was 275 mm² of flat overhang per foot, so it went.
- Tipping: the head leans forward, so `checks()` computes the centre of mass from mesh volumes and part masses and requires ≥ 15 mm to every foot edge. Currently 20.4 mm at the front, 13.8° of tip angle. The front feet sit at y = 10 for that reason.
- The convection slots beside the charge module climb 1.5 mm per slot. Aligned, their corners were collinear in the back face and every backend (Manifold and two CGAL attempts) left a degenerate triangle there.
- The switch well flanks rise 1.25 mm per mm instead of 1.0: at exactly 45° `analyze.py overhangs` counted them.
- The rocker switch stands upright in the right wall (long side vertical): the base prints bottom down, so its panel cut-out is a sideways hole and the bridge over it is 12.2 mm instead of 19.2 mm.

## Electrics — two things that belong in the README and in the build

1. **0.32 A against 0.33 A.** The LFUPSMA charge/boost module is specified for 0–0.32 A at 12 V, the P12 Pro draws 0.33 A at full speed. The top of the knob range is therefore at the module's limit: it gets warm and starting at 100 % may brown out. Start slow, then turn up.
2. **Charger heat.** The CN3058E is a linear charger; at 1 A from 5 V it turns about 1.7 W into heat, and here it sits in a closed bay instead of a fan's intake as in LEO-AC1. The user's 14 × 14 × 6 heatsink sits on the metal pad behind the IC, the holder plate keeps it off the housing, and two rows of slots in the back wall let the bay breathe. Swapping the ISET resistor (marked 122, 1.2 kΩ) for 2.4 kΩ halves the charge current to 0.5 A and the heat to about 0.85 W; a full charge then takes 12–13 h.

## Open items

- Magnets Ø10 × 3 not measured; holding force through the printed faces not tested. Print the fit test before committing to the full print.
- Part masses for the tipping check are data-sheet or estimated values, not weighed (reported by `print_tools.py` as an OPEN item).
- The knob bore is nominal 5.8 mm with zero clearance, as in LEO-AC1 — validate the push fit on the real knurled shaft with a test print.
- Rocker switch body depth behind the panel is still the assumed value from LEO-AC1.
- Filter pressure drop and capture distance are not modelled. The P12 Pro is pressure-optimised (6.9 mmH₂O), which is why it suits a mat, but the working point is unknown.

## Verification and known limits

`docs/verification.json` holds the full report. Checked: closed meshes and body counts, bed placement and build envelope, all 231 assembly pairs free of overlap (three documented exceptions), coaxial round features, contacts, stops, six assembly paths, heat-set insert pockets, the intake lip, mat displacement, and the centre of mass over the foot polygon.

Not checked: flexible deformation (the mat and the TPU feet are rigid bodies here), strength, thermal behaviour, airflow, and anything about the real hardware that has not been measured.
