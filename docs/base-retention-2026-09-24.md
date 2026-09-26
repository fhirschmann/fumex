# Base retention and USB access — 2026-09-24

This revision supersedes the lid-mounted battery tongue and right-side USB keeper described in `print-fit-2026-09-24.md`.

## Geometry

- The battery's axial end wall is integrated into the base, with 0.5 mm nominal end clearance. Its rounded, bevelled top stays below the protection-board and cable envelope.
- Two retainers on the removable head engage the front shoulders of the cylindrical cell at x12 and x68. The rear cradle walls oppose the resulting rearward movement. A 25 mm central opening clears the 20 mm protection board under the shrink wrap, following the split-holder principle used in LEO-AC1. The head must be fitted for upward restraint.
- A single central L-stop on the ballast lid retains the USB board at its PCB edge. Both lateral wire exits remain open. The USB channel's 45-degree gussets begin above the lid, which no longer needs USB support slots.
- Both blind LED pockets and flange seats move 1 mm inward. The front skins are now 1.8 mm; lens-to-pocket clearance stays 0.3 mm. The earlier local thin-wall exception is retired.

## Battery checks

The cell cylinder and protection-board envelope are tested separately. Contact with the board cannot count as battery retention.

- Nominal cell-to-holder clearance: 0.497 mm.
- Nominal protection-board clearance to the complete head: 2.448 mm; sideways clearance to the shoulder holders: 2.5 mm.
- Both shoulders catch the nominal cell after 0.8 mm upward movement. With 0.4 mm rearward offset, contact occurs at 1.325 mm.
- A diagonal escape attempt follows the rear cradle wall as the rising cell gains lateral space: both shoulders catch at 1.525 mm lift and 0.552 mm rearward movement. The protection board still has 1.118 mm clearance.
- The base end stop catches nine shifted/lifted axial probes. The upper cable corridor remains open. Head removal releases the upper retainers for upward battery extraction.

These are rigid geometric checks, not strength, creep, impact or shrink-wrap tests. Verify the actual cell, wires and cushioning on the printed parts. LED visibility through the chosen PETG also needs a physical check.

## USB support and lid service

The two 2 mm wide guides begin at y58.72; their 45° undersides meet the rear wall at z33, 4 mm above the lid. The PCB remains supported on its rear seat. Six 2 mm wide corridor probes check both lateral wire routes, including their upward exits with the central L fitted.

The lid still uses two M3 × 8 screws and Ruthex RX-M3x5.7 inserts. The axes are now (10,63) and (117,56.8). The right post has a front flat with 1.85 mm remaining around the insert bore, preserving the PWM board’s service path. Moving the right screw inwards and forwards preserves straight tool access past the head's mounting bosses and keeps its ear clear of the switch well. The trough and lid share the new switch contour and close within the existing 0.3 mm seam allowance. Usable ballast volume is approximately 40.3 cm³, or 189 g at the established loose-iron density estimate.

Remove the head, battery, rocker switch and lid screws first. The loaded lid follows six straight stages: up 3.4 mm, forwards 4 mm, up another 3 mm, forwards another 16 mm, right 0.2 mm, then up 60 mm. The 392 sampled poses are collision-free with at least 0.20 mm clearance after the initial lift. The switch has a separate 35 mm outward path that also works with the lid and battery installed. Clip flexure, finger access and connected wires remain physical checks.

The updated USB fit coupon retains the cropped right screw post plus two small fixture pads. All three support the lid at its installed z26 height. The cropped screw region is not an insert-fit specimen; the test remains for USB insertion, board seating and the central keeper.

## Final verification

Source SHA256: `edbaddc6a11a0139257ecf6defe52e571f14585859154e7e769e51c90340af35`.

- Ten closed, consistently oriented meshes, each one body and without degenerate faces; eight production types, eleven production pieces and two optional test pieces.
- All 528 assembly pairs, 449 coaxial feature pairs, ten standard paths, the complete PWM service path and the 392-pose loaded-lid path pass. The USB board and fit coupon also pass their continuous swept installation paths.
- Islands, overhangs, thickness and fins: **CLEAN on all ten meshes**. Saved results: [islands](base-retention-2026-09-24/islands.json), [overhangs](base-retention-2026-09-24/overhangs.json), [thickness](base-retention-2026-09-24/thickness.json), [fins](base-retention-2026-09-24/fins.json).
- The head's known numerical Trimesh ray warnings leave 65,500 of 65,672 thickness samples usable; no region is flagged. These sampled checks do not establish every local wall thickness or printed strength.
- Estimated assembled mass 1012.6 g; front tipping margin 28.5 mm and tip angle 21.2°. Bought-part mass estimates and loose-iron packing density remain unmeasured.
- All ten individual slices, four production plates and the optional USB fit plate pass with supports disabled and no slicer warnings. Production totals are 476.8 g / 15.8 h as arranged plates, or 477.2 g / 16.8 h as individual jobs. The USB fit plate uses 10.3 g and takes about 65 minutes. Settings and individual results: [slicer summary](slicer-summary.json).
- Both viewer copies (`build/viewer.html` and `docs/index.html`) are rebuilt from the current assembly exports and are byte-identical. The affected documentation views are regenerated and visually checked. The open local browser tab could not be refreshed because browser policy blocked local-file access; it needs a manual reload.

The changed production pieces are `base`, `head` and `ball_lid`. Their replacements work together; the other production pieces retain their geometry. Both optional USB fit pieces are updated as well.
