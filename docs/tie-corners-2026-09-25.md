# Battery ties, four-corner head fastening and USB hold-down — 2026-09-25

The head-fastener arrangement in this report is superseded by [direct head-to-base clamping](head-clamp-2026-09-25.md). Battery and USB features remain in use.

This revision replaces the head-mounted battery shoulder retainers and the single rear row of head fasteners. It also adds an upper return to the central USB keeper. Updated production parts are `base`, `head`, `head_back` and `ball_lid`, plus two new `battery_bridge` pieces. Use the matching new base, head and back cover together.

## Battery restraint

Two integrated cable-tie loops sit under the cell, between its three existing saddles, at x26 and x54. Each has a 4 × 1.8 mm clear tunnel, 2 mm side walls and a 1.6 mm roof. Recessing the tunnel into the floor preserves the battery's installed height: 1.85 mm of floor remains underneath, and the loop top stays 0.5 mm below the nominal cell. Shallow ramps expose both tunnel mouths for threading before inserting the battery.

Two removable printed bridges under the ties transfer their load into the cylindrical cell shoulders. The protection board occupies the full measured cell length, so placing a bare circumferential tie elsewhere along the cell would not establish a board-free band. The bridges provide a 25 mm opening and nominal 0.5 mm clearance above the board. Both feet contact the cell after 0.2 mm of downward settling, leaving 0.3 mm above the board. Their 1.6 mm roofs print flat on the bed, feet upwards; each piece measures 8 × 29 × 14.8 mm.

Use two ties up to 3.6 × 1.2 mm, nominally 150 mm long, with their buckles in front of the cell. The model checks a 6 × 4 × 5 mm buckle envelope and a 130 mm closed band path, leaving about 20 mm for closure and the tail. The head clears the bridges by 0.4 mm and the bands by at least 0.237 mm. Local head-floor recesses retain 1.3 mm of material.

The base's existing right end wall and the left housing wall retain the cell axially. The cable ties retain it vertically even with the head removed. Cut and replace both ties for service. The geometry checks do not measure tie strength, tightening force, bridge deflection, creep or pressure through the real shrink wrap. Verify actual board clearance while tightening gently.

## Four-corner head fastening

The previous four vertical screws shared one row behind the fan because the permanent filter tube and fan blocked the forward tool paths. The new design changes the screw direction: two fasteners are approached from the front after removing the filter cassette, and two from the rear after removing the fan/back-cover assembly. Their axes are distributed across the four corner regions; the front pair sits higher to clear the magnet pockets and PWM controller.

Coordinates below are in the untilted head frame:

| Pair | Axis coordinates x/y/z (mm) | Screw | Insert engagement | Material beneath screw head |
|---|---|---|---|---|
| Front | 7.5/0/68 and 137.5/0/68 | M3 × 8 | 5.7 mm | 2.05 mm |
| Rear | 25/70/53.7 and 131/70/53.7 | M3 × 8 | 6.4 mm | 1.35 mm |

Four rooted base tongues carry Ruthex RX-M3x5.7 inserts in 7 mm pockets. The corresponding head seats have complete bearing rings, clear driver paths and accessible insert mouths. The back cover's forward lip has matching reliefs; its outside face remains continuous. Hardware quantities are unchanged.

With cassette and fan/back cover removed, the head, mat, support cross and magnets lift together 60 mm clear of the base and installed battery ties/bridges. The checked PWM extraction now includes a 6.5 mm shift left after the shaft clears the front rim, before the final upward lift past the rear-right tongue.

## USB hold-down

The central 4 mm wide keeper on the ballast lid now extends 1 mm over the USB module's front edge. Its upper return has a 1.6 mm roof and a sloping underside. Both side wire routes remain open, and the raised 45° base supports still clear the plain lid by 4 mm. Insert the module before installing the lid and keeper.

In the rigid-envelope checks, 0.1 mm upward movement is free; 0.6 mm upward movement and 2.9° of front-edge lift meet the upper return. This establishes geometric capture, not resistance to a specified cable force. The measured 4.3 mm USB-board height includes components and cannot identify a component-free PCB bearing patch. Check actual contact, solder and wire clearances on the updated [USB fit print](../stl/fumex_usb_fit.3mf) before committing to the full base.

The complete loaded-lid removal path still passes: remove head, battery, rocker switch and lid screws; lift 3.4 mm, pull 4 mm forwards, lift 3 mm, pull another 16 mm forwards, shift 0.2 mm right and lift clear. Real wiring needs enough slack for this sequence.

## Verification

Source SHA-256: `e2618ebbf2db47b545d2ba26b4e51981ecd32fe97618b2e99e35e175a1ecc460`.

- [Assembly report](verification.json): PASS; 11 print meshes (9 production types plus 2 optional USB test pieces), 13 production pieces, 435 coaxial feature pairs, 10 service paths and 595 assembly pairs. Every print mesh is closed, consistently wound, one connected body and free of degenerate triangles.
- Print analyses: [islands](tie-corners-2026-09-25/islands.json), [overhangs](tie-corners-2026-09-25/overhangs.json), [thickness](tie-corners-2026-09-25/thickness.json) and [fins](tie-corners-2026-09-25/fins.json) all CLEAN at their configured thresholds. This is a mesh-analysis result, not physical print validation.
- [Bambu slicing report](slicer-summary.json): all 11 individual meshes and all 5 arranged plates PASS without warnings or supports. The production project has 4 plates, 481.3 g and 16.1 h; the optional USB fit plate is 9.9 g and about 62 minutes. Individual production jobs total 17.5 h. No prime tower or mixed-material parts.
- Static tipping estimate: 28.2 mm front margin and 21.0° at 1.019 kg, based partly on estimated bought-part masses. Ballast capacity remains 40.3 cm³, about 189 g at the assumed loose-iron density.
- Printable STLs, both 3MF projects, README renders, `build/viewer.html` and `docs/index.html` were regenerated from the final model. Project scripts match the shared skill.

Remaining physical checks include USB cable-lever loading, actual tie/buckle dimensions and bridge clearance under tension, PETG creep, LED visibility through the 1.8 mm skins, wiring during service, fan/mat clearance and charger temperature. No force, thermal or flexible-body simulation is claimed.
