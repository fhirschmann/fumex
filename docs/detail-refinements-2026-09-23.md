# Detail refinements — 2026-09-23

The ballast lid uses exactly **two M3 × 8 screws**, one centred at each end, with **Ruthex RX-M3x5.7 inserts**. Both screw seats and insert access are verified in the freshly exported assembly.

The closed LED window, fan-guide lead-ins, continuous intake lip, floor-supported USB-C channel and wider switch recess pass the final geometry checks. The intentional 0.8 mm LED skin is the only reported wall-thickness exception. Slicing succeeds without supports; the base now has no warning, while the head retains its existing floating-cantilever warning.

Source SHA-256: `6bf5fd11fdefd249b418a3faa7921d67a7f2b9f68ec29cc29cbbd020050e2df5`.

## Geometry changes and direct checks

| Feature | Construction and evidence |
|---|---|
| Two lid fasteners | Axes (10,63) and (135,63), with y63 centred between the original trough interior faces y55/71. Two Ø10 mm posts contain Ø4 × 7 mm pockets. Both screw-seat and enclosure probes are 100% filled; straight Ø6.35 mm insert-tool access is clear. M3 × 8 provides 6.2 mm penetration for the 5.7 mm insert, with 0.8 mm clearance to the pocket bottom. |
| Closed LED front | A Ø3.2 mm blind bore starts at y=0.8 behind the unchanged outer front face. The Ø7 mm boss ends at y=5.8. Five mesh rays measure exactly 0.8 mm of skin; the full-disc material probe finds 0 mm³ missing. The inward pocket probe finds 0 mm³ obstruction. |
| LED installation | The nominal Ø3 mm body starts 0.3 mm behind the skin. Its Ø3.8 mm flange rests on the boss's rear face: the bearing-ring probe is 100% filled and a 0.05 mm forward displacement makes 0.16474 mm³ of contact there. A 15 mm inward removal path in 0.5 mm steps has no collision against all other installed physical bodies; reversing it gives the geometric insertion path. Temporary screwdriver envelopes are excluded. |
| Fan guide chamfers | Each of the four L-guides has a 1.2 mm, 45° chamfer on both inward-facing rear edges. The straight locating clearance remains 0.4 mm per side; entry clearance increases to 1.6 mm. Independent rays through all eight flanks at rear depths 0.1/0.6/1.1/1.3 mm measure clearance 1.5/1.0/0.5/0.4 mm. Maximum error over 32 samples: 0.000006 mm. The 2.4 mm guide retains 1.2 mm at the chamfered end. |
| Intake lip | Both half-round mat cut-outs are removed. All 114 sampled points in the former cut-outs, spanning both side lips, three face depths and ±9 mm vertically, are now solid. The separate cassette finger scoops at the outer housing sides remain. The straight-side retaining overlap is 2.25 mm. |
| USB-C support | Both channel walls now grow from the trough floor. The wider right foot carries the one-sided insertion stop; the rear board seat bridges 7.85 mm between supports. Four vertical material probes are 100% filled. Both rear-open lid slots have zero overlap with the enlarged support-clearance probes. The board sits at z=42.85 mm and produces 2.5875 mm³ contact after a 0.05 mm downward move. |
| Switch recess and lid | The wider matched trough/lid contour uses `ball_step=[118.5,60]`; a radius-4.6 mm ear keeps the right screw pocket enclosed. The two existing M3×8/Ruthex axes remain at (10,63) and (135,63). The terminal envelope has 5.5 mm of space in front of it, with 2.402 mm between switch and lid and 2.002 mm at the closest trough-to-switch point. Top-cover slices leave 0 mm² uncovered beyond the permitted 0.3 mm seam; the sampled effective maximum seam is 0.235 mm. |

The LED geometry follows the LEO-AC1 blind-pocket arrangement. The nominal LED body and flange are inherited dimensions, not measurements of the actual FUMEX LED. The black PETG skin still needs a physical light-transmission test. The 15 mm path checks the rigid nominal LED envelope; it does not model leads, adhesive or hand/tool access.

![Two ballast-lid screws and the matching supports](../img/07_ballast_mount.png)

![USB-C channel on continuous support ribs](../img/08_usb_mount.png)

## Final verification

- Eight closed print meshes, eleven physical printed pieces, 337 coaxial feature pairs and 496 assembly pairs pass. Nine standard sampled assembly paths pass, plus the separate 15 mm LED path.
- Islands, overhangs (100 mm² threshold) and fins are CLEAN. The standard thickness threshold remains **1.2 mm**. The base's closed LED skin is the sole thickness finding: minimum/median 0.8 mm over the analyzer's 20 mm² sampled region. This is an explicit local optical exception, not an unconditional thickness pass.
- Head thickness sampling yields 65,088 valid points out of 65,277 with the known numerical Trimesh warnings. Sampling does not prove every possible wall thickness.
- All eight individual types and all four arranged plates slice with supports disabled. The base has **no warning**; only the existing head floating-cantilever warning remains.
- Arranged plates: **472.9 g / 15.4 h**. Individual jobs: **473.4 g / 16.4 h**.
- Net ballast capacity: **40.968 cm³**, approximately **192.55 g** at the assumed packing density. Estimated assembled mass: **1009.8 g**. Front stability margin: **28.6 mm**; tip angle: **21.3°**.

Only the loaded ballast lid's 10 mm vertical lift is established. Complete extraction and a tilt sequence remain unproven. Strength, light transmission, thermal performance, airflow, wire routing with real solder joints and flexible-mat behaviour still require physical checks.

## Evidence

The main results are in [verification.json](verification.json) and [slicer-summary.json](slicer-summary.json). The [evidence snapshot](detail-refinements-2026-09-23/evidence.json) records all four analyses, command exit codes, the intentional thickness exception and artifact hashes. Independent [fan-profile and restored-lip samples](detail-refinements-2026-09-23/geometry-review.json) use the actual exported mesh. The same evidence directory contains the final export, analysis, slicing, rendering and viewer logs.

The source, all eight STL hashes, the slicer's source meshes and the project 3MF match. Both viewer files are identical, rebuilt from the final assembly exports. All eight documentation images were regenerated; the two detail images above were visually inspected. The existing browser tab needs a manual reload: its local-file URL was blocked by the browser security policy for automated access.
