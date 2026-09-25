# Shallow front screw recesses — 2026-09-25

The two front M3 × 8 heads now sit in flat-bottom Ø6.4 × 0.7 mm pockets, matching the rear recess depth. Their upper 0.95 mm remains exposed. The screw axes and the base geometry are unchanged from the [straight-screw revision](straight-front-clamp-2026-09-25.md); only the production head geometry changes.

Front bearing thickness is 1.6 mm, directly backed by the base. Each screw reaches 6.4 mm into its 7 mm pocket, leaving 0.6 mm before the blind end. Rear bearing thickness remains 2.3 mm, with 5.7 mm penetration. The cap tops stay at local z62.3 and the front bearing faces move to z61.6. The intake cutter preserves the complete cap rims and their outer bevels, avoiding a thin remnant beside each pocket.

The soft mat's local geometric allowance drops from 3.45 to 2.75 mm over the screw heads. The printed caps still reach 1.8 mm into its nominal envelope. The tool access, PWM service sequence and fastener count stay the same.

## Verification

Source SHA-256: `fd2fbc0cf9d9d500c3e94c05c317dcb5912706031bdcfc5565e9813130792e07`.

The [assembly report](verification.json) passes: eleven closed single-body meshes, zero degenerate faces, 445 coaxial feature pairs, 595 assembly pairs and ten standard service paths. Both front recesses measure 0.699999 mm at the exported mesh. Bearings, pocket rims, direct backing faces, insert walls and blind floors have 100% material in the probes. The complete PWM service path and ratchet entry/working stroke pass; the assumed ratchet envelope retains a conservative 0.902 mm swing clearance.

All eleven meshes are CLEAN in [islands](recessed-front-screws-2026-09-25/islands.json), [overhangs](recessed-front-screws-2026-09-25/overhangs.json), [thickness](recessed-front-screws-2026-09-25/thickness.json) and [fins](recessed-front-screws-2026-09-25/fins.json). All eleven individual slices, four production plates and the USB fit plate pass without warnings or supports. The [slicer report](slicer-summary.json) gives 477.3 g / 15.9 h for arranged production, 477.8 g / 17.2 h for individual jobs, and 9.9 g / about 62 minutes for the USB fit plate.

Nominal mat overlap is 280.800581 mm³ from the caps plus 98.748029 mm³ from the screws, totalling 379.548611 mm³. The two local zones permit at most 1.8 mm and 2.75 mm depth respectively, with a tightened total-volume gate of 400 mm³. Physical mat forces, print fit, PETG creep and actual ratchet dimensions remain unverified.

The base has zero geometric difference from commit `39c6441` in the Boolean mesh comparison. Only the head production geometry changes. Both 3MF files, twelve documentation views and both viewer copies are rebuilt. The local file viewer needs a manual reload; automatic refresh remains blocked. Shared scripts are unchanged and match the print-project skill.
