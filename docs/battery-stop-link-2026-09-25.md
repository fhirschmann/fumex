# Battery end-stop connection — 2026-09-25

The battery's axial stop is joined directly to the ballast trough front wall. A 3 mm thick web closes the former 2 mm gap and grows continuously from the base floor. Its top slopes down towards the trough so the removable ballast lid stays clear.

The web spans x76.1..79.1 and y49.6..54. Its top descends at 45 degrees from z29 to z25.6 at y53, then extends 1 mm into the trough wall. The original rounded and beveled battery contact wall remains; the connection is added at its rear end. Nominal axial pack clearance stays 0.5 mm. The top is below the BMS and cable exit.

Only the base production geometry changes. A mesh comparison against commit `1b54fd944d2346e6f1fc193c08e591844d3a9e4e` finds 154.869 mm³ added and no material removed, with unchanged outside dimensions. The other seven production STLs are byte-identical and both USB fit pieces are geometrically unchanged. The connection prints with the base without supports; the lid remains a separate removable part. This provides a second attachment for the stop but does not establish an ultimate strength or creep rating.

## Verification

Source SHA-256: `152bdde96866f33b4eff4f85b12d2b582b43e39602d3c16a702fa8b487168946`.

The [assembly report](verification.json) passes with ten closed single-body print meshes, zero degenerate faces, 443 coaxial feature pairs, 561 assembly pairs and ten standard service paths. Independent material probes cover the full height of the former gap and both stop/trough junctions: all report 100% material. The same gap probe rejects the preceding base from commit `1b54fd944d2346e6f1fc193c08e591844d3a9e4e`, where only the floor fills about 0.67% of it.

Battery clearance remains 0.5 mm in the installed pose, and all nine shifted/lifted axial-retention checks pass. The upper BMS/cable corridor has no overlap. The actual connection has 0.283 mm minimum distance to the lid's front edge across its diagonal top (0.4 mm vertically over the trough wall). Battery, head, PWM and complete loaded-lid removal remain clear; loaded-lid clearance after the initial lift remains at least 0.20 mm.

All ten meshes are CLEAN at the configured thresholds in [islands](battery-stop-link-2026-09-25/islands.json), [overhangs](battery-stop-link-2026-09-25/overhangs.json), [thickness](battery-stop-link-2026-09-25/thickness.json) and [fins](battery-stop-link-2026-09-25/fins.json). All ten individual slices, four production plates and the USB fit plate pass without slicer warnings or supports. The [slicer report](slicer-summary.json) gives 119.472 g for the base, 475.9 g / 15.8 h for arranged production and 476.3 g / 16.8 h for individual jobs. The USB fit plate stays at 10.0 g / about 62 minutes.

The static assembled estimate is 1012.8 g, with a 28.3 mm front margin and 21.0° tip angle. Both 3MF projects, all twelve documentation views and both viewer copies are rebuilt. Shared scripts match the print-project skill. The local file viewer requires manual reload because automatic refresh is blocked.
