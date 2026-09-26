# Direct head-to-base clamping — 2026-09-25

The front fasteners in this snapshot are superseded by [the angled front mounting](front-clamp-2026-09-25.md). The rear mounting remains unchanged.

The previous screw heads did bear on complete rings: a 5.7 mm head over a 3.4 mm clearance hole gives 1.15 mm radial overlap and about 16.44 mm² nominal bearing area. However, a 0.25 mm gap behind each seat interrupted the direct compression path to the insert tongue. Tightening would first deform a seat or tongue. The earlier checks proved head contact, insert engagement and printable geometry, but did not establish a rigid clamp stack or retained preload.

At the user's request, the rear screws now run down through the head floor directly into the base rim. Rear horizontal tongues are removed. The front screws retain their accessible front entry, with the axial gap removed and direct bearing against the base tongues. Guiding clearance remains on the non-clamping faces.

The revised check measures the material immediately on both sides of each clamped interface, as well as the head bearing ring, insert walls and bottom, screw engagement and tool access. This establishes a direct geometric load path; tightening torque, PETG creep and ultimate strength still require physical validation.

The joint illustration now shows the assembled relationship. In the previous illustration the head was lifted while the screws stayed in their installed positions, which obscured their actual bearing surfaces.

## Final joint dimensions

| Pair | Insert entry, local head coordinates (mm) | Screw direction | Material below head | M3 × 8 engagement |
|---|---|---|---|---|
| Front | x7.5/137.5, y4.5, z68 | Towards the rear | 2.05 mm | 5.95 mm |
| Rear | x25/131, y66, z48 | Down, normal to the joint | 2.30 mm | 5.70 mm |

Rear bosses are Ø10 × 9 mm, with Ø4 × 7 mm Ruthex pockets and 2 mm closed ends. The rear screw seats are at local z50.3. All four interfaces have zero nominal axial gap; material probes on both sides are completely filled. The [regression evidence](head-clamp-2026-09-25/backing-regression.json) shows that these same front-backing probes find 0% material in the previous published base and 100% in the revised base.

The base, head and back cover are updated. The cover's forward lip now has small round clearances around the rear screw heads instead of the former large tongue clearances. Screw and insert quantities remain unchanged. Assemble both front screws with the cassette removed and both rear screws before fitting the fan/back-cover assembly.

## Verification

Source SHA-256: `fd7bafbd62166f591abb133d0b37a50bc666eee8350e060e27a03c67f91f983d`.

The [assembly report](verification.json) passes with 11 closed single-body print meshes, zero degenerate faces, 429 coaxial feature pairs, 595 assembly pairs and 10 service paths. Screw-bearing and backing rings, insert walls/bottoms, pressing access and driver access all pass. The back-cover removal path now also checks the head screw heads as fixed obstacles.

- All 11 meshes are CLEAN in [islands](head-clamp-2026-09-25/islands.json), [overhangs](head-clamp-2026-09-25/overhangs.json), [thickness](head-clamp-2026-09-25/thickness.json) and [fins](head-clamp-2026-09-25/fins.json) at the configured thresholds.
- All 11 individual [slices](slicer-summary.json), four production plates and the USB test plate pass without warnings or supports. Production totals: 479.3 g / 16.0 h as arranged plates; 479.8 g / 17.4 h as individual jobs. USB test: 9.9 g / about 62 minutes.
- Static assembled estimate: 1016.5 g, 28.2 mm front margin and 21.0° tipping angle. Bought-part masses remain partly estimated.
- STLs, both 3MF projects, documentation views and both viewer copies were rebuilt. The local viewer tab still requires a manual reload because browser policy prevents refreshing it automatically. Project scripts match the shared skill.

The shared skill now explicitly requires checking the compression path behind a screw seat, in addition to head contact and insert engagement (`a3823d0`). No physical preload, pull-out, strength or creep validation is claimed.
