// FUMEX: solder fume extractor. A 120 mm PWM fan (Arctic P12 Pro) draws through a 120 x 120 x 17 mm
// filter mat and blows out the back; 3.2 V 6000 mAh LiFePO4 pack, same electronics as LEO-AC1.
// Skill openscad-print-project. Units mm, Z up.
// Installed frame: x = width (left to right seen from the front), y = depth (front face at y = 0,
// back at y = body_d), z = height (underside of the base at z = 0).
// The housing bends: the base stands upright, the head above it leans `tilt` degrees forward so the
// intake looks down at the work. Head modules are written in the UNTILTED frame (same axes, head
// floor on the plane z = base_h); head_at() tilts them about the joint line.
// Modules build every part in its INSTALLED position; the part branches at the end put each print
// part into PRINT orientation (largest flat face on the bed at z = 0). The tools set `part`.

include <BOSL2/std.scad>

part = "assembly";   // print part, "assembly", "exploded", "metrics", "none"
$fa = 2;
$fs = 0.6;
eps = 0.01;
tip = 0.2;           // thickness of hull tips: eps-thin tips leave degenerate triangles in Manifold exports

/* [Housing] */
body_w = 145;        // outer width (x); set by the magnet pockets in the corners of the intake face
body_d = 74;         // outer depth (y): base and head share one footprint, so the head closes the bay
wall = 3;            // walls, at least seven 0.4 mm lines
floor_t = 3.2;       // base floor
corner_r = 6;
top_corner_steps = 28; // angular subdivisions of the tangent corner blend
plan_r = 3.5;        // the four vertical edges of the housing. The head has to carry the same radius as
                     // the base or its corners stand proud of the base's, and it is the magnet pockets in
                     // the intake face that cap it: at 6 they would fall outside the rounded corner, and
                     // they cannot move further in without reaching the intake opening (user, 2026-09-23)
corner_rb = 0.5;       // at the joint: small enough that the base rim can follow it, see head_outline()
neck_r = 1;        // the same arc mirrored into the base rim, half a millimetre wider - see joint_neck()
edge_c = 1.2;        // 45 degree chamfer on the bed edges
tilt = 15;           // forward lean of the head (user: the housing itself makes the bend)
base_h = 48;         // joint plane height at mid-depth; the plane rises towards the back
joint_y = 37;        // the joint plane turns about this line (mid-depth)
base_joint_h = 8;    // smooth transition to the tilted head footprint, measured normal to the joint
base_joint_steps = 32;
base_joint_wall_extra = 0.15; // extra material inside the transition keeps normal wall thickness >= 3 mm

/* [Head: fan and filter] */
head_h = 145;        // head height (z) in the untilted frame
front_t = 5.6;       // sealed magnets: 1.2 mm front skin, 3.2 mm cavity, 1.2 mm rear skin
open_sq = 117;       // square opening in the intake face; its lip holds the mat in the chamber
open_r = 3;
mat_stop_rise = 1.5;  // flank of the rear lip: 1.5 mm of depth per mm inwards, so it is not an overhang
mat_support = [4, 5, 123, 23.1, 32.9, 8, 58.5, 0.2];
// Cross: bar width/depth, outer span, front/rear y, end-pad width, post inner radius, pocket clearance.
// Printed separately, mat-facing side down; four end posts are trapped between the head and fan frame.
chamber_sq = 121.5;  // filter chamber, 0.75 mm wider than the hand-cut mat all round
chamber_d = 17.5;    // the mat is 17 mm (user, cut from a cooker hood mat)
tube_w = 3;          // wall of the filter chamber inside the shell
lug_d = 10;          // chamber depth behind the mat; the rear lip runs on to the fan frame's seat
plenum = 11.9;       // shortened by the thicker intake face; outer housing depth stays unchanged
back_t = 4;
lip_h = 4;           // back cover lip reaching into the head
lip_t = 3;
lip_cl = 0.25;
boss_d = 8;          // back cover bosses along the walls, clear of the fan
boss_inset = 6.5;    // back cover boss axes from the left and right faces
boss_bottom = 10;    // ... and of the lower pair above the head floor: its screw pocket must stay
                     // inside the cover, whose lower edge sits on the floor
cover_gap = 0.3;     // the back cover runs the full height of the head (user, 2026-09-22); its lower edge
                     // keeps this much off the joint plane, otherwise it grinds along the base rim on its
                     // way off and the path check sees the facets of two coplanar faces touching
grid_bar = 2.5;      // intake and exhaust grid
grid_gap = 9;
grid_r = 1.2;
exhaust_sq = 121;
scoop = [16, 2];     // finger scoops at both side edges of the intake face: diameter, depth (45 degree cone)
guide = [2.4, 16];   // L-ribs guiding the fan onto its seat: thickness, leg length
guide_c = 1.2;       // 45-degree lead-in on the two inner edges at the rear of each guide
fan_post_d = 8;      // spacer posts on the back cover, carrying the fan and its inserts
fan_cable_slot = [32, 48, 56.7]; // x limits and front y; open to the rear for lateral cable insertion

/* [Fan: Arctic P12 Pro, 120 x 120 x 25 mm PWM, 0.33 A at 12 V] */
fan_size = 120;
fan_t = 25;
fan_pitch = 105;     // mounting hole spacing (120 mm fans)
fan_hole_d = 4.5;
fan_blade_d = 113;
fan_cl = 0.4;        // clearance per side in the corner guides

/* [Filter cassette: grid panel held by four magnet pairs] */
cass_t = 5.6;        // sealed magnets: 1.2 mm skins on both sides of the 3.2 mm cavity
cass_c = 1.2;        // 45 degree bevel on the finished contour; 4.4 mm of the rim stays straight.
                     // The narrowed side contour and the magnet pockets limit the bevel to 1.2 mm.
cass_inset = 1;      // flange inside the head outline, leaves a ledge beside the finger scoops
mag = [10.3, 3.2];   // enclosed cavity for a 10 x 3 disc; insert during the print pause
mag_skin = 1.2;     // six solid 0.2 mm layers on each axial side; no glue-in opening
mag_off = 62.5;      // magnet axes from the head centre, on both diagonals. 10 mm inset: 1.3 mm of material
                     // to the rounded plan corner and 1.8 mm to the intake opening

/* [Battery, 3.2 V 6000 mAh LiFePO4 pack, lying across the bay] */
bat_d = 32.5;        // measured cell body without the protection board (LEO-AC1, 2026-09-15)
bat_l = 71.6;        // measured cell-body length; cable end to the right
bat_bms = [20, 4];   // protection board, here facing up: width, thickness
bat_x0 = 4;
bat_cy = 35;         // well forward: everything behind the cell is ballast (user, 2026-09-22). Not
                     // further, or the tilted run-outs of the front head screw bosses reach the cell
bat_cz = 22;
bat_clear = 0.5;
cradle_x = [12, 40, 68];
cradle_t = 4;
cradle_out = 2.5;    // saddle material beyond the cell: every mm here is a mm less ballast trough
bat_stop_gap = 0.5;  // axial clearance to the base's right-hand battery stop
bat_stop_w = 3;      // floor-rooted end wall thickness
bat_stop_y = [30, 51]; // stays ahead of the ballast lid
bat_stop_top = 29;   // below the BMS and upper cable exit
bat_stop_c = 0.4;    // soften the top against the cell's insulating wrap
bat_stop_link_overlap = 1; // embed the floor-rooted stop connection into the trough front wall
bat_tie_x = [26, 54]; // two floor-rooted loops between the three existing saddles
bat_tie_slot = [4, 1.8]; // clear tunnel width and height, for ties up to 3.6 x 1.2 mm
bat_tie_floor = 1.85; // solid floor remaining below the recessed tie tunnels
bat_tie_roof = 1.6;
bat_tie_span = 8;     // bridge length along the tie route (Y)
bat_tie_wall = 2;
bat_tie_head_clearance = [8.8, 18, 13, 1.7]; // retained head relief: x width, y start, y span, depth
bat_tie = [3.6, 1.2, 150];                // conservative band width/thickness, minimum nominal length

/* [PWM fan controller CNY-FA5-PRO: board flat in the bay, potentiometer through the front wall] */
pwm_pcb = [41.05, 32, 1.6]; // measured length (here along y), width (x), PCB thickness
pwm_total_h = 18;    // measured 15 without the fan connector, +3 estimated for the plugged connector
pwm_total_len = 56.30;      // measured rear PCB edge to shaft tip
pwm_comp_h = pwm_total_h - pwm_pcb[2];
pwm_pins = 3;        // solder pins below the PCB (measured 2-3)
pwm_edge_free = 1.5; // pin-free strips along both long edges (measured)
pwm_pad = 1.2;       // rib pads under those strips
pwm_rib = 3;
pwm_hole_d = 3.2;   // measured PCB holes, user 2026-09-23
pwm_hole_edge = 3;  // hole centres from the front and each side edge
pwm_boss_d = 6;     // user confirmed clear bearing area on both PCB faces
pwm_core_d = 2.0;   // starting pilot for 2.5 mm plastic-forming screws; verify on printed PETG
pwm_core_depth = 7.4;
pwm_install_lift = 3.5; // concealed vertical travel for lifting the board off its screw bosses
pwm_core_entry = [2.7, 0.7]; // relieved mouth: diameter, depth
pwm_screw = [2.5, 8, 4.5, 2.5]; // shank, under-head length, measured head diameter, conservative head-height envelope
pot_x = 116;         // potentiometer axis in the front panel (user, 2026-09-23: further right)
pot_z = 21;          // above the front foot bosses, low enough that the knob clears the front rim
pot_axis_h = 6.3;    // PCB top to shaft centre
pot_shaft_d = 5.8;   // measured outside the knurling
pot_shaft_free = 9.5;
pot_bush = [6.73, 5];       // bushing outside diameter, thread length from the housing shoulder (measured)
pot_shoulder_y = 1.8; // preserve the fitted PCB position; the switch limits rearward movement
pot_bush_cl = 0.4;
pot_housing = 13;    // potentiometer housing on the PCB edge (12 mm pot assumed)
pot_recess_r = 10;
pot_tab = [2.1, 0.8, 1.2, 2.1];   // anti-rotation tab below the shaft (measured)
pot_tab_cl = 0.4;    // clearance per side around the anti-rotation tab
pot_pcb_cl = 0.3;

/* [Speed knob] */
knob_d = 24;
knob_skin = 2;       // solid above the shaft end; knob_len follows the pot shaft, not the other way

knob_gap = 1.5;      // underside off the wall face
knob_bore_over = 0.3;
knob_cavity_d = 13;
knob_stem_d = 10;
knob_bore_cl = 0;    // nominal 5.8 bore; validate the push fit on the real knurled shaft
knob_slit = [1, 6];
knob_flutes = 18;
knob_flute = [2, 1.2];
knob_c = 1.2;
knob_mark = [1.6, 7.5, 0.8];   // pointer groove in the top face (single colour, no inlay)

/* [Charge/boost module: eletechsup LFUPSMA, 12 V variant, in the bay under a vent] */
// The board stands on its long edge above the ballast lid, components towards the front and
// heatsink towards the back. The cool OUT end is held like LEO-AC1; the hot IN end hangs free.
// Plenum air can pass the component side and the heatsink before leaving the back vents.
chg_pcb = [32.2, 11, 1.0];  // measured length (here along x), width (z), thickness (y)
chg_comp_h = 2.7;    // parts above the PCB (3.7 total, measured)
chg_comp_end = 2;    // component envelope leaves the PCB end pads exposed
chg_cx = 70;         // board centre on the ballast lid, between its two screws
chg_cy = 60;         // PCB mid-plane across the lid; both board faces are exposed to air
chg_stand = 3.2;     // lower PCB edge above the lid; the heatsink extends 1.5 mm below it
chg_sink = [14, 14, 6, 1];  // user's heatsink behind the IC: length, width, height, insulating pad
chg_sink_end = 9.5;  // near end of the heatsink from the IN end; it overhangs that end by 4.5 mm
// The LEO-AC1 tie position misses the output wires, solder jumpers and hot IC end.
chg_tie = [2.5, 1.2, 0.3, 12.5, 2]; // width, thickness, tunnel clearance, distance from OUT, front web skin
chg_web_gap = 1.5;
chg_web_touch = [9, 18];             // board-back bearing measured from the cool OUT end
chg_web_w = 4;                      // central bearing width, clear of both long-edge solder pads
chg_web_back = 1.6;                 // wall behind the tie tunnel
// The vent over the board is a row of slots, not one opening: printed with the intake face on the bed
// the head floor is a vertical wall, so one 38 mm opening leaves a 113 mm2 flat bridge at its far edge.
chg_vent = [6, 9, 6, 10];    // slot width (x), pitch, count, depth (y) in the head floor over the board
chg_vent_y = 56.7;          // fixed above the electronics; retain 3.3 mm of rear floor when the fan moves

/* [Ventilation slots in the back wall (user, 2026-09-22), above the ballast lid] */
vent = [2, 5, 12, 14, 0];     // slot width, pitch, count, height, rise per slot (user: not staggered)
vent_xz = [34, 32];  // left end and lower edge of the row

/* [USB-C charging socket: PD trigger module (pads 1-4 open = 5 V) in the back wall] */
usbc_board = [12.88, 10.35, 4.30];  // measured: length without the receptacle (y), width (x), height (z)
usbc_protrusion = 1.5;
usbc = [usbc_board[0] + usbc_protrusion, usbc_board[1], usbc_board[2]];
usbc_shell = [8.9, 3.22];
usbc_shell_bottom = 1.1;
usbc_plate = usbc_protrusion;   // local wall thickness: PCB edge inside, receptacle face flush outside
usbc_xz = [106, 45]; // above the ballast lid (user, 2026-09-22), high enough that the lid lifts out under it
usbc_floor = 6;      // rear PCB seat; a short bridge between the two wall gussets
usbc_cl = 0.2;
usbc_wall = 2;
usbc_stop_w = 4;     // central PCB-end bearing; both side wire exits stay open
usbc_keeper_w = 4;  // centered removable L-stop on the ballast lid
usbc_keeper_gap = 0.4; // stem clears the front of the fixed gusset
usbc_keeper_top = [1, 1.6, 1.25]; // overlap past module edge, roof thickness, rise/run in print pose
usbc_keeper_brace = [8, 8, 2, 0.2]; // rearward run, height, side extension, overlap into stem
usbc_gusset_lid_gap = 4; // permits the first 3.4 mm service lift above the battery end stop
usbc_guide_lead = 0.9; // side guides extend just ahead of the PCB, keeping the sloped tips solid

/* [Power switch: measured 14.7 x 20.9 mm rocker, snap-in, in the right side wall] */
// Behind the PWM board, not above it: that is what lets the board move right and the switch move down
// (user, 2026-09-23). The trough's front wall steps back on the right so the switch body fits.
sw_yz = [50, 26];    // centre in the right wall, behind the PWM board and beside the battery
sw_cut = [12.2, 19.2];      // measured panel hole; long side upright, so the printed bridge is short
sw_cut_cl = 0.2;     // PETG holes come out undersize
sw_bezel = [14.7, 20.9, 2]; // outside width (y), height (z), bezel thickness
sw_rocker = 5;
sw_body = [sw_cut[0] - 0.2, sw_cut[1] - 0.2, 11];
sw_total_depth = 23;
sw_pins = sw_total_depth - sw_bezel[2] - sw_rocker - sw_body[2];
sw_panel = 1.5;
sw_well = [5, 0.2, 2.2];    // depth below the outer face, floor margin, wall measured horizontally

/* [LED holders] */
led_d = 3;           // nominal 3 mm breathing LED, glued into the blind pocket from inside
led_xz = [[78, 21], [90, 21]]; // second holder beside the existing charge indicator; wiring is unspecified
led_cl = 0.2;        // retain the LEO-AC1 bore and flange bearing ring
led_skin = 1.8;      // pockets and LEDs moved 1 mm inward to reduce show-through of the internal holes
led_boss = [7, 6.8]; // boss diameter and rear face from the front; preserves the LED's original seated depth

/* [Ballast trough with a screwed lid (user, 2026-09-22): loose iron offcuts, no resin] */
// Only mass behind the centre of mass helps against tipping, so the cell moved forward and everything
// behind it is one trough. A lid instead of potting keeps it serviceable and stops the offcuts from
// reaching the wiring; two side screws fasten it to Ruthex M3 inserts.
ball = [3, 142, 53, 26];    // interior x from / to (both housing walls), front wall outer face (y),
                     // rim and lid underside (z). Full width and lower, with the USB-C socket above it
                     // (user, 2026-09-22); the rim stays below the run-outs of the rear head screw bosses
ball_wall = 2;
ball_post = 10;      // screw posts for the lid, standing free on the trough floor
ball_post_x = [10, 117];    // right fastener clears the switch well, PWM removal and head-boss tool shadow
ball_post_y = [63, 56.8];
ball_post_front_flat = 3.85; // 1.85 mm insert wall; front at y52.95 avoids a coplanar split against the y53 trough wall
ball_lid_t = 3;
lid_pocket = 1.2;    // counterbore in the lid: at head_pocket's 1.9 the head bore on 1.1 mm (audit A5)
ball_lip = 0;        // no lip over the front wall: the cell has to lift past it (battery_out)
ball_step = [118.5, 64]; // leave the switch wiring and the straight lid-removal route open
ball_lid_ear_r = 4.6;  // keep the right screw pocket enclosed beside the enlarged switch recess
ball_switch_corner = [128, 142, 78]; // diagonal continues into the rear wall, shortening the lid's right end
ball_rim = 0.4;      // trough walls end this far below the posts, so the lid bears on the two posts
                     // alone and no two faces of the base share the plane z = ball[3]

/* [Feet: four TPU pads, each screwed with one M3 x 8 from below] */
foot = [18, 16, 4.5];   // length (x), width (y), height
// wide apart for stability, and clear of the PWM board above them
// All four pads inside the housing outline, and inside the bed chamfer too: flush with the outline they
// stood proud of the chamfered bottom edge (user, 2026-09-23).
foot_xy = [[18, 10], [127, 10], [18, 61], [127, 61]];
// A keying pocket in the bottom face would be a 275 mm2 flat overhang per foot (analyze.py overhangs),
// so the pad sits flat and a small peg beside the screw stops it turning.
foot_peg = [3, 2, 7];   // anti-rotation peg on the foot: diameter, length, distance from the screw axis
foot_peg_cl = 0.3;
foot_c = 1;
foot_cl = 0.2;
foot_head_recess = 1.2;
foot_boss = [9, 9];  // boss inside the floor for the insert: diameter, height; 2 mm of material stay
                     // above the pocket (1 mm was below the 1.2 mm wall limit of analyze.py thickness)

/* [Screws, M3 heat-set inserts] */
insert_hole_d = 4.0; // Ruthex RX-M3x5.7
insert_len = 5.7;
insert_depth = 7;    // pocket depth; datasheet: at least L + 1 = 6.7
insert_w_min = 1.6;
screw_clear_d = 3.4;
screw_head_d = 5.7;
screw_head_h = 1.65;
head_pocket = [6.4, 1.9];
// All four screws clamp directly down into base inserts, normal to the head joint.
rim_screws = [[25.5, 6.5], [119.5, 6.5], [25, 66], [131, 66]];
rim_front_entry_z = 60;     // raised base insert face, directly behind the front wall
rim_front_root_z = 46;      // short support-free root joins the front wall below the joint
rim_front_cap_d = 12.2;
rim_front_cap_c = 0.3;
rim_front_bearing = 1.6;    // 0.7 mm recess leaves 6.4 mm of the M3 x 8 in the 7 mm pocket
rim_front_cap_bottom = 59.5; // overlaps the filter-tube floor below the shallow screw pocket
rim_seat_d = 8.8;
rim_recess = 0.7;           // rear floor: 2.3 mm bearing and 5.7 mm M3 x 8 engagement
rim_rear_boss_d = 10;
rim_rear_boss_len = 9;
rim_boss_d = 9.2;
rim_boss_depth = 9;         // 7 mm insert pocket and 2 mm closed end
rim_fit_gap = 0.25;         // side clearance, never between the clamping faces
// ISO 7380 button head Torx from the user's set (M3 x 6, 8, 10, 12, 16, 25) except the fan screws
len_lid = 8;         // 1.8 mm lid bearing plus 6.2 mm into the 7 mm insert pocket
len_fan = 30;        // M3 x 30, bought: through the 25 mm frame, 5 mm of thread in the insert
len_back = 8;
len_head = 8;
len_head_front = 8;
len_foot = 8;

// ---------- derived values ----------
head_cz = base_h + head_h / 2;
head_y = [front_t, front_t + chamber_d, front_t + chamber_d + lug_d,
          front_t + chamber_d + lug_d + fan_t, body_d - back_t];   // chamber, mat end, fan, plenum, cover
tube_sq = chamber_sq + 2 * tube_w;
pot_mount_t = pot_shoulder_y; // housing shoulder depth, independent of front fastening hardware
pot_nose_len = pwm_total_len - pwm_pcb[0] - pot_shaft_free - pot_bush[1];
pwm_wall_gap = pot_mount_t + pot_nose_len - wall;    // negative: the PCB edge reaches into the wall slot
pot_recess = wall - pot_mount_t;
pwm_pcb_slot = max(0, -pwm_wall_gap) + pot_pcb_cl;
pwm_y0 = wall + pwm_wall_gap;
pwm_z0 = pot_z - pot_axis_h - pwm_pcb[2];
pwm_x = [pot_x - pwm_pcb[1] / 2, pot_x + pwm_pcb[1] / 2];
knob_sleeve_z = max(0, pot_bush[1] - pot_mount_t - knob_gap + 0.3); // clear the threaded bushing
knob_bore_top = pot_bush[1] - pot_mount_t + pot_shaft_free - knob_gap + knob_bore_over;
knob_len = knob_bore_top + knob_skin;   // 15.0 mm proud of the front face, and all of it is the 9.5 mm
                                        // shaft: the knob cannot get flatter without cutting it (user
                                        // asked 2026-09-23, chose not to cut). knob_gap stays at 1.5 -
                                        // LEO-AC1 measured that 0.5 rubbed when the knob was pressed home.
usbc_y0 = body_d - wall - usbc_board[0] + usbc_plate;
chg_z0 = ball[3] + ball_lid_t + chg_stand;              // lower edge of the upright PCB
chg_x0 = chg_cx - chg_pcb[0] / 2;                       // OUT end of the board
chg_y0 = chg_cy - chg_pcb[2] / 2;                       // component-side PCB face
chg_sink_z = chg_z0 + (chg_pcb[1] - chg_sink[1]) / 2;   // heatsink lower edge, centred over the PCB width
chg_sink_cx = chg_x0 + chg_pcb[0] - chg_sink_end + chg_sink[0] / 2;   // heatsink centre along x

function base_top(y) = base_h + (y - joint_y) * tan(tilt);
function fan_holes() = [for (sx = [-1, 1], sz = [-1, 1]) [body_w / 2 + sx * fan_pitch / 2, head_cz + sz * fan_pitch / 2]];
function mag_xz() = [for (sx = [-1, 1], sz = [-1, 1]) [body_w / 2 + sx * mag_off, head_cz + sz * mag_off]];
// four screws are enough for the back cover (user, 2026-09-22)
function head_bosses() = [for (sx = [-1, 1], z = [base_h + boss_bottom, base_h + head_h - boss_inset])
                          [body_w / 2 + sx * (body_w / 2 - boss_inset), z]];
function rim_bosses() = rim_screws;
function rim_dir(p) = p[1] < body_d / 2 ? 1 : -1;
function rim_entry(p) = [p[0], p[1], rim_dir(p) > 0 ? rim_front_entry_z : base_h];
function rim_axis(p) = [0, 0, -1];
function rim_bearing(p) = rim_dir(p) > 0 ? rim_front_bearing : wall - rim_recess;
function rim_length(p) = rim_dir(p) > 0 ? len_head_front : len_head;
function rim_seat_point(p) = rim_entry(p) - rim_axis(p) * rim_bearing(p);
// lowest point of the cell over y, or clear of it altogether
function bat_low(y) = abs(y - bat_cy) >= bat_d / 2 + bat_clear ? 1e6
                    : bat_cz - sqrt(pow(bat_d / 2 + bat_clear, 2) - pow(y - bat_cy, 2));
// Two side fasteners share the centre line of the trough and clear the curved upper rim.
function ball_posts() = [for (i = [0:len(ball_post_x) - 1]) [ball_post_x[i], ball_post_y[i]]];
// both rear corners of the lid meet a rounded housing corner
function pot_tab_z() = [pot_shaft_d / 2 + pot_tab[3] - pot_tab_cl, pot_bush[0] / 2 + pot_tab[3] + pot_tab[1] + pot_tab_cl];

assert(head_y[4] + back_t == body_d, "Head depth must fill the shared footprint");
assert(wall >= 3 * 0.4, "Walls below three perimeters");
assert(lug_d - insert_depth >= 3, "Less than 3 mm of gusset in front of the fan insert pockets");
assert(mat_support[0] >= 4 && mat_support[1] >= 5, "Filter cross is too slender");
assert(mat_support[3] > front_t + 17 && mat_support[3] + mat_support[1] <= head_y[2] - 5,
       "Filter cross leaves insufficient clearance to the mat or fan");
assert(mat_support[4] <= head_y[2] - mat_support[7], "Filter support posts collide with the fan");
assert(tube_sq / 2 - mat_support[2] / 2 - mat_support[7] >= 2,
       "Filter support pockets leave too little tube wall");
// where the insert pocket starts, the gusset flank must still clear the insert by the datasheet wall
assert(fan_post_d / 2 >= insert_hole_d / 2 + insert_w_min, "Fan posts too thin for the inserts");
assert(guide_c > 0 && guide[0] - guide_c >= 1.2, "Fan guide lead-in leaves less than three perimeters");
assert(head_y[4] - head_y[3] >= insert_depth + 1, "Fan posts too short for the inserts");
assert(open_sq < chamber_sq - 2, "Intake lip does not hold the mat");
assert(pot_mount_t > 1.2, "Front wall around the bushing too thin");
assert(pwm_screw[1] - pwm_pcb[2] <= pwm_core_depth - 1, "PWM screw bottoms in its pilot hole");
assert(pwm_z0 - pwm_core_depth - floor_t >= 2, "PWM pilot leaves too little material over the floor");
assert(pwm_boss_d >= pwm_screw[2] + 1.2, "PWM boss too narrow for the screw bearing");
assert(pwm_boss_d <= 2 * pwm_hole_edge, "PWM bosses project beyond the confirmed mounting pads");
assert(base_top(0) > pot_z + knob_d / 2 + 2, "Knob reaches over the front rim");
assert(chg_sink_z > ball[3] + ball_lid_t + 1.2, "Heatsink too close to the ballast lid");
assert(chg_y0 - chg_comp_h > ball[2] + 1 && chg_y0 + chg_pcb[2] + chg_sink[3] + chg_sink[2] < body_d - wall - 1,
       "Charge module leaves no air passage around its two faces");
assert(min([for (q = ball_posts()) abs(q[0] - chg_cx) - chg_pcb[0] / 2 - 2]) > 2,
       "Charge module holder sits on a ballast lid screw");
assert(max(chg_z0 + chg_pcb[1], chg_sink_z + chg_sink[1]) + 5 < base_top(chg_y0 - chg_comp_h),
       "Less than 5 mm over the charge module to the head floor");
assert(vent_xz[1] > ball[3] + ball_lid_t, "Back wall slots would let the ballast out");
assert(mag_skin >= 1.2 && cass_t >= mag[1] + 2 * mag_skin - eps,
       "Cassette needs closed skins on both sides of the magnets");
assert(front_t >= mag[1] + 2 * mag_skin - eps,
       "Head needs closed skins on both sides of the magnets");
assert(plan_r + cass_c < body_w / 2 - mag_off - mag[0] / 2, "Cassette bevel cuts into the magnet pockets");
assert(len_fan - fan_t >= 5, "Fan screws reach less than 5 mm into the insert");
assert(len_lid - (ball_lid_t - lid_pocket) < insert_depth, "Ballast lid screws reach the pocket floor");
assert(len_lid - (ball_lid_t - lid_pocket) >= insert_len, "Ballast lid screws miss full insert engagement");
assert(ball_post / 2 >= insert_hole_d / 2 + insert_w_min, "Ballast insert posts are too thin");
assert(ball_lid_ear_r >= head_pocket[0] / 2 + 1.2, "Right lid screw pocket loses its enclosed rim");
assert(led_skin >= 1.2 && led_skin < wall, "LED front skin must meet the normal wall-thickness threshold");
assert(min([for (p = foot_xy) bat_low(p[1])]) > foot_boss[1], "Foot boss reaches into the battery");
assert(bat_stop_gap >= 0.3 && bat_stop_gap <= 0.6, "Battery end stop has excessive axial play");
assert(bat_tie_floor >= 1.8 && bat_tie_roof >= 1.6 && bat_tie_wall >= 2,
       "Battery tie loops need continuous floor, roof and side walls");
assert(bat_cz - bat_d/2 - (bat_tie_floor + bat_tie_slot[1] + bat_tie_roof) >= 0.5 - eps,
       "Battery tie anchors touch the cell underside");
assert(bat_stop_w >= 3 && bat_stop_top > bat_cz + 4, "Battery end wall is too slender or low");
assert(bat_stop_y[1] <= ball[2] - 0.2, "Fixed battery stop reaches the removable ballast lid");
assert(bat_stop_top <= bat_cz + bat_d / 4 - 1,
       "Battery stop must stay below the BMS and cable exit");
assert(foot_boss[1] - insert_depth >= 1.2, "Foot insert pocket floor thinner than three perimeters");
assert(floor_t - foot_peg[1] >= 3 * 0.4, "Floor under the foot peg holes thinner than three perimeters");
assert(min([for (p = rim_bosses()) rim_length(p) - rim_bearing(p)]) >= insert_len - eps,
       "Head screws must engage the complete 5.7 mm insert");

// ---------- helpers ----------
module rrect(size, r) offset(r = r) offset(delta = -r) square(size, center = true);
module bounds_rect(a, b) translate([min(a[0], b[0]), min(a[1], b[1])]) square([max(abs(b[0] - a[0]), eps), max(abs(b[1] - a[1]), eps)]);
// 2D children in (x, z) extruded along y, and in (y, z) extruded along x
module along_y(y0, y1) translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children();
module along_x(x0, x1) translate([x0, 0, 0]) multmatrix([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]) linear_extrude(x1 - x0) children();
module cyl_y(c, y0, y1, r1, r2 = -1) translate([c[0], y0, c[1]]) rotate([-90, 0, 0]) cylinder(r1 = r1, r2 = r2 < 0 ? r1 : r2, h = y1 - y0);
module cyl_x(c, x0, x1, r1, r2 = -1) translate([x0, c[0], c[1]]) rotate([0, 90, 0]) cylinder(r1 = r1, r2 = r2 < 0 ? r1 : r2, h = x1 - x0);
// Point the local +z axis along an axis-aligned direction
module axis_orient(d) {
    if (d[2] < 0) rotate([180, 0, 0]) children();
    else if (d[1] > 0) rotate([-90, 0, 0]) children();
    else if (d[1] < 0) rotate([90, 0, 0]) children();
    else if (d[0] > 0) rotate([0, 90, 0]) children();
    else if (d[0] < 0) rotate([0, -90, 0]) children();
    else children();
}
module head_at() translate([0, joint_y, base_h]) rotate([tilt, 0, 0]) translate([0, -joint_y, -base_h]) children();
// generous in x and y: tilted, a cube that only just covers the footprint leaves a sliver of the front
// wall uncut, which the slicer then reports as an empty layer
module joint_halfspace() head_at() translate([-40, -40, base_h]) cube([body_w + 80, body_d + 80, 400]);

module base_outline(inset = 0) translate([body_w / 2, body_d / 2]) rrect([body_w - 2 * inset, body_d - 2 * inset], max(plan_r - inset, 0.5));
// The same footprint as a prism, to give the head the base's vertical edges. The cassette stands cass_t in
// front of it, so its own prism runs on forward at the width the footprint has at y = 0.
module plan_prism() translate([0, 0, base_h - 1]) linear_extrude(head_h + 2) base_outline();
// Local, tangent blend of the plan and elevation corner profiles.
// A compact smooth cutoff avoids vanishingly small cuts beside the original arcs.
// 0.001 mm of cutter overlap keeps coincident tangencies out of the STL boolean.
// The regular profiles stay unchanged outside the plan_r x corner_r corner field.
function blend_index(i, j, n) = i * (n + 1) + j;
function blend_smooth(t) = t * t * (3 - 2 * t);
function blend_x(a, b) = let (hi = max(a,b), lo = min(a,b),
    t = hi > 0 ? min(1,max(0,(lo / hi - 0.05) / 0.10)) : 0)
    hi + blend_smooth(t) * (sqrt(a * a + b * b) - hi);
module top_corner_cut(steps = top_corner_steps) {
    n = steps + 2;
    ring = (n + 1) * (n + 1);
    surface = [for (i = [0:n], j = [0:n])
        let (a = plan_r * (1 - cos(90 * min(steps,max(0,i-1)) / steps)),
             b = corner_r * (1 - cos(90 * min(steps,max(0,j-1)) / steps)))
        [blend_x(a, b) + 0.001, i == 0 ? plan_r + eps : i == n ? -eps : plan_r * (1 - sin(90 * (i-1) / steps)),
         base_h + head_h - corner_r + (j == 0 ? -eps : j == n ? corner_r + eps : corner_r * sin(90 * (j-1) / steps))]];
    rear = [for (p = surface) [-1, p[1], p[2]]];
    faces = concat(
        [for (i = [0:n - 1], j = [0:n - 1])
            let (a = blend_index(i,j,n), b = blend_index(i,j+1,n),
                 c = blend_index(i+1,j+1,n), d = blend_index(i+1,j,n))
            each [[a,b,c], [a,c,d], [ring+a,ring+c,ring+b], [ring+a,ring+d,ring+c]]],
        [for (j = [0:n - 1]) let (a = blend_index(0,j,n), b = blend_index(0,j+1,n))
            [a,ring+a,ring+b,b]],
        [for (j = [0:n - 1]) let (a = blend_index(n,j,n), b = blend_index(n,j+1,n))
            [a,b,ring+b,ring+a]],
        [for (i = [0:n - 1]) let (a = blend_index(i,0,n), b = blend_index(i+1,0,n))
            [a,b,ring+b,ring+a]],
        [for (i = [0:n - 1]) let (a = blend_index(i,n,n), b = blend_index(i+1,n,n))
            [a,ring+a,ring+b,b]]);
    polyhedron(points = concat(surface, rear), faces = [for (f = faces) [for (i = [len(f)-1:-1:0]) f[i]]], convexity = 4);
}
module top_corner_blends() for (side = [0,1], back = [0,1])
    translate([side * body_w, back * body_d, 0])
        scale([side ? -1 : 1, back ? -1 : 1, 1]) top_corner_cut();

// corner_r at the top, corner_rb at the two corners that sit on the joint plane. They have to be smaller:
// whatever radius the head has there, the base rim has to follow it or the head's side walls curve away
// from the base and leave a step. At corner_r = 6 that neck would remove the whole 3 mm side wall of the
// base over its top 3 mm - built and measured, the export came back as 7 separate bodies - and the head's
// bottom face would be 133 mm wide against a 139 mm bay opening, bearing on the front and back rim only.
// It is down at 0.5 for a second reason: at 2 the elevation arc met the 3.5 mm arc of the vertical edge in
// the same corner, and the two different radii plus the chamfers around the joint made a visible jumble
// there (user, 2026-09-23: "diese rundungen hinten sehen einfach beschissen aus"). At 0.5 the joint is a
// straight parting line that runs into the rounded vertical edge, and that edge carries the corner.
module head_outline(inset = 0)
    let (w = body_w - 2 * inset, h = head_h - 2 * inset,
         rt = max(corner_r - inset, 0.5), rb = max(corner_rb - inset, 0.5))
    translate([body_w / 2, head_cz]) union() {
        intersection() { rrect([w, h], rt); translate([0,  h / 4]) square([w, h / 2], center = true); }
        intersection() { rrect([w, h], rb); translate([0, -h / 4]) square([w, h / 2], center = true); }
    }
// The base rim follows the head's bottom corners down: corner_rb narrower at the joint plane, back to the
// full width over corner_rb below it. A mirrored copy of the arc would meet the side wall tangentially and
// leave a zero-volume sliver in the export, so the run-out is a straight 45 degrees.
module joint_neck() head_at() along_y(-1, body_d + 1) difference() {
    translate([body_w / 2, base_h - neck_r + 0.5]) square([body_w + 40, 2 * neck_r + 1], center = true);
    translate([body_w / 2, base_h - neck_r - 5])
        rrect([body_w - 2 * corner_rb + 2 * neck_r, 2 * neck_r + 10], neck_r);
    // The cutter's top corners are an arc of neck_r whose centres sit corner_rb in from the housing edge and
    // neck_r below the joint plane. So at the joint plane the base is exactly as wide as the head and both
    // arcs are tangent to the horizontal there: the rounding carries on through the edge instead of breaking
    // into a straight chamfer (user, 2026-09-23). Built from the numbers rather than by mirroring
    // head_outline(), because widening that contour moves its bottom edge down with it and the arc lands
    // half a millimetre off.
    // neck_r is half a millimetre more than corner_rb so the arc crosses the outer face of the side wall
    // instead of touching it: tangent there, Manifold exports a zero-volume four-triangle shell. For the same
    // reason the slab reaches 1 mm above the joint plane, clear of the face joint_halfspace() leaves.
}
module head_centre_sq(size, r) translate([body_w / 2, head_cz]) rrect([size, size], r);

// Square grid of rounded cells, centred on the origin and trimmed to a square area
module grid_2d(area, bar = grid_bar, gap = grid_gap) let (n = max(1, floor((area + bar) / (gap + bar))),
                                                         span = n * gap + (n - 1) * bar)
    intersection() {
        for (i = [0:n - 1], j = [0:n - 1])
            translate([-span / 2 + gap / 2 + i * (gap + bar), -span / 2 + gap / 2 + j * (gap + bar)]) rrect([gap, gap], grid_r);
        square([area, area], center = true);
    }

// Point paths matching the native offset(r) outline sampling. Keeping the
// finished contour as data lets BOSL2 generate exact-height 45-degree chamfers.
function head_profile_points(inset = 0) = let (
    w = body_w - 2 * inset, h = head_h - 2 * inset,
    rt = max(corner_r - inset, 0.5), rb = max(corner_rb - inset, 0.5))
    [for (c = [0:3]) let (
        r = c == 0 || c == 3 ? rb : rt,
        nf = max(5, ceil(min(360 / $fa, 2 * PI * r / $fs))),
        da = 360 / nf, n = ceil(90 / da),
        cx = c < 2 ? w / 2 - r : -w / 2 + r,
        cz = c == 0 || c == 3 ? -h / 2 + r : h / 2 - r)
        for (k = [0:n]) let (a = -90 + c * 90 + min(k * da, 90))
        [body_w / 2 + cx + r * cos(a), head_cz + cz + r * sin(a)]];
function cassette_profile_points() = intersection(
    head_profile_points(cass_inset),
    move([body_w / 2, head_cz], p=rect([body_w - 2 * plan_r, head_h + 10])))[0];
function cover_profile_points() = intersection(
    head_profile_points(),
    move([body_w / 2, base_h + cover_gap + head_h / 2], p=rect([body_w + 2, head_h])))[0];
// A native-position profile in x/z, swept from y0 to y1. Chamfers are measured
// from the real end planes; no hull-tip thickness enters their dimensions.
module profile_sweep_y(path, y0, y1, front_c = 0, back_c = 0) {
    translate([0, y1, 0]) rotate([90, 0, 0])
        offset_sweep(path, height = y1 - y0, offset = "delta",
            bottom = os_chamfer(height = back_c, width = back_c),
            top = os_chamfer(height = front_c, width = front_c));
}
// Extend the tool beyond the quantized chamfer end. A one-grid outward offset
// and equal added chamfer width/height keep the 45-degree cut unchanged while
// avoiding a vanishing cut against the independently tessellated native outline.
module front_rim_chamfer(path, y, c) let(sweep_eps = 1 / 1024) difference() {
    translate([-1, y - eps, base_h - 1]) cube([body_w + 2, c + 2 * eps, head_h + 2]);
    profile_sweep_y(offset(path, delta = sweep_eps), y, y + c + 3 * eps, front_c = c + sweep_eps);
}
module back_rim_chamfer(path, y, c) let(sweep_eps = 1 / 1024) difference() {
    translate([-1, y - c - eps, base_h - 1]) cube([body_w + 2, c + 2 * eps, head_h + 2]);
    profile_sweep_y(offset(path, delta = sweep_eps), y - c - 3 * eps, y, back_c = c + sweep_eps);
}

// ---------- head: shell, filter chamber, fan seat (untilted frame) ----------
// Local z follows the screw axis; t is the distance into the base from its insert entry.
module rim_at(p, t = 0) translate(rim_entry(p) + rim_axis(p) * t)
    rotate([180, 0, 0]) children();
module rim_front_boss(p) rim_at(p) cylinder(d = rim_boss_d, h = rim_boss_depth);
module rim_front_base_raw(p, clearance = 0) hull() {
    rim_at(p) cylinder(d = rim_boss_d+2*clearance, h = rim_boss_depth);
    translate([p[0]-rim_boss_d/2-clearance, -clearance, rim_front_root_z])
        cube([rim_boss_d+2*clearance, wall+2*clearance, base_h-rim_front_root_z]);
}
// A short solid bearing cap closes the tube floor around the raised insert boss.
// The head is recessed by the same 0.7 mm as at the rear, with its upper part exposed.
module rim_front_cap(p) let (e = rim_entry(p),
    h = e[2]+rim_bearing(p)+rim_recess-rim_front_cap_bottom)
    translate([e[0], e[1], rim_front_cap_bottom]) {
        cylinder(d = rim_front_cap_d, h = h-rim_front_cap_c+eps);
        translate([0, 0, h-rim_front_cap_c])
            cylinder(d1 = rim_front_cap_d, d2 = rim_front_cap_d-2*rim_front_cap_c,
                h = rim_front_cap_c);
    }
module rim_head_seats() for (p = rim_bosses()) if (rim_dir(p) > 0) rim_front_cap(p);
module rim_head_windows() for (p = rim_bosses()) if (rim_dir(p) > 0) {
    // The normal sweep clears the complete base root during straight head removal.
    hull() for (drop = [0, 15]) translate([0, 0, -drop])
        rim_front_base_raw(p, rim_fit_gap);
    // Open the shallow front skins left by the sloping root clearance.
    // At z=57.5 the retained front wall is already 1.25 mm thick; the cap stays intact.
    translate([p[0]-rim_boss_d/2-rim_fit_gap, -eps, base_h-1])
        cube([rim_boss_d+2*rim_fit_gap, front_t+2*eps, 57.5-base_h+1]);
}
module rim_head_holes() for (p = rim_bosses()) {
    rim_at(p, -rim_bearing(p)-eps) cylinder(d = screw_clear_d, h = rim_bearing(p)+2*eps);
    rim_at(p, -rim_bearing(p)-30)
        cylinder(d = head_pocket[0], h = 30);
}
module head_raw() difference() {
    intersection() { plan_prism(); head_body(); }
    top_corner_blends();
    battery_tie_head_relief();
}
module head_body() difference() {
    union() {
        difference() {
            along_y(0, head_y[4]) head_outline();                       // outer shell
            along_y(front_t, head_y[4] + eps) head_outline(wall);       // one cavity behind the intake face
        }
        along_y(front_t - 0.5, head_y[2]) difference() {                // filter chamber tube, overlapping the intake face
            head_centre_sq(tube_sq, open_r + tube_w);
            head_centre_sq(chamber_sq, open_r);
        }
        mat_stop();
        for (p = head_bosses()) cyl_y(p, head_y[2], head_y[4], boss_d / 2);
        fan_guides();
        rim_head_seats();
    }
    difference() { // Preserve the complete shallow pocket rims beside the intake opening.
        along_y(-eps, front_t + eps) head_centre_sq(open_sq, open_r);
        rim_head_seats();
    }
    filter_support_pockets();
    for (p = head_bosses()) cyl_y(p, head_y[4] - insert_depth, head_y[4] + eps, insert_hole_d / 2);
    for (p = mag_xz()) cyl_y(p, mag_skin, mag_skin + mag[1], mag[0] / 2);
    for (sx = [-1, 1]) cyl_y([body_w / 2 + sx * body_w / 2, head_cz], -eps, scoop[1],
                             scoop[0] / 2 + eps, scoop[0] / 2 - scoop[1]);   // finger scoops at the side edges
    rim_head_windows();
    rim_head_holes();
    // Lay the cable into the rear-open slot before sliding in the fan/cover assembly.
    // Skip the adjacent vent to retain a full 5.5 mm web, not a thin slit remnant.
    translate([fan_cable_slot[0], fan_cable_slot[2], base_h - 1])
        cube([fan_cable_slot[1] - fan_cable_slot[0], head_y[4] - fan_cable_slot[2] + eps, wall + 2]);
    for (i = [1:chg_vent[2] - 1])
        translate([chg_cx - ((chg_vent[2] - 1) * chg_vent[1] + chg_vent[0]) / 2 + i * chg_vent[1],
                   chg_vent_y, base_h - 1])
            cube([chg_vent[0], chg_vent[3], wall + 2]);
    front_rim_chamfer(head_profile_points(), 0, edge_c);
}
// Rear lip of the filter chamber, the counterpart of the intake lip. Without it the mat is held at the
// front by that lip and at the back by nothing but the four gusset corners - 7.8 % of its rear face - with
// 10.5 mm of clear air to the fan frame and about 1 N of suction pushing it exactly that way at full speed
// (user asked what stops the mat falling into the fan, 2026-09-23). Same 2.25 mm all round as the front.
// Printed intake-face-down this lip hangs inwards, so its flank rises 1.5 mm per mm instead of 1: at 45
// degrees `analyze.py overhangs` counts it. It merges into the chamber tube, so it starts out of the bore
// wall rather than as a knife edge.
function mat_stop_y() = [head_y[1], head_y[1] + (chamber_sq - open_sq) / 2 * mat_stop_rise];
module mat_stop() let (y0 = mat_stop_y()[0], y1 = mat_stop_y()[1])
    translate([body_w / 2, 0, head_cz]) difference() {
        along_y(y0, head_y[2]) rrect([tube_sq, tube_sq], open_r + tube_w);
        union() {
            hull() { along_y(y0 - eps, y0 + tip) rrect([chamber_sq, chamber_sq], open_r);
                     along_y(y1 - tip, y1 + eps) rrect([open_sq, open_sq], open_r); }
            along_y(y1, head_y[2] + eps) rrect([open_sq, open_sq], open_r);
        }
    }

// A removable cross supports the fleece centre without bridging the chamber during the head print.
// The widened ends sit in rear-open pockets. Their posts stop against the fan's outer frame; the
// middle stays 5 mm in front of the fan front plane. R4 concave corners strengthen the centre;
// a tangent 6-mm flare blends each arm into its wider end pad. Both faces have 0.4-mm chamfers.
function filter_support_arm() = let (
    w = mat_support[0], span = mat_support[2], pad = mat_support[5], flare = 6,
    edge = [for (i = [0:16]) let (q = i / 16)
        [span / 2 - 3 - flare + flare * q, w / 2 + (pad - w) / 2 * q * q * (3 - 2 * q)]])
    concat([[0, -w / 2]], [for (p = edge) [p.x, -p.y]],
           [[span / 2, -pad / 2], [span / 2, pad / 2]], reverse(edge), [[0, w / 2]]);
function filter_support_profile() = let (
    w = mat_support[0],
    outline = union([for (a = [0:90:270]) rot(a, p = filter_support_arm())])[0],
    radii = [for (p = outline) abs(abs(p.x) - w / 2) < eps && abs(abs(p.y) - w / 2) < eps ? 4 : 0])
    move([body_w / 2, head_cz], p = round_corners(outline, radius = radii));
module filter_support_raw() {
    profile_sweep_y(filter_support_profile(), mat_support[3], mat_support[3] + mat_support[1],
                    front_c = 0.4, back_c = 0.4);
    for (a = [0:90:270]) translate([body_w / 2, 0, head_cz]) rotate([0, a, 0])
        translate([mat_support[6], mat_support[3] + mat_support[1] - 0.6, -mat_support[5] / 2])
            cube([mat_support[2] / 2 - mat_support[6],
                  mat_support[4] - mat_support[3] - mat_support[1] + 0.6, mat_support[5]]);
}
module filter_support_pockets() let (c = mat_support[7])
    for (a = [0:90:270]) translate([body_w / 2, 0, head_cz]) rotate([0, a, 0])
        translate([mat_support[2] / 2 - 3 - c, mat_support[3] - c, -mat_support[5] / 2 - c])
            cube([3 + 2 * c, head_y[2] - mat_support[3] + c + eps, mat_support[5] + 2 * c]);
module filter_support() head_at() filter_support_raw();
module filter_support_print() translate([-body_w / 2, head_cz, -mat_support[3]])
    rotate([90, 0, 0]) filter_support_raw();
// The fan bears on the end face of the filter tube: the rear lip closes the bore to open_sq, so the tube
// ends as a ring the fan frame sits on. Four 45 degree corner gussets used to carry the fan's inserts
// instead, and they had to - the fan's mounting holes are 52.5 mm from the axis, inside the 60.75 mm bore,
// so any boss for them stands in the filter chamber, and printed intake-face-down it has to grow from the
// intake face at 45 degrees: 38.9 mm legs over 27.5 mm of depth, pressing 6.6 cm3 out of the mat. The user
// asked whether the fan can be screwed to the back cover instead (2026-09-23) - it can, and the same
// M3 x 30 do it: fan and cover are screwed together on the bench, where the fan's front face is reachable,
// and the pair goes into the head as one.
// One-sided cool-end holder, based on LEO-AC1. The hot IN end and heatsink stand free.
// The cable tie retains the board; the lower seat, central end stop and rear bearing locate it.
function chg_tie_y() = chg_y0 + chg_pcb[2] + chg_web_gap + chg_tie[4] + chg_tie[2];
module chg_brackets() let (
    z0 = ball[3] + ball_lid_t,
    za = chg_z0 + (chg_pcb[1] - chg_web_w) / 2, zb = za + chg_web_w,
    yb = chg_y0 + chg_pcb[2], yw = yb + chg_web_gap,
    yr = chg_tie_y() + chg_tie[1] + chg_tie[2] + chg_web_back,
    tx = chg_x0 + chg_tie[3], tc = chg_tie[0] / 2 + chg_tie[2],
    tz = chg_z0 - chg_tie[1] - chg_tie[2]) difference() {
    union() {
        // Rear pedestal stays 1.5 mm off the jumpers and ends before the thermal metal pad.
        translate([chg_x0 - 2, yw, z0 - eps])
            cube([chg_web_touch[1] + 2, yr - yw, zb - z0 + eps]);
        // PCB lower cut edge, beyond the OUT wire pads. No support below the hot half.
        translate([chg_x0 + 3, chg_y0 - 0.4, z0 - eps])
            cube([8, chg_pcb[2] + 0.8, chg_z0 - z0 + eps]);
        // A steep underside grows the central bearing into the PCB back without a shelf.
        // Recess the hidden top seam by eps instead of joining coplanar cap faces.
        along_x(chg_x0 + chg_web_touch[0], chg_x0 + chg_web_touch[1])
            polygon([[yw + eps, za - 1.25 * chg_web_gap], [yb, za], [yb, zb], [yw + eps, zb - eps]]);
        // Central OUT-end stop leaves the two corner wire pads open. Its underside is a ramp.
        along_x(chg_x0 - 2, chg_x0)
            polygon([[yw + eps, za - 1.25 * (yw - chg_y0)], [chg_y0, za],
                     [chg_y0, zb], [yw + eps, zb - eps]]);
    }
    // Rotate the LEO web tunnel with the horizontal PCB. Its lower opening joins a
    // passage under the board; the pedestal bridges only the 3.1 mm tunnel width.
    translate([tx - tc, chg_tie_y() - chg_tie[2], tz])
        cube([2 * tc, chg_tie[1] + 2 * chg_tie[2], zb - tz + 1]);
    translate([tx - tc, chg_y0 - chg_comp_h - chg_tie[1] - 1, tz])
        cube([2 * tc, yr - (chg_y0 - chg_comp_h - chg_tie[1]) + 2,
              chg_tie[1] + 2 * chg_tie[2]]);
}
// Bought cable tie: the closed band follows the measured LEO contact position.
// Its buckle and elastic tightening are not represented by this collision envelope.
module chg_tie_env() let (
    t = chg_tie[1], yf = chg_y0 - chg_comp_h, yr = chg_tie_y())
    along_x(chg_x0 + chg_tie[3] - chg_tie[0] / 2, chg_x0 + chg_tie[3] + chg_tie[0] / 2)
        difference() {
            bounds_rect([yf - t, chg_z0 - t], [yr + t, chg_z0 + chg_pcb[1] + t]);
            bounds_rect([yf, chg_z0], [yr, chg_z0 + chg_pcb[1]]);
        }
// ventilation slots in the back wall, above the ballast lid: the outlet of the draught through the bay
module vent_slots() for (i = [0:vent[2] - 1])
    translate([vent_xz[0] + i * vent[1], body_d - wall - 1, vent_xz[1] + i * vent[4]])
        cube([vent[0], wall + 2, vent[3]]);
module fan_guides() for (sx = [-1, 1], sz = [-1, 1]) translate([body_w / 2, 0, head_cz]) scale([sx, 1, sz])
    let (i = fan_size / 2 + fan_cl, y0 = head_y[2] - 0.5, depth = head_y[3] - y0) {
        // The fan enters from +Y with the back cover. Only the inward-facing rear edges
        // are bevelled; the straight locating faces and front seat retain their clearance.
        translate([i, y0, i - guide[1]])
            cuboid([guide[0], depth, guide[1] + guide[0]], anchor=FRONT+LEFT+BOTTOM,
                   chamfer=guide_c, edges=[BACK+LEFT]);
        translate([i - guide[1], y0, i])
            cuboid([guide[1] + guide[0], depth, guide[0]], anchor=FRONT+LEFT+BOTTOM,
                   chamfer=guide_c, edges=[BACK+BOTTOM]);
    }
module head() head_at() head_raw();
module head_print_pose() translate([0, base_h + head_h, 0]) rotate([90, 0, 0]) children();   // intake face on the bed

// ---------- head back cover (untilted frame) ----------
module grid_2d_at() translate([body_w / 2, head_cz]) grid_2d(exhaust_sq);
module head_back_raw() difference() {
    head_back_body();
    top_corner_blends();
}
module head_back_body() intersection() {
    plan_prism();
    translate([-1, head_y[3] - 1, base_h + cover_gap])            // reaches forward for the fan posts
        cube([body_w + 2, body_d - head_y[3] + 2, head_h]);
    difference() {
    union() {
        along_y(head_y[4], body_d) head_outline();
        along_y(head_y[4] - lip_h, head_y[4] + eps) difference() {
            head_outline(wall + lip_cl);
            head_outline(wall + lip_cl + lip_t);
            for (p = head_bosses()) offset(r = 0.8) translate([p[0], p[1]]) circle(d = boss_d);
            // Clear the rear button heads while retaining the rest of the locating lip.
            for (p = rim_bosses()) if (rim_dir(p) < 0)
                translate([p[0], base_h + wall]) circle(r = head_pocket[0]/2 + 0.8);
        }
        fan_posts();
    }
    along_y(head_y[4] - 1, body_d + 1) difference() {                   // exhaust grid, pad under each post
        grid_2d_at();
        for (p = fan_holes()) translate([p[0], p[1]]) circle(d = fan_post_d + 6);
    }
    for (p = head_bosses()) {
        cyl_y(p, head_y[4] - 1, body_d + 1, screw_clear_d / 2);
        cyl_y(p, body_d - head_pocket[1], body_d + 1, head_pocket[0] / 2);
    }
    back_rim_chamfer(cover_profile_points(), body_d, edge_c);
    }
}
module head_back() head_at() head_back_raw();
// Spacer posts carrying the fan: they bridge the plenum to the fan's back face and hold its inserts. The
// cover prints outer-face-down, so they grow straight up and their insert pockets open at the top.
module fan_posts() for (p = fan_holes()) difference() {
    cyl_y(p, head_y[3], head_y[4] + eps, fan_post_d / 2);
    cyl_y(p, head_y[3] - eps, head_y[3] + insert_depth, insert_hole_d / 2);
}
module head_back_print_pose() translate([0, -base_h, body_d]) rotate([-90, 0, 0]) children();   // outer face on the bed

// ---------- filter cassette (untilted frame, in front of the intake face) ----------
// The cassette lies on the intake face and touches no rim, so like the back cover it keeps the radius
// on all four corners rather than the shell's square bottom (user, 2026-09-23).
// Its finished outline, not the one it starts from: the head outline first, then the width the shared
// footprint leaves in front of the intake face. The bevel below is taken from THIS contour. Built the
// other way round - bevel first, prism afterwards - the prism cut the bevel off the two long sides
// entirely and left a square 4.5 mm wall there (audit 2026-09-23, G1).
module cass_face(inset = 0) offset(delta = -inset) intersection() {
    head_outline(cass_inset);
    translate([body_w / 2, head_cz]) square([body_w - 2 * plan_r, head_h + 10], center = true);
}
module cassette_raw() difference() {
    profile_sweep_y(cassette_profile_points(), -cass_t, 0, front_c = cass_c);
    translate([body_w / 2, 0, head_cz]) along_y(-cass_t - 1, 1) grid_2d(open_sq);
    for (p = mag_xz()) cyl_y(p, -cass_t + mag_skin, -mag_skin, mag[0] / 2);

}
module cassette() head_at() cassette_raw();
module cassette_print_pose() translate([0, base_h + head_h, cass_t]) rotate([90, 0, 0]) children();   // grid face on the bed

// The upper base follows the head's exact projected footprint over a smooth transition.
function joint_smooth(q) = q * q * (3 - 2 * q);
// The same quarter-circle sampling used by offset(r) in base_outline().
function joint_plan_points(inset, sampling_inset = undef) = let (
    w = body_w - 2 * inset, h = body_d - 2 * inset,
    r = max(plan_r - inset, 0.5),
    sample_r = max(plan_r - (is_undef(sampling_inset) ? inset : sampling_inset), 0.5),
    nf = max(5, ceil(min(360 / $fa, 2 * PI * sample_r / $fs))),
    da = 360 / nf, n = ceil(90 / da))
    [for (c = [0:3], k = [0:n]) let (
        a = -90 + c * 90 + min(k * da, 90),
        cx = c < 2 ? w / 2 - r : -w / 2 + r,
        cy = c == 0 || c == 3 ? -h / 2 + r : h / 2 - r)
        [body_w / 2 + cx + r * cos(a), body_d / 2 + cy + r * sin(a)]];
function joint_profile_points(inset, d) = let (
    q = min(1, max(0, 1 - (d - inset * sin(tilt)) / base_joint_h)), s = joint_smooth(q),
    i = inset > 0 ? inset + base_joint_wall_extra * pow(sin(180 * q), 2) : 0,
    delta = body_d / 2 * (1 - cos(tilt)) * s,
    sy = (body_d - 2 * i - 2 * delta) / (body_d - 2 * i) / cos(tilt))
    // Keep the vertex count fixed while the inner contour thickens through the loft.
    [for (p = joint_plan_points(i, inset))
        [p[0], joint_y + (p[1] - joint_y) * (1 - 2 * delta / (body_d - 2 * i)),
         base_h + (p[1] - joint_y) * sy * sin(tilt) - d / cos(tilt)]];
module base_joint_loft(inset) let (
    ds = concat([base_h + body_d], [for (k = [base_joint_steps:-1:0]) (base_joint_h + inset * sin(tilt)) * k / base_joint_steps], [-0.1]),
    n = len(joint_plan_points(inset)), nr = len(ds),
    pts = [for (d = ds) each joint_profile_points(inset, d)])
    polyhedron(points = pts, faces = [for (f = concat(
        [for (j = [1:n-2]) [0, j+1, j]],
        [for (i = [0:nr-2], j = [0:n-1]) each
            [[i*n+j, i*n+(j+1)%n, (i+1)*n+(j+1)%n], [i*n+j, (i+1)*n+(j+1)%n, (i+1)*n+j]]],
        [for (j = [1:n-2]) [(nr-1)*n, (nr-1)*n+j, (nr-1)*n+j+1]])) [for (j = [len(f)-1:-1:0]) f[j]]]);
module base_joint_envelope(inset = 0) intersection() {
    base_joint_loft(inset);
    translate([-1, -1, 0]) cube([body_w + 2, body_d + 2, 200]);
}

// ---------- base ----------
module base() difference() {
    union() {
      difference() {
       union() {
        difference() {
            base_joint_envelope();
            intersection() {
                base_joint_envelope(wall);
                translate([-1, -1, floor_t]) cube([body_w + 2, body_d + 2, 200]);
            }
        }
        battery_cradle();
        battery_end_stop();
        battery_tie_anchors();
        pwm_ribs();
        pwm_bosses();
        led_boss_body();
        usbc_channel();
        foot_bosses();
        sw_wall_box();
        ballast_walls();
    }
       joint_halfspace();
       joint_neck();
      }
      // Add complete insert faces after the joint cuts; their wall roots are clipped separately.
      rim_boss_bodies();
    }
    // That plane rises 15 degrees towards the back, so it meets the vertical back face at 75 degrees and
    // leaves an acute edge across the full width - the sharp edge under the back cover (user, 2026-09-23).
    // Cut at 45 degrees to the joint plane, so it mirrors the chamfer on the cover's lower edge and the two
    // read as one groove. It stays behind head_y[4], where the rim carries no head wall anyway.
    head_at() along_x(-1, body_w + 1)
        polygon([[body_d - edge_c, base_h], [body_d + 3, base_h - edge_c - 3], [body_d + 3, base_h + 3]]);
    pot_cuts();
    battery_tie_tunnels();
    pwm_pilots();
    // The inward-curving upper rim needs shallow relief for the slim driver shafts.
    for (p = pwm_holes()) translate([p[0], p[1], pwm_z0 + pwm_pcb[2] + pwm_screw[3]])
        cylinder(d = 4.6, h = base_h);
    led_cut();
    usbc_cuts();
    sw_cuts();
    vent_slots();
    ballast_screw_holes();
    for (p = rim_bosses()) head_at() rim_at(p, -eps)
        cylinder(d = insert_hole_d, h = insert_depth + eps);
    for (p = foot_xy) translate([p[0], p[1], -1]) cylinder(d = insert_hole_d, h = insert_depth + 1);
    for (p = foot_xy) translate([p[0] + foot_peg[2], p[1], -eps])
        cylinder(d = foot_peg[0] + foot_peg_cl, h = foot_peg[1] + eps);   // anti-rotation peg holes
    difference() {                                                      // exact bottom-bed chamfer
        translate([-1, -1, -eps]) cube([body_w + 2, body_d + 2, edge_c + 2 * eps]);
        offset_sweep(joint_plan_points(0), height = edge_c + 3 * eps, offset = "delta",
            bottom = os_chamfer(height = edge_c, width = edge_c));
    }
}

// three open saddles up to the axis; the protection board faces up, foam tape keeps the cell quiet
module battery_cradle() for (cx = cradle_x) translate([cx - cradle_t / 2, 0, 0]) along_x(0, cradle_t) difference() {
    bounds_rect([bat_cy - bat_d / 2 - cradle_out, floor_t - eps], [bat_cy + bat_d / 2 + cradle_out, bat_cz]);
    translate([bat_cy, bat_cz]) circle(d = bat_d + 2 * bat_clear);
}
// The cable ties follow the shrink-wrapped pack directly, including its side BMS.
// This envelope checks fit; it does not establish a pressure-free path over the electronics.
module battery_tie_outline() hull() {
    translate([bat_cy, bat_cz]) circle(r = bat_d/2 + 0.05);
    translate([bat_cy-bat_bms[0]/2, bat_cz+bat_d/4])
        offset(delta = 0.05) square([bat_bms[0], bat_d/4+bat_bms[1]]);
    translate([bat_cy - bat_tie_span/2, bat_tie_floor + bat_tie_slot[1]])
        square([bat_tie_span, bat_tie_roof]);
}
module battery_ties_env() for (x = bat_tie_x) union() {
    along_x(x - bat_tie[0]/2, x + bat_tie[0]/2) difference() {
        offset(delta = bat_tie[1]) battery_tie_outline();
        battery_tie_outline();
    }
    // Conservative bought buckle envelope; thread the tail before loading the cell.
    translate([x - 3, bat_cy - bat_d/2 - 4.75, bat_cz - 2.5]) cube([6, 4, 5]);
}
module battery_tie_head_relief() for (x = bat_tie_x)
    translate([x-bat_tie_head_clearance[0]/2, bat_tie_head_clearance[1], base_h-eps])
        cube([bat_tie_head_clearance[0], bat_tie_head_clearance[2], bat_tie_head_clearance[3]+eps]);

// Recess the tunnel into the floor so its 1.6 mm roof clears the unraised cell.
// Two shallow ramps expose the tunnel mouths for threading before fitting the battery.
module battery_tie_anchors() let (
    w = bat_tie_slot[0] + 2 * bat_tie_wall,
    top = bat_tie_floor + bat_tie_slot[1] + bat_tie_roof)
    for (x = bat_tie_x) translate([x, bat_cy, floor_t - eps])
        offset_sweep(round_corners([[-w/2, -bat_tie_span/2], [w/2, -bat_tie_span/2],
                                   [w/2, bat_tie_span/2], [-w/2, bat_tie_span/2]], radius = 0.6),
                     height = top - floor_t + eps, offset = "delta", top = os_chamfer(height = 0.3));
module battery_tie_tunnels() let (
    a = bat_cy - bat_tie_span/2, b = bat_cy + bat_tie_span/2,
    z = bat_tie_floor, top = z + bat_tie_slot[1])
    for (x = bat_tie_x) along_x(x - bat_tie_slot[0]/2, x + bat_tie_slot[0]/2)
        polygon([[a - 4, floor_t + eps], [a, z], [b, z], [b + 4, floor_t + eps],
                 [b + 4, top], [a - 4, top]]);
// two ribs under the pin-free long edges, pads on top, solder pins hanging free between them
module pwm_ribs() for (sx = [-1, 1]) let (edge = pot_x + sx * pwm_pcb[1] / 2,        // long edge of the board
                                          inner = edge - sx * pwm_edge_free,        // where the solder pins start
                                          r0 = min(inner, inner + sx * pwm_rib), p0 = min(edge - sx * 0.3, inner + sx * 0.3)) {
    translate([r0, pwm_y0, floor_t - eps]) cube([pwm_rib, pwm_pcb[0] - 2, pwm_z0 - pwm_pad - floor_t + eps]);
    translate([p0, pwm_y0, pwm_z0 - pwm_pad - eps]) cube([pwm_edge_free - 0.6, pwm_pcb[0] - 2, pwm_pad + eps]);
}
function pwm_holes() = [for (x = [pwm_x[0] + pwm_hole_edge, pwm_x[1] - pwm_hole_edge])
    [x, pwm_y0 + pwm_hole_edge]];
module pwm_bosses() for (p = pwm_holes()) translate([p[0], p[1], floor_t - eps])
    cylinder(d = pwm_boss_d, h = pwm_z0 - floor_t + eps);
module pwm_pilots() for (p = pwm_holes()) {
    translate([p[0], p[1], pwm_z0 - pwm_core_depth]) cylinder(d = pwm_core_d, h = pwm_core_depth + eps);
    translate([p[0], p[1], pwm_z0 - pwm_core_entry[1]])
        cylinder(d1 = pwm_core_d, d2 = pwm_core_entry[0], h = pwm_core_entry[1] + eps);
}
module pot_cuts() {
    // The PCB is screwed to the floor; this covered slot lets it lift before tipping out.
    hull() for (z = [pot_z, pot_z + pwm_install_lift])
        cyl_y([pot_x, z], -1, pot_mount_t, (pot_bush[0] + pot_bush_cl) / 2);
    // Stop below the curved upper rim and run fully into the bay: a short cutter
    // ending at nominal wall would leave a thin isolated skin behind the loft.
    intersection() {
        hull() for (z = [pot_z, pot_z + pwm_install_lift])
            cyl_y([pot_x, z], pot_mount_t, wall + 3, pot_recess_r);
        translate([pot_x - pot_recess_r - 1, -1, 0])
            cube([2 * pot_recess_r + 2, wall + 5, pot_z + pot_housing / 2 + pwm_install_lift + 1]);
    }
    translate([pot_x - (pot_tab[0] + 2 * pot_tab_cl) / 2, -1, pot_z - pot_tab_z()[1]])
        cube([pot_tab[0] + 2 * pot_tab_cl, pot_mount_t + 1, pot_tab_z()[1] - pot_tab_z()[0] + pwm_install_lift]);
    if (pwm_pcb_slot > 0.01) difference() {
        translate([pwm_x[0] - pot_pcb_cl, wall - pwm_pcb_slot, pwm_z0 - pot_pcb_cl])
            cube([pwm_pcb[1] + 2 * pot_pcb_cl, pwm_pcb_slot + eps, pwm_pcb[2] + 2 * pot_pcb_cl + pwm_install_lift]);
        pwm_bosses(); // preserve each complete bearing face below the PCB
    }
}
module led_boss_body() for (p = led_xz) cyl_y(p, wall - eps, led_boss[1], led_boss[0] / 2);
module led_cut() for (p = led_xz) {
    cyl_y(p, led_skin, led_boss[1] + 1, (led_d + led_cl) / 2); // blind pockets, open only to the bay
}
// Two narrow wall gussets leave both sides of the central keeper open for wires.
function usbc_support_x() = [
    [usbc_xz[0] - usbc[1] / 2 - usbc_cl - usbc_wall, usbc_xz[0] - usbc[1] / 2 - usbc_cl],
    [usbc_xz[0] + usbc[1] / 2 + usbc_cl, usbc_xz[0] + usbc[1] / 2 + usbc_cl + usbc_wall]];
// A 45-degree underside grows from the rear wall entirely above the lid.
module usbc_gusset(x0, x1, top) let (
    yi = usbc_y0 - usbc_guide_lead, yb = body_d - wall + eps,
    zr = ball[3] + ball_lid_t + usbc_gusset_lid_gap)
    along_x(x0, x1) polygon([[yi, zr + body_d - wall - yi], [yb, zr - eps],
                            [yb, top], [yi, top]]);
// Between the two gussets the rear PCB seat bridges 10.75 mm.
// The plug-force stop is on the removable lid, leaving this channel open forwards.
module usbc_channel() let (
    legs = usbc_support_x(), yb = body_d - wall,
    zseat = usbc_xz[1] - usbc[2] / 2,
    zb = zseat - usbc_cl - usbc_wall, zt = usbc_xz[1] + usbc[2] / 2 + usbc_cl,
    xr = usbc_xz[0] + usbc[1] / 2 + usbc_cl) {
    for (xs = legs) usbc_gusset(xs[0], xs[1], zt);
    // The board rests on this rear seat; the inner end remains open for its wires.
    translate([legs[0][1] - eps, yb - usbc_floor, zb])
        cube([xr - legs[0][1] + 2 * eps, usbc_floor + eps, zseat - zb]);
}
module usbc_cuts() {
    translate([usbc_xz[0] - usbc[1] / 2 - usbc_cl, body_d - wall - 1, usbc_xz[1] - usbc[2] / 2 - usbc_cl])
        cube([usbc[1] + 2 * usbc_cl, wall - usbc_plate + 1, usbc[2] + 2 * usbc_cl]);  // recess from inside, plate left outside
    usbc_stadium(body_d - usbc_plate - 1, body_d + 1, usbc_cl);
}
module usbc_stadium(y0, y1, grow) along_y(y0, y1) translate([usbc_xz[0], usbc_xz[1] - usbc[2] / 2 + usbc_shell_bottom + usbc_shell[1] / 2]) hull()
    for (s = [-1, 1]) translate([s * (usbc_shell[0] - usbc_shell[1]) / 2, 0]) circle(d = usbc_shell[1] + 2 * grow);
// rectangle around the switch frame at the well floor, growing 45 degrees towards the outer face
// 1.25 mm per mm: the flanks stay just off 45 degrees, which analyze.py overhangs counts as an overhang
module sw_funnel(x0, x1, grow) hull() for (x = [x0, x1]) let (g = grow + sw_well[1] + 1.25 * (x - (body_w - sw_well[0])))
    translate([x, sw_yz[0] - sw_bezel[0] / 2 - g, sw_yz[1] - sw_bezel[1] / 2 - g]) cube([eps, sw_bezel[0] + 2 * g, sw_bezel[1] + 2 * g]);
module sw_wall_box() sw_funnel(body_w - sw_well[0] - sw_panel, body_w - wall, sw_well[2]);
module sw_cuts() {
    sw_funnel(body_w - sw_well[0], body_w + 1, 0);
    let (h = sw_cut + [1, 1] * 2 * sw_cut_cl)
        translate([body_w - sw_well[0] - sw_panel - 1, sw_yz[0] - h[0] / 2, sw_yz[1] - h[1] / 2]) cube([sw_panel + 2, h[0], h[1]]);
}
// Front wall follows the switch well with room for its body, terminals and lid removal.
module ball_switch_front(extra = 0) intersection() {
    // The extended diagonal must join the rear wall without growing outside it.
    translate([-1, -1]) square([body_w + 2, body_d - wall + 2]);
    polygon([
    [ball_step[0] - ball_wall, ball_step[1] + extra],
    [ball_switch_corner[0], ball_step[1] + extra],
    [ball_switch_corner[1], ball_switch_corner[2] + extra],
    [ball_switch_corner[1], ball_switch_corner[2] + ball_wall + extra],
    [ball_switch_corner[0], ball_step[1] + ball_wall + extra],
    [ball_step[0] - ball_wall, ball_step[1] + ball_wall + extra]]);
}
module ballast_walls() {
    translate([ball[0], ball[2], floor_t - eps]) cube([ball_step[0] - ball[0], ball_wall, ball[3] - ball_rim - floor_t + eps]);
    translate([0, 0, floor_t - eps]) linear_extrude(ball[3] - ball_rim - floor_t + eps)
        ball_switch_front();
    translate([ball_step[0] - ball_wall, ball[2], floor_t - eps])
        cube([ball_wall, ball_step[1] - ball[2] + ball_wall, ball[3] - ball_rim - floor_t + eps]);
    for (i = [0:len(ball_posts()) - 1]) let (q = ball_posts()[i])
        translate([q[0], q[1], floor_t - eps]) difference() {
            cylinder(d = ball_post, h = ball[3] - floor_t + eps);
            if (i == 1) translate([-ball_post, -ball_post, -eps])
                cube([2 * ball_post, ball_post - ball_post_front_flat, ball[3] - floor_t + 3 * eps]);
        }
}
module ballast_screw_holes() for (q = ball_posts())
    translate([q[0], q[1], ball[3] - insert_depth]) cylinder(d = insert_hole_d, h = insert_depth + 1);
// Lid bears on two insert posts. Its switch notch stays ahead of the entire trough wall.
module ball_lid() difference() {
    union() { ball_lid_plate(); usbc_keeper(); chg_brackets(); }
    for (q = ball_posts()) translate([q[0], q[1], ball[3] - 1]) {
        cylinder(d = screw_clear_d, h = ball_lid_t + 2);
        translate([0, 0, 1 + ball_lid_t - lid_pocket]) cylinder(d = head_pocket[0], h = lid_pocket + 1);
    }
}
// Install the USB module first, then this centered lid-mounted keeper.
// The upper return captures its measured envelope; bare PCB thickness is unknown.
// Wire exits on both sides stay open; lifting and withdrawing the lid releases it.
module usbc_keeper() let (
    x0 = usbc_xz[0] - usbc_keeper_w / 2, yf = ball[2] + 0.2,
    yr = usbc_y0 - 2 - usbc_keeper_gap, yt = usbc_y0 - usbc_cl,
    zb = usbc_xz[1] - usbc[2] / 2 - usbc_cl - usbc_wall,
    zt = usbc_xz[1] + usbc[2] / 2 + usbc_cl,
    reach = usbc_y0 + usbc_keeper_top[0],
    root_z = zt - usbc_cl * usbc_keeper_top[2],
    tip_z = zt + usbc_keeper_top[0] * usbc_keeper_top[2]) {
    assert(usbc_keeper_w == usbc_stop_w, "USB keeper stem and returns must share one profile width");
    // The underside rises faster than 45 degrees and starts 0.2 mm above the
    // module's inner top edge. The short return resists cable-induced lifting.
    // One extrusion avoids coincident internal faces where the returns join.
    along_x(x0, x0 + usbc_keeper_w)
        polygon([[yf, ball[3]], [yr, ball[3]], [yr, zb - 0.1],
                 [yt, zb - 0.3 + yt - (yr - 0.2)], [yt, root_z],
                 [reach, tip_z], [reach, tip_z + usbc_keeper_top[1]],
                 [yr - 0.2, tip_z + usbc_keeper_top[1]], [yr - 0.2, zt], [yf, zt]]);
    // Low triangular cheeks spread plug loads into the lid, below both wire exits.
    // Each slopes down towards the rear and grows from the lid without supports.
    for (xs = [[x0-usbc_keeper_brace[2], x0+usbc_keeper_brace[3]],
               [x0+usbc_keeper_w-usbc_keeper_brace[3], x0+usbc_keeper_w+usbc_keeper_brace[2]]])
        along_x(xs[0], xs[1])
            polygon([[yf, ball[3]+ball_lid_t-eps],
                     [yf+usbc_keeper_brace[0], ball[3]+ball_lid_t-eps],
                     [yf, ball[3]+ball_lid_t+usbc_keeper_brace[1]]]);
}
// A rounded end wall grows from the base floor, independent of the removable lid.
// It bears on the cell body below the BMS and leaves the upper cable end open.
module battery_end_stop() let (
    x0 = bat_x0 + bat_l + bat_stop_gap, x1 = x0 + bat_stop_w,
    path = round_corners([[x0, bat_stop_y[0]], [x1, bat_stop_y[0]],
        [x1, bat_stop_y[1]], [x0, bat_stop_y[1]]], radius = 1),
    wall_top = ball[3] - ball_rim,
    slope_start = ball[2] - (bat_stop_top - wall_top)) {
    translate([0, 0, floor_t - eps]) offset_sweep(path,
        height = bat_stop_top - floor_t + eps, offset = "delta", top = os_chamfer(height = bat_stop_c));
    // Join the stop to the fixed trough wall below the removable lid. The full
    // floor root and 45-degree descending top need no bridge or print supports.
    assert(slope_start < bat_stop_y[1] - 1 && bat_stop_link_overlap < ball_wall,
        "Battery stop connection must overlap the rounded stop and trough wall");
    along_x(x0, x1) polygon([
        [slope_start, floor_t-eps], [ball[2]+bat_stop_link_overlap, floor_t-eps],
        [ball[2]+bat_stop_link_overlap, wall_top], [ball[2], wall_top],
        [slope_start, bat_stop_top]]);
}
module ball_lid_plate() difference() {
    // Narrow seams and a relieved rear corner keep the trough closed.
    translate([0, 0, ball[3]]) linear_extrude(ball_lid_t) union() {
        difference() {
            translate([ball[0] + 0.22, ball[2] - ball_lip])
                square([ball[1] - ball[0] - 0.42, body_d - wall - 0.2 - ball[2] + ball_lip]);
            translate([ball[0], body_d - wall]) polygon([[0, 0], [0.76, 0], [0, -0.76]]);
            translate([ball[1], body_d - wall]) polygon([[0, 0], [-0.76, 0], [0, -0.76]]);
            polygon([[ball_step[0], ball[2] - 1], [body_w + 1, ball[2] - 1],
                     [body_w + 1, body_d], [ball_switch_corner[1], ball_switch_corner[2] - 1],
                     [ball_switch_corner[0], ball_step[1] - 1], [ball_step[0], ball_step[1] - 1]]);
        }
        translate([ball_post_x[1], ball_post_y[1]]) circle(r=ball_lid_ear_r);
    }
    for (q = ball_posts()) translate([q[0], q[1], ball[3] - 1]) {
        cylinder(d = screw_clear_d, h = ball_lid_t + 2);
        translate([0, 0, 1 + ball_lid_t - lid_pocket]) cylinder(d = head_pocket[0], h = lid_pocket + 1);
    }
}
module ball_lid_print_pose() translate([-ball[0], -(ball[2] - ball_lip), -ball[3]]) children();
// Small crops of the actual parts, in their original print orientation. Check
// the real board in this pair before reprinting the complete electronics base.
module usbc_fit_base() translate([-97, -ball[2], 0]) union() {
    // Include the complete trough step instead of leaving a thin cropped wall.
    intersection() {
        base();
        translate([97, ball[2], 0]) cube([ball_step[0] - 97, body_d - ball[2], 65]);
    }
    // Fixture-only pads replace the distant screw-post seats omitted by the crop.
    // Two pads supplement the real right screw post retained by this crop.
    // The former middle pad is redundant and split its coplanar post-top face.
    for (p = [[98, ball[2]], [ball_step[0] - ball_wall, ball_step[1] - ball_wall]])
        translate([p[0], p[1], ball[3] - ball_rim - eps])
            cube([ball_wall, ball_wall, ball_rim + eps]);
}
module usbc_fit_lid() translate([-97, -ball[2], -ball[3]]) intersection() {
    ball_lid();
    translate([97, ball[2], ball[3]]) cube([ball_step[0] - 97, body_d - wall - ball[2], 25]);
}
// What the trough holds: its interior minus the housing itself, so the foot boss, the posts and the
// rounded inner corners are cut out of it and the reported mass is what really fits.
module ballast_env() difference() {
    translate([ball[0], ball[2] + ball_wall, floor_t])
        cube([ball[1] - ball[0], body_d - wall - ball[2] - ball_wall, ball[3] - floor_t]);
    translate([0, 0, floor_t - 1]) linear_extrude(ball[3] - floor_t + 2)
        polygon([[ball_step[0] - ball_wall, ball[2] - 1], [ball[1] + 1, ball[2] - 1],
                 [ball[1] + 1, ball_switch_corner[2] + ball_wall],
                 [ball_switch_corner[1], ball_switch_corner[2] + ball_wall],
                 [ball_switch_corner[0], ball_step[1] + ball_wall],
                 [ball_step[0] - ball_wall, ball_step[1] + ball_wall]]);
    base();
    ballast_screw_holes();   // installed inserts exclude these pockets from the loose-iron volume
    // the insert pockets of the rear feet are sealed voids under a 2 mm cap: no resin gets in there
    for (p = foot_xy) translate([p[0], p[1], -1]) cylinder(d = insert_hole_d + 0.4, h = insert_depth + 1);
}
// The raised front bosses and their short wall roots stay together above the joint.
// Clip only to the vertical exterior; clipping roots at the joint would disconnect them.
module rim_boss_bodies() for (p = rim_bosses()) if (rim_dir(p) > 0) {
    intersection() {
        head_at() rim_front_base_raw(p);
        translate([0, 0, -1]) linear_extrude(101) base_outline();
    }
} else difference() {
    intersection() {
        base_joint_envelope();
        head_at() let (dy = body_d - wall - p[1]) hull() {
            translate([p[0], p[1], base_h - rim_rear_boss_len])
                cylinder(d = rim_rear_boss_d, h = rim_rear_boss_len + 1);
            translate([p[0] - rim_rear_boss_d/2, body_d - wall, base_h - rim_rear_boss_len - dy])
                cube([rim_rear_boss_d, wall, rim_rear_boss_len + 1 + dy]);
        }
    }
    joint_halfspace();
}
module foot_bosses() for (p = foot_xy) translate([p[0], p[1], 0]) cylinder(d = foot_boss[0], h = foot_boss[1]);

// ---------- knob ----------
module knob_local() difference() {   // z = 0 at the underside (knob_gap off the wall), top face at knob_len
    union() {
        cylinder(d = knob_d, h = knob_len - knob_c);
        translate([0, 0, knob_len - knob_c - eps]) cylinder(d1 = knob_d, d2 = knob_d - 2 * knob_c, h = knob_c + eps);
    }
    for (i = [0:knob_flutes - 1]) rotate(i * 360 / knob_flutes)
        translate([knob_d / 2 - knob_flute[1], -knob_flute[0] / 2, 1]) cube([knob_flute[1] + 1, knob_flute[0], knob_len - knob_c - 1]);
    translate([0, 0, -eps]) cylinder(d = knob_cavity_d, h = knob_sleeve_z + eps);
    difference() {
        translate([0, 0, knob_sleeve_z - eps]) cylinder(d = knob_cavity_d, h = knob_slit[1] + eps);
        translate([0, 0, knob_sleeve_z - 2 * eps]) cylinder(d = knob_stem_d, h = knob_slit[1] + 3 * eps);
    }
    translate([0, 0, knob_sleeve_z - eps]) cylinder(d = pot_shaft_d + 2 * knob_bore_cl, h = knob_bore_top - knob_sleeve_z + eps);
    translate([-knob_slit[0] / 2, -knob_stem_d / 2 - 1, knob_sleeve_z - eps]) cube([knob_slit[0], knob_stem_d + 2, knob_slit[1] + eps]);
    translate([knob_d / 2 - knob_c - knob_mark[1], -knob_mark[0] / 2, knob_len - knob_mark[2]])   // pointer groove, open to the bed
        cube([knob_mark[1], knob_mark[0], knob_mark[2] + eps]);
}
module knob() translate([pot_x, -knob_gap, pot_z]) axis_orient([0, -1, 0]) knob_local();
module knob_print_pose() translate([0, 0, knob_len]) mirror([0, 0, 1]) children();   // top face on the bed

// ---------- feet ----------
module foot_local() difference() {
    union() {
        hull() {
            translate([-foot[0] / 2 + foot_c, -foot[1] / 2 + foot_c, -foot[2]]) cube([foot[0] - 2 * foot_c, foot[1] - 2 * foot_c, eps]);
            translate([-foot[0] / 2, -foot[1] / 2, -foot[2] + foot_c]) cube([foot[0], foot[1], foot[2] - foot_c]);
        }
        translate([foot_peg[2], 0, -eps]) cylinder(d = foot_peg[0], h = foot_peg[1] + eps);
    }
    translate([0, 0, -foot[2] - 1]) {
        cylinder(d = screw_clear_d, h = foot[2] + 2);
        cylinder(d = head_pocket[0], h = 1 + foot_head_recess + screw_head_h);
    }
}
module place_feet() for (p = foot_xy) translate([p[0], p[1], 0]) foot_local();
module foot_print_pose() translate([0, 0, foot[2]]) children();   // ground face on the bed

// ---------- bought parts as envelopes ----------
module fan_env() head_at() translate([body_w / 2 - fan_size / 2, head_y[2], head_cz - fan_size / 2]) cube([fan_size, fan_t, fan_size]);
module fan_visual() head_at() translate([body_w / 2, head_y[2], head_cz]) rotate([-90, 0, 0]) {
    difference() {
        translate([-fan_size / 2, -fan_size / 2, 0]) cube([fan_size, fan_size, fan_t]);
        translate([0, 0, -1]) cylinder(d = fan_blade_d + 2, h = fan_t + 2);
        for (sx = [-1, 1], sy = [-1, 1]) translate([sx * fan_pitch / 2, sy * fan_pitch / 2, -1]) cylinder(d = fan_hole_d, h = fan_t + 2);
    }
    let (hub = 20) {
        cylinder(r = hub, h = fan_t - 3);
        for (i = [0:6]) rotate(i * 360 / 7) translate([hub - 1, 0, 11]) rotate([40, 0, 0]) translate([0, -9, -0.75]) cube([fan_blade_d / 2 - hub - 1, 18, 1.5]);
        for (i = [0:3]) rotate(45 + i * 90) translate([hub - 2, -1.5, fan_t - 3]) cube([fan_size / 2 * sqrt(2) - hub - 3, 3, 3]);
    }
}
// the hand-cut mat, its corners pressed into the chamber fillets
module filter_env() head_at() translate([body_w / 2, 0, head_cz]) along_y(front_t, front_t + 17) rrect([120, 120], open_r);
module magnets_env() for (p = mag_xz()) head_at() {
    // Each disc rests on the bed-facing cavity floor, leaving 0.2 mm above it.
    cyl_y(p, mag_skin, mag_skin + 3, mag[0] / 2 - 0.15);
    cyl_y(p, -cass_t + mag_skin, -cass_t + mag_skin + 3, mag[0] / 2 - 0.15);
}
module battery_env() {
    translate([bat_x0, bat_cy, bat_cz]) rotate([0, 90, 0]) cylinder(d = bat_d, h = bat_l);
    translate([bat_x0, bat_cy - bat_bms[0] / 2, bat_cz + bat_d / 4]) cube([bat_l, bat_bms[0], bat_d / 4 + bat_bms[1]]);
}
// Separate the real PCB holes from the coarse component/pin envelopes. The user
// confirmed clear mounting pads for the 6 mm bosses and 4.5 mm flat-underhead screws.
module pwm_board_env() {
    difference() {
        translate([pwm_x[0], pwm_y0, pwm_z0]) cube([pwm_pcb[1], pwm_pcb[0], pwm_pcb[2]]);
        for (p = pwm_holes()) translate([p[0], p[1], pwm_z0 - 1]) cylinder(d = pwm_hole_d, h = pwm_pcb[2] + 2);
    }
    difference() {
        translate([pwm_x[0], pwm_y0 + 1, pwm_z0 + pwm_pcb[2] - eps])
            cube([pwm_pcb[1], pwm_pcb[0] - 1, pwm_comp_h + eps]);
        for (p = pwm_holes()) translate([p[0], p[1], pwm_z0 + pwm_pcb[2] - 2 * eps])
            cylinder(d = pwm_screw[2] + 0.5, h = pwm_comp_h + 1);
    }
    difference() {
        translate([pwm_x[0] + pwm_edge_free, pwm_y0 + 1, pwm_z0 - pwm_pins])
            cube([pwm_pcb[1] - 2 * pwm_edge_free, pwm_pcb[0] - 1, pwm_pins + eps]);
        for (p = pwm_holes()) translate([p[0], p[1], pwm_z0 - pwm_pins - 1])
            cylinder(d = pwm_boss_d + 0.4, h = pwm_pins + 2);
    }
}
module pot_local() { // local z along the shaft; no nut or washer, PCB screws retain the controller
    translate([-pot_housing / 2, -pot_housing / 2, -pot_mount_t - pot_nose_len - 1])
        cube([pot_housing / 2 + pot_axis_h, pot_housing, pot_nose_len + 1]);
    translate([0, 0, -pot_mount_t - eps]) cylinder(d = pot_bush[0], h = pot_bush[1] + eps);
    translate([0, 0, -pot_mount_t + pot_bush[1] - eps]) cylinder(d = pot_shaft_d, h = pot_shaft_free + eps);
}
module pot_env() {
    translate([pot_x, 0, pot_z]) axis_orient([0, -1, 0]) rotate([0, 0, -90]) pot_local();
    translate([pot_x - pot_tab[0] / 2, pot_mount_t - pot_tab[2],
               pot_z - pot_shaft_d / 2 - pot_tab[3] - pot_tab[1]])
        cube([pot_tab[0], pot_tab[2] + eps, pot_tab[1]]);
}
module chg_module_env() translate([chg_x0, chg_y0, chg_z0]) {
    cube([chg_pcb[0], chg_pcb[2], chg_pcb[1]]);       // PCB upright, normal along y
    translate([chg_comp_end, -chg_comp_h, 0])
        cube([chg_pcb[0] - 2 * chg_comp_end, chg_comp_h + eps, chg_pcb[1]]);
}
// Insulating pad and heatsink on the rear PCB face; both remain clear of the lid.
module chg_sink_env() translate([chg_sink_cx - chg_sink[0] / 2, chg_y0 + chg_pcb[2], chg_sink_z])
    cube([chg_sink[0], chg_sink[3] + chg_sink[2], chg_sink[1]]);
module usbc_env() {
    translate([usbc_xz[0] - usbc[1] / 2, usbc_y0, usbc_xz[1] - usbc[2] / 2]) cube([usbc[1], usbc_board[0], usbc[2]]);
    usbc_stadium(body_d - usbc_protrusion - eps, body_d, 0);
}
module sw_env() let (xf = body_w - sw_well[0]) {
    translate([xf, sw_yz[0] - sw_bezel[0] / 2, sw_yz[1] - sw_bezel[1] / 2]) cube([sw_bezel[2], sw_bezel[0], sw_bezel[1]]);
    translate([xf + sw_bezel[2] - eps, sw_yz[0] - sw_bezel[0] / 2 + 1, sw_yz[1] - sw_bezel[1] / 2 + 1]) cube([sw_rocker + eps, sw_bezel[0] - 2, sw_bezel[1] - 2]);
    translate([xf - sw_body[2], sw_yz[0] - sw_body[0] / 2, sw_yz[1] - sw_body[1] / 2]) cube([sw_body[2] + eps, sw_body[0], sw_body[1]]);
    translate([xf - sw_body[2] - sw_pins, sw_yz[0] - 3, sw_yz[1] - 4]) cube([sw_pins + eps, 6, 8]);
}
module led_env() for (p = led_xz) {   // LEO-AC1 nominal envelope: lens clear of the skin, flange on the boss
    cyl_y(p, led_skin + 0.3, led_boss[1] + eps, led_d / 2);
    cyl_y(p, led_boss[1], led_boss[1] + 1, 1.9);
}
module screw(len, socket = false) difference() {
    union() {
        translate([0, 0, -screw_head_h]) cylinder(d = screw_head_d, h = screw_head_h);
        translate([0, 0, -screw_head_h]) cylinder(r = 1.5, h = len + screw_head_h);
    }
    if (socket) translate([0, 0, -screw_head_h - eps]) cylinder(d = 2.5 / cos(30), h = 1, $fn = 6);
}
// From the front of the fan into the inserts in the cover's posts: the pair is screwed together on the
// bench, before it goes into the head
module screws_fan(socket = false) head_at() for (p = fan_holes()) translate([p[0], head_y[2], p[1]]) axis_orient([0, 1, 0]) screw(len_fan, socket);
module screws_back(socket = false) head_at() for (p = head_bosses()) translate([p[0], body_d - head_pocket[1], p[1]]) axis_orient([0, -1, 0]) screw(len_back, socket);
module screws_head(socket = false) head_at() for (p = rim_bosses())
    rim_at(p, -rim_bearing(p)) screw(rim_length(p), socket);
module screws_lid(socket = false) for (q = ball_posts())
    translate([q[0], q[1], ball[3] + ball_lid_t - lid_pocket]) axis_orient([0, 0, -1]) screw(len_lid, socket);
module screws_feet(socket = false) for (p = foot_xy) translate([p[0], p[1], -foot[2] + foot_head_recess + screw_head_h]) axis_orient([0, 0, 1]) screw(len_foot, socket);

// User's two 2.5 x 8 thermoplastic screws; cylindrical major diameter represents
// the formed thread. Its deliberate pilot interference is checked separately.
module screws_pwm() for (p = pwm_holes()) translate([p[0], p[1], pwm_z0 + pwm_pcb[2]]) {
    cylinder(d = pwm_screw[2], h = pwm_screw[3]);
    translate([0, 0, -pwm_screw[1]]) cylinder(d = pwm_screw[0], h = pwm_screw[1] + eps);
}
// ---------- driver access ----------
// A Torx bit in a 1/4 inch holder, on the head of every screw and pointing away from it: 7 mm for the
// first 25 mm, then 13 mm of holder. Checked for overlap like any other assembly body, so a screw that
// cannot be reached shows up as a collision (user, 2026-09-23: "viele kann man nicht nutzen").
driver = [4, 6, 6.35, 25, 13, 55];   // tip, 1/4 inch shank, holder: diameter and length of each
module driver_at() translate([0, 0, -screw_head_h]) mirror([0, 0, 1]) {
    cylinder(d = driver[0], h = driver[1]);
    translate([0, 0, driver[1] - eps]) cylinder(d = driver[2], h = driver[3] + eps);
    translate([0, 0, driver[1] + driver[3] - eps]) cylinder(d = driver[4], h = driver[5] + eps);
}
// Conservative, unmeasured Wera-style access envelope. Coordinates are relative
// to the outside face of the ISO7380 screw head; no tool enters the solid screw.
// Full 25-mm bit length is retained above that face (2 mm extra conservatism).
// A real 25-mm bit engaging 2 mm with a 14-mm ratchet head leaves its head's
// lower face 9 mm above the screw face. Do not move that face up with the bit.
module front_ratchet_local(swing = 0) {
    cylinder(d = 4, h = 6, $fn = 64);
    translate([0, 0, 6 - eps]) cylinder(d = 7.4, h = 19 + eps, $fn = 96);
    translate([0, 0, 9]) cylinder(d = 22, h = 14, $fn = 96);
    rotate([0, 0, swing]) translate([-7, -76, 9]) cube([14, 76, 14]);
}
// rim_axis() points into the insert. Keep the ratchet handle forwards in -Y
// while its bit points up along the same normal as the rear screws.
module front_ratchet_at(p, swing = 0) let (
    u = -rim_axis(p),
    q = rim_seat_point(p) + u * screw_head_h
) translate(q) multmatrix([
    [u[2], 0, u[0], 0],
    [0,    1, 0,    0],
    [-u[0],0, u[2], 0],
    [0,    0, 0,    1]
]) front_ratchet_local(swing);
module drivers_fan()  head_at() for (p = fan_holes())   translate([p[0], head_y[2], p[1]]) axis_orient([0, 1, 0]) driver_at();
module drivers_back() head_at() for (p = head_bosses()) translate([p[0], body_d - head_pocket[1], p[1]]) axis_orient([0, -1, 0]) driver_at();
module drivers_head() head_at() for (p = rim_bosses())
    if (rim_dir(p) > 0) front_ratchet_at(p);
    else rim_at(p, -rim_bearing(p)) driver_at();
module drivers_feet() for (p = foot_xy) translate([p[0], p[1], -foot[2] + foot_head_recess + screw_head_h]) axis_orient([0, 0, 1]) driver_at();
module drivers_lid()  for (q = ball_posts()) translate([q[0], q[1], ball[3] + ball_lid_t - lid_pocket]) axis_orient([0, 0, -1]) driver_at();

// A slim 4 mm shaft reaches the PCB screws beside the front wall. Its 25 mm
// exposed shaft clears the board components; the wider handle starts above the rim.
module drivers_pwm() for (p = pwm_holes())
    translate([p[0], p[1], pwm_z0 + pwm_pcb[2] + pwm_screw[3]]) {
        cylinder(d = 4, h = 25);
        translate([0, 0, 25 - eps]) cylinder(d = driver[2], h = driver[3] + eps);
        translate([0, 0, 25 + driver[3] - eps]) cylinder(d = driver[4], h = driver[5] + eps);
    }

// ---------- assembly ----------
module assembly(explode = 0) {
    color("#2b2d30") base();
    color("#2b2d30") head_at() translate([0, 0, explode * 1.4]) head_raw();
    color("#2b2d30") head_at() translate([0, explode * 2.4, explode * 1.4]) head_back_raw();
    color("#8c9196") head_at() translate([0, -explode * 1.6, explode * 1.4]) cassette_raw();
    color("#70767c") head_at() translate([0, explode * 0.5, explode * 1.4]) filter_support_raw();
    color("#5a5f66") translate([0, -explode * 0.8, explode * 1.4]) filter_env();
    color("#8c9196") translate([0, -explode * 0.6, 0]) knob();
    color("#5a5f66") translate([0, 0, explode * 0.8]) ball_lid();
    color("#414950") translate([0, -explode * 0.3, explode * 0.4]) battery_ties_env();
    color("#1a1b1d") translate([0, 0, -explode * 0.6]) place_feet();
    color("#3f4247") fan_visual();
}

// ---------- branches: the tools check that print_project.py PARTS matches them ----------
if      (part == "assembly") assembly();
else if (part == "exploded") assembly(18);
else if (part == "metrics") echo("PROJECT_METRICS", [
    ["cass_t", cass_t], ["cass_c", cass_c], ["cass_inset", cass_inset], ["cover_gap", cover_gap],
    ["corner_r", corner_r], ["plan_r", plan_r], ["edge_c", edge_c], ["mag_off", mag_off],
    ["wall", wall], ["tilt", tilt], ["body", [body_w, body_d]], ["head_h", head_h],
    ["fan_insert_front", lug_d - insert_depth], ["fan_thread", len_fan - fan_t],
    ["head_thread", min([for (p = rim_bosses()) rim_length(p) - rim_bearing(p)])],
    ["head_screw", [rim_recess, len_head, rim_seat_d]],
    ["head_mount", [0, rim_front_entry_z+rim_front_bearing+rim_recess, rim_boss_d, rim_fit_gap, rim_boss_depth]],
    ["head_axes", [for (p = rim_bosses()) concat(rim_entry(p), rim_axis(p), [rim_bearing(p), rim_length(p)])]],
    ["chamber", [chamber_sq, chamber_d]], ["open_sq", open_sq],
    ["head_y", head_y], ["mat_stop", mat_stop_y()], ["mat_support", mat_support],
    ["fan_cable_slot", fan_cable_slot],
    ["charge_vent", [chg_vent_y, chg_vent[3]]],
    ["magnet_pocket", mag], ["magnet_skin", mag_skin], ["front_t", front_t],
    ["pot_mount_t", pot_mount_t], ["front_rim_z", base_top(0)],
    ["pwm_front", [pot_x, pot_z, pot_shoulder_y, pwm_install_lift]], ["pwm_pcb", pwm_pcb], ["pwm_origin", [pwm_x[0], pwm_y0, pwm_z0]],
    ["pwm_holes", pwm_holes()], ["pwm_hole_d", pwm_hole_d], ["pwm_boss_d", pwm_boss_d],
    ["pwm_core", [pwm_core_d, pwm_core_depth, pwm_core_entry[0], pwm_core_entry[1]]],
    ["pwm_screw", pwm_screw], ["floor_t", floor_t], ["knob_d", knob_d],
    ["knob_top_z", pot_z + knob_d / 2], ["fan_axis_pitch", fan_pitch],
    ["foot_x", [foot_xy[0][0], foot_xy[1][0]]], ["foot_y", [foot_xy[0][1], foot_xy[2][1]]],
    ["foot_size", foot], ["foot_chamfer", foot_c], ["insert_depth", insert_depth], ["insert_hole_d", insert_hole_d],
    ["insert_w_min", insert_w_min], ["opening_sq", open_sq], ["fan_post", [fan_post_d, head_y[4] - head_y[3]]],
    ["charge_pcb", chg_pcb], ["charge_origin", [chg_x0, chg_y0, chg_z0]],
    ["charge_components", chg_comp_h], ["charge_sink", chg_sink],
    ["charge_tie", chg_tie], ["charge_web", [chg_web_gap, chg_web_touch, chg_web_w, chg_web_back]],
    ["lid_screw", [ball_lid_t, lid_pocket, len_lid]],
    ["battery", [bat_x0, bat_cy, bat_cz, bat_d, bat_l, bat_bms]],
    ["battery_tie_head_clearance", bat_tie_head_clearance], ["battery_ties", bat_tie],
    ["battery_stop", [bat_stop_gap, bat_stop_w, bat_stop_y, bat_stop_c, bat_stop_top]],
    ["battery_tie_anchors", [bat_tie_x, bat_tie_slot, bat_tie_floor, bat_tie_roof, bat_tie_span, bat_tie_wall]],
    ["usb_origin", [usbc_xz[0], usbc_y0, usbc_xz[1]]], ["usb_board", usbc_board],
    ["usb_keeper", [usbc_keeper_w, usbc_keeper_gap, usbc_stop_w]], ["usb_keeper_top", usbc_keeper_top],
    ["usb_keeper_brace", usbc_keeper_brace],
    ["usb_guides", [usbc_guide_lead, usbc_gusset_lid_gap]],
    ["led_pocket", [led_xz, led_d, led_cl, led_skin, led_boss]],
    ["base_h", base_h], ["joint_y", joint_y], ["base_joint_h", base_joint_h],
    ["foot_peg", foot_peg], ["ballast", ball], ["ballast_posts", ball_posts()], ["lid_screw_length", len_lid], ["seat_y", head_y[2]], ["back_y", head_y[4]],
    ["fan_holes", fan_holes()], ["head_bosses", head_bosses()], ["rim_screws", rim_screws]]);
else if (part == "none") {}
else if (part == "base") base();
else if (part == "head") head_print_pose() head_raw();
else if (part == "head_back") head_back_print_pose() head_back_raw();
else if (part == "cassette") cassette_print_pose() cassette_raw();
else if (part == "knob") knob_print_pose() knob_local();
else if (part == "foot") foot_print_pose() foot_local();
else if (part == "ball_lid") ball_lid_print_pose() ball_lid();
else if (part == "filter_support") filter_support_print();
else if (part == "usbc_fit_base") usbc_fit_base();
else if (part == "usbc_fit_lid") usbc_fit_lid();
