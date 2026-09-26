# Reinforced PD-trigger keeper foot — 2026-09-25

Two triangular cheeks now brace the lid-mounted USB-PD keeper at its foot. Each extends 2 mm beyond the 4 mm stem, overlaps it by 0.2 mm, rises 8 mm above the lid, and runs 8 mm rearwards. The widened and lengthened foot distributes plug loads into the lid. The sloped tops print without support.

The cheeks occupy x102..104.2 and x107.8..110, with feet from y53.2 to y61.2 and upper tips at z37. The keeper's PCB-edge stop, upper return and the two side cable exits remain unchanged. The ribs end below the wire corridors; they are integral to the lid, with no separate fasteners or glue.

Changed print geometry: `ball_lid` and the matching `usbc_fit_lid` coupon. Base and other production parts keep their existing geometry.

## Verification

Source SHA-256: `7e90185f184b1b34f1a70f9b1028df8e681000716e65b3594a7d6f6cf688a46d`.

The [assembly report](verification.json) passes with eleven closed single-body print meshes, zero degenerate faces, 445 coaxial feature pairs, 595 assembly pairs and ten standard service paths. Both ribs have complete material at their feet, through the webs, into the stem and in the lid beneath them. The new probes reject the preceding unbraced lid.

All six cable corridors stay clear. The lower PCB stop, upper return and 2.9° lift-capture check remain valid. The complete loaded-lid service path passes with at least 0.20 mm clearance after the initial lift. The keeper clearance probe includes both entire ribs. The updated USB fit coupon also passes its seat, stop and insertion checks.

All eleven meshes are CLEAN in [islands](pd-keeper-braces-2026-09-25/islands.json), [overhangs](pd-keeper-braces-2026-09-25/overhangs.json), [thickness](pd-keeper-braces-2026-09-25/thickness.json) and [fins](pd-keeper-braces-2026-09-25/fins.json). All eleven individual slices, four production plates and the USB fit plate pass without warnings or supports. The [slicer report](slicer-summary.json) gives 8.43 g for the lid, 477.4 g / 15.9 h for arranged production and 478.0 g / 17.2 h for individual jobs. The USB fit plate is 10.0 g / about 62 minutes.

The static assembled estimate is 1014.0 g, with a 28.3 mm front margin and 21.0° tip angle. These checks establish geometry and printability; physical keeper strength, PETG creep and cable-lever forces have not been measured.

STLs, both 3MF projects, all twelve documentation views and both viewer copies are rebuilt. Shared scripts match the print-project skill. The local file viewer requires manual reload because automatic refresh is blocked.
