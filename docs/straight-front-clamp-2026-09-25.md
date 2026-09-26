# Straight front head-to-base screws — 2026-09-25

All four head screws are M3 × 8 and point down in the same direction into the base. The front inserts sit in raised bosses directly behind the front wall. Their screw heads are exposed above flat seats, with no enclosing plastic wall. This supersedes the [angled front arrangement](front-clamp-2026-09-25.md).

## Geometry and assembly

| Pair | Insert entry in the untilted head frame (mm) | Direction | Screw | Bearing thickness | Engagement |
|---|---|---|---|---|---|
| Front left | 25.5, 6.5, 60 | 0, 0, −1 | M3 × 8 | 2.3 mm | 5.7 mm |
| Front right | 119.5, 6.5, 60 | 0, 0, −1 | M3 × 8 | 2.3 mm | 5.7 mm |
| Rear | x25/131, y66, z48 | 0, 0, −1 | M3 × 8 | 2.3 mm | 5.7 mm |

All axes follow the joint normal, exactly as the rear pair did; the housing's existing 15° tilt is unchanged. Front bosses are Ø9.2 × 9 mm, with Ø4 × 7 mm Ruthex pockets and 2 mm closed bottoms. Short hull roots join them to the front wall. Each head seat has a complete bearing ring and a directly contacting base face behind it.

The head's Ø12.2 mm front caps join the lower filter tube between local z59.5 and z62.3. Their Ø9.7 mm guide openings provide 0.25 mm clearance around the bosses, with 1.25 mm radial material closing the surrounding path. The outer bevel ends at the flat seat. No printed material encloses the exposed screw head above it. Two small rectangular front reliefs below local z57.5 remove thin remnants around the supporting roots; at least 1.254 mm front wall remains above them, with the filter-tube floor closed. The intake opening trims the frontmost sector of the cap bevel; the complete bearing ring remains intact.

The nominal mat begins at z60.5. The caps extend 1.8 mm into that envelope and the bare screw heads 3.45 mm. The user accepts local bending of the flexible mat; contact is limited to these two regions and checked by location, depth and volume. This is a geometric allowance, not a model of mat force or stiffness.

Remove the cassette and mat for front fastening. Enter through the intake with the small Wera ratchet and a 25 mm TX10 bit fitted directly into it. Install the rear screws before the fan-and-cover assembly. Refit the mat with its lower edge bent locally over the front heads.

The complete PWM removal path now uses two pitching stages: after the initial lift and shaft retraction, tilt the rear up to 20°, withdraw another 7.9 mm, then continue to 35° before the existing lift and sideways extraction. The earlier direct pitch to 35° collided with the new front boss. Remove the head, battery, switch and loaded ballast lid first, followed by the knob and both PCB screws. Reverse this route for installation.

Total hardware: **14 M3 × 8, four M3 × 30 and 18 Ruthex RX-M3x5.7 inserts**, plus the existing two 2.5 × 8 thermoplastic PCB screws.

## Verification

Source SHA-256: `b45799ece7eedaee3dce09ec6baf3b646c45baf648104f66f1b36f7e49f55787`.

The [assembly report](verification.json) passes with eleven closed single-body meshes, zero degenerate faces, 427 coaxial feature pairs, 595 assembly pairs and ten standard service paths. All four screw-bearing rings, backing rings, insert-wall rings and blind-floor probes contain 100% material; all nominal clamping gaps are zero. The complete 532-pose PWM path passes, including both separate screw withdrawals and knob removal, with a maximum numerical overlap of 0.000052 mm³.

All eleven meshes are CLEAN in [islands](straight-front-clamp-2026-09-25/islands.json), [overhangs](straight-front-clamp-2026-09-25/overhangs.json), [thickness](straight-front-clamp-2026-09-25/thickness.json) and [fins](straight-front-clamp-2026-09-25/fins.json), at the configured thresholds. The base uses the normal CGAL fallback; no mesh repair is applied.

The conservative ratchet model assumes a Ø22 × 14 mm head, 87 mm overall length, 14 mm handle width and 2 mm engagement of the 25 mm bit. Tool dimensions are not measured. Continuous entry and seating sweeps are free; the ±6° swing has 0.969 mm sampled clearance and a conservative 0.902 mm lower bound between angular samples. The cassette and mat are removed for this operation; the actual housing and installed electronics remain obstacles.

Nominal mat contact is 313.069 mm³ for the two printed caps and 108.392 mm³ for the screw heads, together 421.460 mm³. The independent gate allows less than 450 mm³ only in the two specified local zones, with maximum depths of 1.8 and 3.45 mm respectively. No flexible-force, physical tool-fit, creep or strength validation is claimed.

All eleven individual slices, four production plates and one USB fit plate pass without warnings or supports. The [slicer report](slicer-summary.json) gives **477.3 g / 15.8 h** for the arranged production project and 477.9 g / 17.2 h for individual jobs. The USB fit plate remains 9.9 g and about 62 minutes. Static assembled estimate: 1013.9 g, 28.3 mm front margin and 21.0° tipping angle; bought-part masses remain partly estimated.

The changed production parts are the base and head; use the matching current pair. STLs, both 3MF projects, all twelve documentation images and both viewer copies are regenerated. The local viewer tab requires a manual reload because browser policy blocks automatic refresh.

Shared scripts remain identical to the print-project skill. Skill commit `00197d8` records the thin shell remnants created by raised-boss release windows and the need to check them in the print pose.
