# FUMEX — a solder fume extractor that bends towards the work

A 120 mm PWM fan pulls the smoke off the soldering iron through a 120 × 120 × 17 mm filter mat and blows it out the back, away from you. The housing stands upright over its electronics bay and then bends 15° forward, so the intake face looks down at the joint instead of past it. Battery powered: a 3.2 V 6000 mAh LiFePO4 pack runs it for hours and charges over USB-C while the fan keeps going.

Designed for a Bambu Lab H2S with AMS in Bambu PETG black and grey. The electronics are the ones from [LEO-AC1](https://github.com/fhirschmann/leo-ac1); only the fan is different.

![Assembly](img/01_assembly.png)

| Exploded | Back |
|:---:|:---:|
| ![Exploded](img/02_exploded.png) | ![Back](img/03_back.png) |

## How the air runs

```
grid of the cassette ─► mat 17 mm ─► corner gussets ─► fan 120 × 25 ─► plenum ─► slots in the back cover
```

The mat sits on the intake side, so flux resin settles in the fleece and the impeller stays clean. It is held by a 2.25 mm lip around the 117 mm intake opening; two half-round notches in that lip let you get a finger behind it. Instead of a flat plate with a round bore in front of the fan — which would have been a 4400 mm² flat overhang over the chamber — the four corners of the chamber fill in at 45°: nothing needs support, the remaining opening is wider than the fan's swept annulus, and those gussets carry the fan's four heat-set inserts.

The filter cassette is held by four magnet pairs and comes off by hand; two finger scoops in the side edges of the intake face give you something to pull against.

The charge module rides in that airflow: it lies on the inside of the back cover with its heatsink facing the fan, a few millimetres behind the blades. Nothing sticks out of the housing, and its heat never reaches the cell.

## Printed parts

| Part | Qty | Material | Size (mm) | Print orientation |
|---|---|---|---|---|
| `head` fan and filter housing | 1 | PETG black | 145 × 145 × 70 | intake face on the bed |
| `base` electronics bay | 1 | PETG black | 145 × 74 × 57.9 | bottom on the bed, open at the top along the 15° joint plane |
| `head_back` back cover | 1 | PETG black | 145 × 144.7 × 9 | outside on the bed; carries the charge module on its inner face |
| `ball_lid` ballast lid | 1 | PETG black | 94.8 × 17.8 × 3 | flat on the bed |
| `cassette` filter cassette | 1 | PETG grey | 143 × 143 × 4.5 | grid face on the bed |
| `knob` speed knob | 1 | PETG grey | Ø 28 × 14 | top on the bed |
| `foot` foot | 4 | TPU | 18 × 16 × 6.5 | ground face on the bed, 100 % infill |

All parts are in the Bambu Studio project [`stl/fumex_all_parts.3mf`](stl/fumex_all_parts.3mf): plate 1 head and ballast lid, plate 2 base and back cover, plate 3 grey parts, plate 4 TPU feet. Filaments: 1 PETG black, 2 PETG grey, 3 TPU. No part mixes colours, so there is no prime tower. Every part prints without supports. Bambu Studio estimates about **0.48 kg and 16.3 hours** in total (head 230 g, base 122 g, back cover 60 g, cassette 52 g, knob 6 g, lid 5 g, feet 4 × 1.5 g).

Print profile: 0.20 mm layers, 4 walls, 5 top/bottom layers, 20 % gyroid (feet 100 %).

## Bought parts

| Part | Qty | Link | Notes |
|---|---|---|---|
| Fan ARCTIC P12 Pro (PST) | 1 | [arctic.de](https://www.arctic.de/en/P12-Pro-PST/ACFAN00306A) | 120 × 120 × 25 mm, 185 g, 600–3000 rpm, 131 m³/h, 6.9 mmH₂O, 12 V / 0.33 A, 0 rpm below 5 % PWM; pressure-optimised, which is what a filter mat needs. Blowing towards the back |
| Filter mat, 120 × 120 × 17 | 1 | – | cut from a cooker hood mat: white fleece plus a carbon layer. **Fleece side to the front**, carbon behind it |
| Battery 3.2 V 6000 mAh LiFePO4 pack with protection board (BMS), JST-PH 2.0 | 1 | [eremit.de](https://www.eremit.de/p/3-2v-6000mah-pack-mit-schutz-arduino-aio-jst-ph-2-0-stecker) | cell Ø 32.5 × 71.6 mm, lying across the bay, protection board up; charge only with a LiFePO4 charger (3.65 V), **no** TP4056 |
| Charge/boost module "2-in-1 3.2 V LiFePO4", **12 V variant** | 1 | [AliExpress](https://de.aliexpress.com/item/1005008094801881.html) | eletechsup LFUPSMA, board 32.2 × 11 × 1.0 mm; IN± 5 V charging, B± battery, O± 12 V. See the note on its 0.32 A rating below |
| Aluminium heatsink 14 × 14 × 6 mm with an insulating silicone thermal pad | 1 | – | on the metal pad behind the charger IC, facing the fan; the pad must cover the whole heatsink face |
| PWM fan controller CNY-FA5-PRO, DC 8–24 V, with potentiometer and switch | 1 | [AliExpress](https://de.aliexpress.com/item/1005010113177510.html) | 41 × 32 × 15 mm, flat in the bay, shaft through the front panel |
| USB-C PD trigger module, Type A (default 5 V) | 1 | [AliExpress](https://de.aliexpress.com/item/1005010610660644.html) | charging socket in the back wall. **Leave pads 1–4 open** (they select 9/12/15/20 V); the charge module only takes 4–6 V, check 5 V with a multimeter before connecting |
| ON-OFF rocker switch, snap-in, 21 × 15 mm (cut-out 19.2 × 12.2 mm) | 1 | [AliExpress](https://de.aliexpress.com/item/1005008871215158.html) | in the right side wall, long side upright |
| LED 3 mm, breathing/fading, 3.3 V, water clear | 1 | [AliExpress](https://de.aliexpress.com/item/1005005336879647.html) | charge indicator beside the knob; it looks through a real hole, black PETG does not glow |
| Resistor 220 Ω, 1/4 W | 1 | – | series resistor for the LED on the 5 V USB input |
| Neodymium disc magnets Ø 10 × 3 | 8 | – | four pairs, glued into open pockets in the intake face and the cassette |
| Resettable PTC fuse Bourns MF-R160 or RXEF160 (1.6 A hold) | 1 | – | optional, between battery plus and the switch, in heat shrink |
| Heat-set inserts Ruthex RX-M3x5.7 | 16 | [ruthex.de](https://www.ruthex.de) | 4 fan, 4 back cover, 4 head screws, 4 feet |
| M3 × 30, ISO 7380 Torx | 4 | – | fan; the frame alone is 25 mm thick, so nothing shorter reaches a thread |
| M3 × 8, ISO 7380 Torx | 12 | – | back cover (4), head onto the base (4), feet (4) |
| M3 × 12 plastic-forming screw (Delta PT, Plastite or similar) | 4 | – | ballast lid, straight into the printed posts — no inserts there |
| Iron offcuts for the ballast | – | – | up to 39 cm³, about 180 g, loose in the trough under its lid |
| JST-PH 2.0 cable, 2-pin, mating the battery plug | 1 | – | battery to the switch and B+ / B− |
| Small cable ties, 2.5–3.6 mm wide | 3 | – | one holds the charge module on the back cover, two for strain relief |
| Silicone wire 24 AWG, red and black | about 1 m | – | USB-C module, switch, LED, 12 V to the PWM controller |
| Heat-shrink tubing 2–3 mm | – | – | every solder joint |
| Foam tape, self-adhesive, 1–2 mm | – | – | a strip above and below the cell keeps it from rattling |

## Wiring

```
USB-C PD trigger 5 V ─┬──► IN+ / IN−   charge/boost module (12 V) ──► O+ / O− 12 V ──► PWM controller ──► 4-pin fan
                      └──► 220 Ω ──► LED ──► IN−
battery (JST-PH, built-in BMS) ──► (PTC) ──► rocker switch ──► B+ / B−
```

- The module charges the battery with up to 1 A and delivers 12 V at the same time, so the fan keeps running while it charges. Use a USB power supply with at least 2 A.
- With the switch in the battery line, off really disconnects the battery, and the battery only charges with the switch on. To charge without the fan running, turn the knob down until it clicks.
- The LED shows that the charging cable is plugged in, not the charge state.
- **Start slow.** The module is specified for 0–0.32 A at 12 V and the P12 Pro draws 0.33 A at full speed, so the top of the knob range sits right at its limit: it gets warm there, and switching on at 100 % may brown out. Turn the knob up once the fan is running. At half speed the pack lasts far longer than the roughly four hours it manages flat out.
- The CN3058E on the module is a linear charger: at 1 A from 5 V it turns about 1.6 W into heat, and it does that exactly while the battery is charging — which is when a LiFePO4 cell least wants to be warm. So the board does not live in the sealed bay at all: it lies on the inside of the back cover, in the plenum, with its heatsink a few millimetres behind the fan. Run the fan while charging and that heatsink sits in a 130 m³/h stream; with the fan off it is at least in the open head instead of beside the cell. Its six wires run down through the notch in the head floor into the base — leave enough slack to lay the cover aside.
- If that is still not cool enough for your taste, replace the ISET resistor (marked 122, 1.2 kΩ) with 2.4 kΩ: half the charge current, half the heat, and 12–13 hours for a full charge.

## Assembly

1. Press in the heat-set inserts: 4 into the corner gussets of the head from the fan side, 4 into the bosses along its side walls from the back, 4 into the bosses under the base rim, 4 into the base floor from below. The ballast lid needs none — its screws form their own thread.
2. Glue the magnets: four into the pockets of the intake face first, then put the other four on top of them, drop the cassette on and glue those into the cassette. The polarity then cannot be wrong.
3. Screw the fan into the corner gussets with M3 × 30, blowing towards the back, and route its cable through the notch in the head floor.
4. Fit the electronics in the base: PWM controller flat on its rib pads with the potentiometer through the front wall, washer and nut from outside; LED glued in beside the knob with its resistor; USB-C module into its channel in the back wall; rocker switch snapped into the right wall. Fix the USB-C and switch wires with a cable tie through the loops beside them.
5. Stick the insulating pad onto the metal pad on the back of the charge module and the heatsink onto the pad. Lay the board on the two ledges on the inside of the back cover, parts towards the cover, heatsink towards the fan, and hold it with one cable tie through the loops above and below it.
6. Fill the ballast trough behind the battery with iron offcuts — up to about 180 g — and screw its lid down with four M3 × 12 plastic-forming screws. Fill it properly or pack the rest with foam; loose pieces under a half-empty lid rattle.
7. Lay the battery into its three saddles, protection board up, cable end to the right, a strip of foam tape above and below.
8. Put a drop of CA gel into the knob bore and push the knob onto the shaft until it bottoms; it then stands 1.2 mm off the wall and turns freely.
9. Set the head onto the base and screw it down with 4 × M3 × 8 from inside, reaching in through the open back. Then screw on the back cover with 4 × M3 × 8.
10. Screw the four TPU feet on from below with M3 × 8; the small peg beside each screw stops them turning.
11. Push the mat in fleece side first, past the lip, and put the cassette on.

To change the mat: pull the cassette off, hook a finger into one of the notches in the lip, pull the mat out, push the new one in.

## Design notes

- Base and head share one 145 × 72 footprint, so the head's floor closes the electronics bay — there is no separate bay cover. The 145 mm width comes from the magnet pockets in the corners of the intake face, not from the fan.
- The head leans forward, so the centre of mass moves towards the front feet. The model computes it from the part masses and checks that it stays at least 15 mm inside the foot polygon: 30.6 mm at the front, which is 23.3° of tip angle at 1.02 kg. The ballast does most of that work — the cell sits well forward so everything behind it is one trough, 39 cm³ or about 180 g of iron offcuts under a screwed lid.
- **Filling the ballast:** only behind the cell, never in front of it — mass ahead of the centre of mass makes tipping worse, and the large free space at the front is exactly the wrong place. The lid keeps the pieces away from the wiring and comes off again, so the offcuts stay reusable. Its four screws form their own thread in the printed posts; a plastic-forming screw tolerates a handful of refits, so do not open it every week.
- Walls 3 mm, base floor 3.2 mm, back cover 4 mm, corner radius 6 mm.
- The head is located on the base by its four screws; there is no register, and the outer contours match.
- The mat is 17 mm of soft fleece, so it seals against the chamber walls: everything downstream of it is filtered air.
- PETG softens well below a soldering iron. Keep the tip away from the housing.

## Build from source

Model: [`fumex.scad`](fumex.scad) (OpenSCAD, parameters at the top), project settings and checks: [`print_project.py`](print_project.py). The scripts in `scripts/` export and check the meshes, slice with the Bambu Studio CLI and build the 3D assembly viewer.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/print_tools.py export     # export and check stl/, asm/, docs/verification.json
.venv/bin/python scripts/analyze.py islands        # floating regions
.venv/bin/python scripts/analyze.py overhangs      # unsupported faces
.venv/bin/python scripts/analyze.py thickness      # walls thinner than 1.2 mm
.venv/bin/python scripts/analyze.py fins           # slender towers with a free tip
.venv/bin/python scripts/slice_check.py            # Bambu Studio CLI, project 3MF
.venv/bin/python scripts/build_viewer.py --copy-to docs/index.html   # viewer page
.venv/bin/python scripts/render_views.py           # img/, transparent PNGs
```

The fan in the model and the viewer is a simple parametric placeholder; no manufacturer CAD is used or needed.

## Licence

Model, printable files, images and documentation: [CC BY-NC-SA 4.0](LICENSE). Scripts in `scripts/`: [MIT](LICENSE-MIT).
