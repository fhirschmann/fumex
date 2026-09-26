# Direct battery cable ties — 2026-09-25

The two loose printed bridges between the battery and cable ties are removed at the user's request. The ties now follow the shrink-wrapped pack directly and use the same two floor loops. No replacement spacers are added. The remaining printed parts, including the base and head, retain their geometry.

The removed bridges were load spreaders: they bore on the cell shoulders above a free channel for the BMS. The direct strap envelope instead includes the measured full-length side board (approximately 20 mm wide and 4 mm thick) as part of the wrapped pack. It does not demonstrate pressure isolation of that board. Tighten gently by hand, without crushing the wrap or electronics, and cut the ties for battery removal.

The print set now has eight production types and eleven pieces, including the four feet, plus two optional USB fit types. The bridge STL, plate instances, assembly body and viewer item are removed. The shallow existing head reliefs stay compatible with previously printed housing parts.

## Verification

Source SHA-256: `b918a76215a4885e8c215c0fe97e16c3aa9fbab6748c803e2b0783f3ac3178f7`.

The [assembly report](verification.json) passes with ten closed single-body print meshes, zero degenerate faces, 443 coaxial feature pairs, 561 assembly pairs and ten standard service paths. The complete PWM, USB and loaded-lid paths also pass. The two ties remain in place during the 60 mm head-removal check.

The direct ties clear the head by 2.709 mm. Each band needs about 120.448 mm along its centreline, leaving 29.552 mm for buckle and tail with a nominal 150 mm tie. The existing tunnels have 0.4 mm width and 0.6 mm thickness clearance; all floor, roof and side-wall material probes pass. The battery cable corridor stays clear.

The model deliberately reports cell and BMS contact separately: at 0.1 mm upward pack movement, contact is with the BMS envelope only (3.600053 mm³ per band); at 0.3 mm, contact also includes the cell (0.929589 mm³). This is direct pack restraint, not the previous bridge's load isolation. Clamp force, shrink-wrap integrity and flexible strap behaviour have not been tested physically.

All ten meshes are CLEAN at the configured thresholds in [islands](direct-battery-ties-2026-09-25/islands.json), [overhangs](direct-battery-ties-2026-09-25/overhangs.json), [thickness](direct-battery-ties-2026-09-25/thickness.json) and [fins](direct-battery-ties-2026-09-25/fins.json). Thickness sampling retains 65,253 of 65,414 head rays with the known numerical warnings. All ten individual slices, four production plates and the USB fit plate pass without slicer warnings or supports. The [slicer report](slicer-summary.json) gives 475.8 g / 15.8 h for arranged production and 476.2 g / 16.8 h for individual jobs. The USB fit plate remains 10.0 g / about 62 minutes.

All eight remaining production types and both USB test pieces are geometrically unchanged from commit `2beb14ea21e3c4499f302b4efcb3e42927a42121`. Seven production STLs and the fit lid are byte-identical. The base and fit base have different STL serialization but zero bidirectional Boolean difference and identical bounds. No housing reprint is required for this change.

The static assembled estimate is 1012.6 g, with a 28.3 mm front margin and 21.0° tip angle. Both 3MF projects, all twelve documentation views and both viewer copies are rebuilt. Shared scripts match the print-project skill. The local file viewer requires manual reload because automatic refresh is blocked.
