# Angled front head-to-base screws — 2026-09-25

All four head screws now fasten down into the base. The front pair uses M3 × 16 at 40° outwards from the downward joint normal; the rear pair retains the M3 × 8 mounting from the [rear-clamp revision](head-clamp-2026-09-25.md). The old high front tongues, front-face screw holes and mating windows are removed.

The user accepts bending the soft filter mat locally over the front screw heads. The sealed head wells end 2.7 mm above the nominal bottom of the mat; the screw heads overlap that nominal envelope by about 2.5 mm. Only these two small contact regions are allowed. Both edges of each well mouth are chamfered. This is a permitted local deformation envelope, not a simulation of fleece stiffness or sealing pressure.

## Fasteners and assembly

| Pair | Insert entry in the untilted head frame (mm) | Direction | Screw | Clamped material | Engagement |
|---|---|---|---|---|---|
| Front left | 9.1, 10, 52 | −0.6427876, 0, −0.7660444 | M3 × 16 | 10.3 mm | 5.7 mm |
| Front right | 135.9, 10, 52 | +0.6427876, 0, −0.7660444 | M3 × 16 | 10.3 mm | 5.7 mm |
| Rear | x25/131, y66, z48 | 0, 0, −1 | M3 × 8 | 2.3 mm | 5.7 mm |

Each screw head bears on a complete ring backed directly by the base. Front bosses are Ø9.2 × 9 mm with Ø4 × 7 mm insert pockets and 2 mm closed ends. Their full inclined contact faces remain intact; support roots meet the side walls without obstructing the battery or PWM board. The head wells close the space between the filter tube and the head floor around each shaft.

The base print envelope is now 145 × 74 × 57.3 mm; the head is 145 × 145 × 70 mm in print orientation.

The total hardware becomes **12 M3 × 8, two M3 × 16, four M3 × 30 and 18 Ruthex inserts**, plus the two existing 2.5 × 8 thermoplastic PCB screws.

Remove the cassette and mat for front fastening. Insert a 25 mm TX10 bit directly into the small Wera ratchet and enter through the front. The rear screws go in before the fan-and-cover assembly. Refit the mat with its lower edge bent slightly over the front wells.

## Tool access

The linked tool is the Wera Tool-Check PLUS 1 (05049055001), containing the 8001 A / Zyklop Mini 1, a 25 mm TX10 bit and a ratchet with 6° return angle. See the official [set data sheet](https://hybris-media.wera.de/en/05049055001.pdf) and [ratchet data sheet](https://hybris-media.wera.de/download/pdfgenerator-datasheets/en/05073230001.pdf).

The access model assumes a Ø22 × 14 mm ratchet head, 14 mm handle width and 2 mm bit engagement. These dimensions are not measured. The complete 25 mm bit remains represented above the screw outer face, with a Ø7.4 mm envelope around its hex shank. The head starts 9 mm behind that face. The handle points forwards through the intake.

The check uses the actual exported housing and installed parts. It verifies the complete tool at the screw, continuous convex-piece swept volumes for entry and seating, and a ±6° handle swing with a bound between angular samples. The mat and cassette are removed; electronics, support cross and fan remain obstacles.

## Verification

Source SHA-256: `168a78f6f4feee21a4a681cc80e19e1eff23b0a5b94902d21c74bd88b72ffc9a`.

The [assembly report](verification.json) passes with 11 closed single-body meshes, zero degenerate faces, 445 coaxial feature pairs, 595 assembly pairs and 10 service paths. All four bearing rings, direct backing rings, insert-wall rings and blind-floor probes contain 100% material; every nominal clamping gap is zero. The original complete PWM service path remains unchanged and passes with a maximum numerical overlap of 0.000052 mm³.

- All 11 meshes are CLEAN in [islands](front-clamp-2026-09-25/islands.json), [overhangs](front-clamp-2026-09-25/overhangs.json), [thickness](front-clamp-2026-09-25/thickness.json) and [fins](front-clamp-2026-09-25/fins.json), at the configured thresholds.
- Ratchet entry and seating sweeps have zero collision. The ±6° swing has 0.442 mm sampled minimum clearance and a conservative 0.376 mm lower bound between samples, using the assumed tool envelope.
- Nominal mat overlap is 248.438 mm³ for the head wells and 42.380 mm³ for the screw heads, together 290.818 mm³. The independent gate limits this to the two specified regions, 2.7 mm maximum depth and 330 mm³ total. These are permitted local contacts, not a stiffness or compression-force result.
- Static assembled estimate: 1015.5 g, 28.2 mm front margin and 21.0° tipping angle. Bought-part masses remain partly estimated.

All 11 individual slices, four production plates and the USB test plate pass without warnings or supports. The arranged production project uses 478.8 g and 15.9 hours; individual jobs total 479.4 g and 17.3 hours. The USB fit project remains 9.9 g and about 62 minutes. See the [slicer report](slicer-summary.json).

The updated production geometry is the base and head; use them as a matching pair. The back cover retains the preceding revision's rear-screw clearances. STLs, both 3MF projects, all documentation images and both viewer copies are regenerated. The local viewer tab needs a manual reload because browser policy prevents refreshing it automatically.

Shared scripts remain identical to the skill. Skill commit `32581a6` records angled-boss release clearance, checking nearby PCB service paths, complete ratchet envelopes and bounded flexible contacts. No physical strength, creep, tool-fit or mat-force validation is claimed.
