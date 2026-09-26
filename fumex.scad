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
edge_c = 1.2;        // 45 degree chamfer on the bed edges
tilt = 15;           // forward lean of the head (user: the housing itself makes the bend)
base_h = 48;         // joint plane height at mid-depth; the plane rises towards the back
joint_y = 37;        // the joint plane turns about this line (mid-depth)

/* [Head: fan and filter] */
head_h = 145;        // head height (z) in the untilted frame
front_t = 3.2;       // intake face
open_sq = 117;       // square opening in the intake face; its lip holds the mat in the chamber
open_r = 3;
chamber_sq = 121.5;  // filter chamber, 0.75 mm wider than the hand-cut mat all round
chamber_d = 17.5;    // the mat is 17 mm (user, cut from a cooker hood mat)
tube_w = 3;          // wall of the filter chamber inside the shell
lug_d = 10;          // the chamber runs this much further back than the mat: the fan bears on four corner
                     // gussets there and its inserts sit in them
// A flat seat plate with a round bore would be a 4400 mm2 flat overhang over the chamber (analyze.py
// overhangs). Instead the four corners fill in at 45 degrees from the intake face: nothing overhangs,
// the opening stays wider than the swept annulus, and the gussets carry the fan inserts.
plenum = 14.3;       // free space behind the fan: the charge module rides on the back cover in there
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

/* [Fan: Arctic P12 Pro, 120 x 120 x 25 mm PWM, 0.33 A at 12 V] */
fan_size = 120;
fan_t = 25;
fan_pitch = 105;     // mounting hole spacing (120 mm fans)
fan_hole_d = 4.5;
fan_blade_d = 113;
fan_cl = 0.4;        // clearance per side in the corner guides

/* [Filter cassette: grid panel held by four magnet pairs] */
cass_t = 4.5;        // magnet pocket 3.2 plus 1.3 mm skin
cass_inset = 1;      // flange inside the head outline, leaves a ledge beside the finger scoops
mag = [10.3, 3.2];   // pocket for a 10 x 3 neodymium disc (skill: +0.3 diameter, +0.2 depth)
mag_off = 64.2;      // magnet axes from the head centre, on both diagonals

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
mat_notch = 20;      // half-round notches in the intake lip at both side edges: get a finger behind the mat
cradle_t = 4;
cradle_out = 2.5;    // saddle material beyond the cell: every mm here is a mm less ballast trough

/* [PWM fan controller CNY-FA5-PRO: board flat in the bay, potentiometer through the front wall] */
pwm_pcb = [41.05, 32, 1.6]; // measured length (here along y), width (x), PCB thickness
pwm_total_h = 18;    // measured 15 without the fan connector, +3 estimated for the plugged connector
pwm_total_len = 56.30;      // measured rear PCB edge to shaft tip
pwm_comp_h = pwm_total_h - pwm_pcb[2];
pwm_pins = 3;        // solder pins below the PCB (measured 2-3)
pwm_edge_free = 1.5; // pin-free strips along both long edges (measured)
pwm_pad = 1.2;       // rib pads under those strips
pwm_rib = 3;
pot_x = 108;         // potentiometer axis in the front panel; left enough that the switch pins clear the board
pot_z = 21;          // above the front foot bosses, low enough that the knob clears the front rim
pot_axis_h = 6.3;    // PCB top to shaft centre
pot_shaft_d = 5.8;   // measured outside the knurling
pot_shaft_free = 9.5;
pot_bush = [6.73, 5];       // bushing outside diameter, thread length from the housing shoulder (measured)
pot_nut = [11.6, 2.15];     // across corners (10 across flats), thickness (measured)
pot_washer = [11, 0.85];
pot_thread_reserve = 0.2;
pot_bush_cl = 0.4;
pot_housing = 13;    // potentiometer housing on the PCB edge (12 mm pot assumed)
pot_recess_r = 10;
pot_tab = [2.1, 0.8, 1.2, 2.1];   // anti-rotation tab below the shaft (measured)
pot_tab_cl = 0.2;
pot_pcb_cl = 0.3;

/* [Speed knob] */
knob_d = 28;
knob_len = 14;
knob_gap = 1.5;      // underside off the wall face
knob_bore_over = 0.3;
knob_cavity_d = 13;
knob_stem_d = 10;
knob_stem_cl = 0.5;
knob_bore_cl = 0;    // nominal 5.8 bore; validate the push fit on the real knurled shaft
knob_slit = [1, 6];
knob_flutes = 18;
knob_flute = [2, 1.2];
knob_c = 1.2;
knob_mark = [1.6, 7.5, 0.8];   // pointer groove in the top face (single colour, no inlay)

/* [Charge/boost module: eletechsup LFUPSMA, 12 V variant, upright on the head floor] */
// The CN3058E is a linear charger: at 1 A from 5 V it turns about 1.6 W into heat. Nothing may stick out
// of the housing and the board belongs in the air (user, 2026-09-22), so it stands upright in the plenum
// on the head floor, heatsink towards the fan. On the floor rather than on the back cover (user), so the
// cover comes off without it and its six wires drop straight through the floor notch into the base.
chg_pcb = [32.2, 11, 1.0];  // measured length (here along x), width (z), thickness (y)
chg_comp_h = 2.7;    // parts above the PCB (3.7 total, measured)
chg_cx = 72.5;       // board centre across the head
chg_z_off = 2;       // lower edge above the holder plate; the heatsink then clears the plate
chg_sink = [14, 14, 6, 1];  // user's heatsink behind the IC: length, width, height, insulating pad
chg_sink_end = 9.5;  // near end of the heatsink from the IN end; it overhangs that end by 4.5 mm
chg_fan_gap = 1.5;   // heatsink face to the back of the fan
chg_br = [3.6, 1.4, 2, 2.5];  // end brackets: thickness (x; 3 left only 1 mm beside the groove), groove width, depth, tie tunnel
// The holder is a part of its own, screwed to the head floor with two M3 x 8. Anything standing in the
// plenum blocks the fan on its way out, so it has to be removable - that is exactly why the module does
// not sit on the fixed floor.
chg_plate = 3;       // holder base plate
chg_screw_in = 5;    // its screw axes from both ends

/* [USB-C charging socket: PD trigger module (pads 1-4 open = 5 V) in the back wall] */
usbc_board = [12.88, 10.35, 4.30];  // measured: length without the receptacle (y), width (x), height (z)
usbc_protrusion = 1.5;
usbc = [usbc_board[0] + usbc_protrusion, usbc_board[1], usbc_board[2]];
usbc_shell = [8.9, 3.22];
usbc_shell_bottom = 1.1;
usbc_plate = usbc_protrusion;   // local wall thickness: PCB edge inside, receptacle face flush outside
usbc_xz = [106, 45]; // above the ballast lid (user, 2026-09-22), high enough that the lid lifts out under it
usbc_floor = 6;      // the channel floor reaches only this far from the back wall: a full-length floor
                     // would be a 198 mm2 flat overhang, and a 45 degree gusset would sit in the trough
usbc_cl = 0.2;
usbc_wall = 2;

/* [Power switch: measured 14.7 x 20.9 mm rocker, snap-in, in the right side wall] */
sw_yz = [37, 34];    // forward and up: the ballast trough now runs the full width behind it    // centre in the right wall, behind the PWM board and beside the battery
sw_cut = [12.2, 19.2];      // measured panel hole; long side upright, so the printed bridge is short
sw_cut_cl = 0.2;     // PETG holes come out undersize
sw_bezel = [14.7, 20.9, 2]; // outside width (y), height (z), bezel thickness
sw_rocker = 5;
sw_body = [sw_cut[0] - 0.2, sw_cut[1] - 0.2, 11];
sw_total_depth = 23;
sw_pins = sw_total_depth - sw_bezel[2] - sw_rocker - sw_body[2];
sw_panel = 1.5;
sw_well = [5, 0.2, 2.2];    // depth below the outer face, floor margin, wall measured horizontally

/* [Charge indicator LED] */
led_d = 3;           // 3 mm breathing LED; black PETG is opaque, so it looks through a real hole
led_xz = [88, 21];
led_cl = 0.2;
led_boss = [7, 5];   // boss inside the wall: diameter, length

/* [Cable tie loops on the inside of the back wall (strain relief)] */
tie_loop = [8, 6, 6, 5, 2.5];   // width (x), height (z), stand-off (y), tunnel width, tunnel depth
tie_loop_xz = [[118, 45], [128, 45]];   // high enough that the ballast lid lifts out under them

/* [Ballast trough with a screwed lid (user, 2026-09-22): loose iron offcuts, no resin] */
// Only mass behind the centre of mass helps against tipping, so the cell moved forward and everything
// behind it is one trough. A lid instead of potting keeps it serviceable and stops the offcuts from
// reaching the wiring; it screws straight into printed posts with M3 plastic-forming screws.
ball = [3, 142, 53, 26];    // interior x from / to (both housing walls), front wall outer face (y),
                     // rim and lid underside (z). Full width and lower, with the USB-C socket above it
                     // (user, 2026-09-22); the rim stays below the run-outs of the rear head screw bosses
ball_wall = 2;
ball_post = 10;      // screw posts in the four corners; at Ø10, 3.5 mm off both walls, they close the
                     // corner completely (Ø8 left a sealed sliver void, which exports as a second body)
ball_lid_t = 3;
ball_lip = 0;        // no lip over the front wall: the cell has to lift past it (battery_out)
ball_dish = [16, 1.5];   // finger dish in the lid instead: diameter, depth
ball_rim = 0.4;      // trough walls end this far below the posts, so the lid bears on the four posts
                     // alone and no two faces of the base share the plane z = ball[3]
// M3 plastic-forming screws straight into the posts, no heat-set inserts (user, 2026-09-22)
pt_core = 2.5;       // core hole, about 0.8 x d; check the holding torque on a test print
pt_depth = 10;

/* [Feet: four TPU pads, each screwed with one M3 x 8 from below] */
foot = [18, 16, 4.5];   // length (x), width (y), height
// wide apart for stability, and clear of the PWM board above them
// Pads flush with the front face and clear of the corner radius, so all four sit fully under the housing
// (user, 2026-09-22). The tipping edge is then y = 0, which the ballast more than makes up for.
foot_xy = [[16, 8], [129, 8], [16, 62], [129, 62]];
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
// Head screws along the side walls: their bosses merge into those walls, so they hang from the rim on
// solid material. y stays clear of the back cover lip inside the head, x of the electronics below.
rim_screws = [[7.5, 9], [137.5, 9], [7.5, 62], [137.5, 62]];
rim_boss_len = 9;
rim_boss_d = 10;     // 13 bulged 12.5 mm into the bay and read as a random step (user, 2026-09-22)
// ISO 7380 button head Torx from the user's set (M3 x 6, 8, 10, 12, 16, 25) except the fan screws
len_fan = 30;        // M3 x 30, bought: through the 25 mm frame, 5 mm of thread in the insert
len_back = 8;
len_head = 8;
len_foot = 8;

// ---------- derived values ----------
head_cz = base_h + head_h / 2;
head_y = [front_t, front_t + chamber_d, front_t + chamber_d + lug_d,
          front_t + chamber_d + lug_d + fan_t, body_d - back_t];   // chamber, mat end, fan, plenum, cover
tube_sq = chamber_sq + 2 * tube_w;
pot_mount_t = pot_bush[1] - pot_nut[1] - pot_washer[1] - pot_thread_reserve;
pot_nose_len = pwm_total_len - pwm_pcb[0] - pot_shaft_free - pot_bush[1];
pwm_wall_gap = pot_mount_t + pot_nose_len - wall;    // negative: the PCB edge reaches into the wall slot
pot_recess = wall - pot_mount_t;
pwm_pcb_slot = max(0, -pwm_wall_gap) + pot_pcb_cl;
pwm_y0 = wall + pwm_wall_gap;
pwm_z0 = pot_z - pot_axis_h - pwm_pcb[2];
pwm_x = [pot_x - pwm_pcb[1] / 2, pot_x + pwm_pcb[1] / 2];
knob_sleeve_z = pot_washer[1] + pot_nut[1] - knob_gap + knob_stem_cl;
knob_bore_top = pot_bush[1] - pot_mount_t + pot_shaft_free - knob_gap + knob_bore_over;
usbc_y0 = body_d - wall - usbc_board[0] + usbc_plate;
chg_z0 = base_h + wall + chg_plate + chg_z_off;         // lower edge of the board, above the holder plate
chg_cz = chg_z0 + chg_pcb[1] / 2;
chg_y = head_y[3] + chg_fan_gap + chg_sink[3] + chg_sink[2];   // PCB face towards the fan
chg_x0 = chg_cx - chg_pcb[0] / 2;                       // OUT end of the board
chg_sink_cx = chg_x0 + chg_pcb[0] - chg_sink_end + chg_sink[0] / 2;   // heatsink centre along x

function base_top(y) = base_h + (y - joint_y) * tan(tilt);
function fan_holes() = [for (sx = [-1, 1], sz = [-1, 1]) [body_w / 2 + sx * fan_pitch / 2, head_cz + sz * fan_pitch / 2]];
function mag_xz() = [for (sx = [-1, 1], sz = [-1, 1]) [body_w / 2 + sx * mag_off, head_cz + sz * mag_off]];
// four screws are enough for the back cover (user, 2026-09-22)
function head_bosses() = [for (sx = [-1, 1], z = [base_h + boss_bottom, base_h + head_h - boss_inset])
                          [body_w / 2 + sx * (body_w / 2 - boss_inset), z]];
function rim_bosses() = rim_screws;
// lowest point of the cell over y, or clear of it altogether
function bat_low(y) = abs(y - bat_cy) >= bat_d / 2 + bat_clear ? 1e6
                    : bat_cz - sqrt(pow(bat_d / 2 + bat_clear, 2) - pow(y - bat_cy, 2));
// x of the two charge-module brackets; the back cover's lip is notched over exactly these
function chg_bracket_x() = [chg_x0 + chg_br[2] - chg_br[0], chg_x0 + chg_pcb[0] - chg_br[2]];
function chg_hx() = [chg_bracket_x()[0] - 1, chg_bracket_x()[1] + chg_br[0] + 1];
function chg_screws() = [for (x = [chg_hx()[0] + chg_screw_in, chg_hx()[1] - chg_screw_in])
                         [x, (chg_y + head_y[4] - 1) / 2]];
function ball_posts() = [for (x = [ball[0] + 3.5, ball[1] - 3.5],
                             y = [ball[2] + ball_wall + 3.5, body_d - wall - 3.5]) [x, y]];
// both rear corners of the lid meet a rounded housing corner
function pot_tab_z() = [pot_shaft_d / 2 + pot_tab[3] - pot_tab_cl, pot_bush[0] / 2 + pot_tab[3] + pot_tab[1] + pot_tab_cl];

assert(head_y[4] + back_t == body_d, "Head depth must fill the shared footprint");
assert(wall >= 3 * 0.4, "Walls below three perimeters");
assert(lug_d - insert_depth >= 3, "Less than 3 mm of gusset in front of the fan insert pockets");
// where the insert pocket starts, the gusset flank must still clear the insert by the datasheet wall
assert(lug_flank(head_y[2] - insert_depth) >= insert_hole_d / 2 + insert_w_min,
       "Fan insert too close to the gusset flank");
assert(open_sq < chamber_sq - 2, "Intake lip does not hold the mat");
assert(pot_mount_t > 1.2, "Wall under washer and nut too thin");
assert(base_top(0) > pot_z + knob_d / 2 + 2, "Knob reaches over the front rim");
// the stack must fit between the fan and the back cover, and the bracket ramp must clear the fan
assert(chg_y + chg_pcb[2] + chg_comp_h + 0.5 < head_y[4], "Charge module reaches the back cover");
assert(chg_y - chg_z_off > head_y[3], "Bracket ramp runs into the fan");
assert(mag[1] < cass_t - 1, "Cassette too thin for the magnet pockets");
assert(len_fan - fan_t >= 5, "Fan screws reach less than 5 mm into the insert");
assert(min([for (p = foot_xy) bat_low(p[1])]) > foot_boss[1], "Foot boss reaches into the battery");
assert(foot_boss[1] - insert_depth >= 1.2, "Foot insert pocket floor thinner than three perimeters");
assert(floor_t - foot_peg[1] >= 3 * 0.4, "Floor under the foot peg holes thinner than three perimeters");
assert(len_head - wall >= 5, "Head screws reach less than 5 mm into the base inserts");

// ---------- helpers ----------
module rrect(size, r) offset(r = r) offset(delta = -r) square(size, center = true);
module rect(a, b) translate([min(a[0], b[0]), min(a[1], b[1])]) square([max(abs(b[0] - a[0]), eps), max(abs(b[1] - a[1]), eps)]);
// 2D children in (x, z) extruded along y, and in (y, z) extruded along x
module along_y(y0, y1) translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children();
module along_x(x0, x1) translate([x0, 0, 0]) multmatrix([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]) linear_extrude(x1 - x0) children();
module cyl_y(c, y0, y1, r1, r2 = -1) translate([c[0], y0, c[1]]) rotate([-90, 0, 0]) cylinder(r1 = r1, r2 = r2 < 0 ? r1 : r2, h = y1 - y0);
module cyl_x(c, x0, x1, r1, r2 = -1) translate([x0, c[0], c[1]]) rotate([0, 90, 0]) cylinder(r1 = r1, r2 = r2 < 0 ? r1 : r2, h = x1 - x0);
// Point the local +z axis along an axis-aligned direction
module orient(d) {
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

module base_outline(inset = 0) translate([body_w / 2, body_d / 2]) rrect([body_w - 2 * inset, body_d - 2 * inset], max(corner_r - inset, 0.5));
module head_outline(inset = 0) translate([body_w / 2, head_cz]) rrect([body_w - 2 * inset, head_h - 2 * inset], max(corner_r - inset, 0.5));
module head_centre_sq(size, r) translate([body_w / 2, head_cz]) rrect([size, size], r);

// Square grid of rounded cells, centred on the origin and trimmed to a square area
module grid_2d(area, bar = grid_bar, gap = grid_gap) let (n = max(1, floor((area + bar) / (gap + bar))),
                                                         span = n * gap + (n - 1) * bar)
    intersection() {
        for (i = [0:n - 1], j = [0:n - 1])
            translate([-span / 2 + gap / 2 + i * (gap + bar), -span / 2 + gap / 2 + j * (gap + bar)]) rrect([gap, gap], grid_r);
        square([area, area], center = true);
    }

// ---------- head: shell, filter chamber, fan seat (untilted frame) ----------
module head_raw() difference() {
    union() {
        difference() {
            along_y(0, head_y[4]) head_outline();                       // outer shell
            along_y(front_t, head_y[4] + eps) head_outline(wall);       // one cavity behind the intake face
        }
        along_y(front_t - 0.5, head_y[2]) difference() {                // filter chamber tube, overlapping the intake face
            head_centre_sq(tube_sq, open_r + tube_w);
            head_centre_sq(chamber_sq, open_r);
        }
        fan_lugs();
        for (p = head_bosses()) cyl_y(p, head_y[2], head_y[4], boss_d / 2);
        fan_guides();
    }
    along_y(-eps, front_t + eps) head_centre_sq(open_sq, open_r);       // intake opening; its lip holds the mat
    for (p = fan_holes()) cyl_y(p, head_y[2] - insert_depth, head_y[2] + eps, insert_hole_d / 2);   // into the gussets
    for (p = head_bosses()) cyl_y(p, head_y[4] - insert_depth, head_y[4] + eps, insert_hole_d / 2);
    for (p = mag_xz()) cyl_y(p, -eps, mag[1], mag[0] / 2);              // magnet pockets, open at the intake face
    for (sx = [-1, 1]) cyl_y([body_w / 2 + sx * body_w / 2, head_cz], -eps, scoop[1],
                             scoop[0] / 2 + eps, scoop[0] / 2 - scoop[1]);   // finger scoops at the side edges
    for (sx = [-1, 1]) cyl_y([body_w / 2 + sx * open_sq / 2, head_cz], -eps, front_t + eps, mat_notch / 2);   // grip the mat
    for (p = rim_bosses()) translate([p[0], p[1], base_h - 1]) {
        cylinder(d = screw_clear_d, h = wall + 2);
        translate([0, 0, 1 + wall - 0.6]) cylinder(d = head_pocket[0], h = 1);   // the button head sits flush
    }
    translate([body_w / 2 - 10, head_y[3] + 2, base_h - 1]) cube([20, 10, wall + 2]);   // fan and module wires to the bay
    for (q = chg_screws()) translate([q[0], q[1], base_h + wall - insert_depth]) cylinder(d = insert_hole_d, h = insert_depth + 1);
    difference() {                                                      // chamfer on the intake bed face
        along_y(-eps, edge_c) head_outline(-1);
        hull() { along_y(-eps, -eps + tip) head_outline(edge_c); along_y(edge_c - tip, edge_c) head_outline(0); }
    }
}
// Corner gussets from the intake face back to the fan: 45 degree flanks, so they print without support.
// The fan bears on their back faces and its heat-set inserts sit in them; the mat presses into them.
module fan_lugs() for (sx = [-1, 1], sz = [-1, 1]) translate([body_w / 2, 0, head_cz]) scale([sx, 1, sz]) hull() {
    along_y(front_t, front_t + tip) corner_tri(0.6);
    along_y(head_y[2] - tip, head_y[2]) corner_tri(lug_leg());
}
function lug_leg(y = -1) = sqrt(2) * ((y < 0 ? head_y[2] : y) - front_t);   // 45 degrees: 1 mm per mm of depth
// distance from a fan insert axis to the gusset flank at depth y
function lug_flank(y) = (lug_leg(y) - 2 * (chamber_sq / 2 - fan_pitch / 2)) / sqrt(2);
module corner_tri(l) let (c = chamber_sq / 2) polygon([[c, c], [c - l, c], [c, c - l]]);
// Holder for the charge module: a plate that screws to the head floor and two grooved end brackets that
// take the short edges of the board. One cable tie through the tunnels above it stops the board lifting
// out. Printed with the plate on the bed, so the brackets and their grooves are plain vertical walls.
module chg_holder() difference() {
    union() {
        translate([chg_hx()[0], chg_y - 0.5, base_h + wall])
            cube([chg_hx()[1] - chg_hx()[0], head_y[4] - 0.5 - chg_y + 0.5, chg_plate]);
        for (sx = [-1, 1]) let (x0 = chg_bracket_x()[sx < 0 ? 0 : 1])
            translate([x0, chg_y, base_h + wall + chg_plate - eps])   // not in front of the PCB: the
                // heatsink overhangs the board's IN end and would clip the right bracket
                cube([chg_br[0], head_y[4] - 0.5 - chg_y, chg_z0 + chg_pcb[1] + 4 - base_h - wall - chg_plate]);
    }
    for (sx = [-1, 1]) let (x0 = chg_bracket_x()[sx < 0 ? 0 : 1],
                            g0 = sx < 0 ? x0 + chg_br[0] - chg_br[2] : x0) {
        translate([g0 - eps, chg_y - 0.2, chg_z0])                 // groove: board end with its parts
            cube([chg_br[2] + 2 * eps, chg_pcb[2] + chg_comp_h + 0.4, chg_pcb[1] + 4]);
        translate([x0 - 1, chg_y + 1, chg_z0 + chg_pcb[1] + 1])    // cable tie tunnel
            cube([chg_br[0] + 2, chg_br[3], 2]);
    }
    for (q = chg_screws()) translate([q[0], q[1], base_h + wall - 1]) {
        cylinder(d = screw_clear_d, h = chg_plate + 2);
        translate([0, 0, 1 + chg_plate - head_pocket[1]]) cylinder(d = head_pocket[0], h = head_pocket[1] + 1);
    }
}
module chg_holder_print_pose() translate([-chg_hx()[0], -(chg_y - 0.5), -(base_h + wall)]) children();
module fan_guides() for (sx = [-1, 1], sz = [-1, 1]) translate([body_w / 2, 0, head_cz]) scale([sx, 1, sz])
    along_y(head_y[2] - 0.5, head_y[3]) let (i = fan_size / 2 + fan_cl, o = i + guide[0]) {
        rect([i, i - guide[1]], [o, o]);      // L round the corner, both inner faces on the fan
        rect([i - guide[1], i], [o, o]);
    }
module head() head_at() head_raw();
module head_print_pose() translate([0, base_h + head_h, 0]) rotate([90, 0, 0]) children();   // intake face on the bed

// ---------- head back cover (untilted frame) ----------
module head_back_raw() intersection() {
    translate([-1, head_y[4] - lip_h - 1, base_h + cover_gap]) cube([body_w + 2, back_t + lip_h + 2, head_h]);
    difference() {
    union() {
        along_y(head_y[4], body_d) head_outline();
        along_y(head_y[4] - lip_h, head_y[4] + eps) difference() {
            head_outline(wall + lip_cl);
            head_outline(wall + lip_cl + lip_t);
            for (p = head_bosses()) offset(r = 0.8) translate([p[0], p[1]]) circle(d = boss_d);
            translate([chg_hx()[0] - 0.8, base_h])   // the charge module holder stands in the lip band
                square([chg_hx()[1] - chg_hx()[0] + 1.6, chg_z0 + chg_pcb[1] + 8 - base_h]);
        }
    }
    translate([body_w / 2, 0, head_cz]) along_y(head_y[4] - 1, body_d + 1) grid_2d(exhaust_sq);
    for (p = head_bosses()) {
        cyl_y(p, head_y[4] - 1, body_d + 1, screw_clear_d / 2);
        cyl_y(p, body_d - head_pocket[1], body_d + 1, head_pocket[0] / 2);
    }
    difference() {                                                      // chamfer on the outer bed face
        along_y(body_d - edge_c, body_d + eps) head_outline(-1);
        hull() { along_y(body_d - edge_c, body_d - edge_c + tip) head_outline(0);
                 along_y(body_d - tip, body_d) head_outline(edge_c); }
    }
    }
}
module head_back() head_at() head_back_raw();
module head_back_print_pose() translate([0, -base_h, body_d]) rotate([-90, 0, 0]) children();   // outer face on the bed

// ---------- filter cassette (untilted frame, in front of the intake face) ----------
module cassette_raw() difference() {
    along_y(-cass_t, 0) head_outline(cass_inset);
    translate([body_w / 2, 0, head_cz]) along_y(-cass_t - 1, 1) grid_2d(open_sq);
    for (p = mag_xz()) cyl_y(p, -mag[1], eps, mag[0] / 2);              // pockets open towards the head
    difference() {                                                      // chamfer on the outer bed face
        along_y(-cass_t - eps, -cass_t + edge_c) head_outline(-1);
        hull() { along_y(-cass_t - eps, -cass_t + tip) head_outline(cass_inset + edge_c);
                 along_y(-cass_t + edge_c - tip, -cass_t + edge_c) head_outline(cass_inset); }
    }
}
module cassette() head_at() cassette_raw();
module cassette_print_pose() translate([0, base_h + head_h, cass_t]) rotate([90, 0, 0]) children();   // grid face on the bed

// ---------- base ----------
module base() difference() {
    union() {
        difference() {
            linear_extrude(base_top(body_d) + 1) base_outline();
            translate([0, 0, floor_t]) linear_extrude(base_top(body_d) + 2) base_outline(wall);
        }
        battery_cradle();
        pwm_ribs();
        led_boss_body();
        usbc_channel();
        rim_boss_bodies();
        foot_bosses();
        tie_loops();
        sw_wall_box();
        ballast_walls();
    }
    joint_halfspace();                                   // the tilted joint plane cuts the rim
    pot_cuts();
    led_cut();
    usbc_cuts();
    sw_cuts();
    ballast_screw_holes();
    for (p = rim_bosses()) head_at() translate([p[0], p[1], base_h - insert_depth]) cylinder(d = insert_hole_d, h = insert_depth + 2);
    for (p = foot_xy) translate([p[0], p[1], -1]) cylinder(d = insert_hole_d, h = insert_depth + 1);
    for (p = foot_xy) translate([p[0] + foot_peg[2], p[1], -eps])
        cylinder(d = foot_peg[0] + foot_peg_cl, h = foot_peg[1] + eps);   // anti-rotation peg holes
    difference() {                                                      // chamfer on the bottom bed face
        translate([-1, -1, -eps]) cube([body_w + 2, body_d + 2, edge_c + eps]);
        hull() { translate([0, 0, -eps]) linear_extrude(tip) base_outline(edge_c);
                 translate([0, 0, edge_c - tip]) linear_extrude(tip) base_outline(0); }
    }
}

// three open saddles up to the axis; the protection board faces up, foam tape keeps the cell quiet
module battery_cradle() for (cx = cradle_x) translate([cx - cradle_t / 2, 0, 0]) along_x(0, cradle_t) difference() {
    rect([bat_cy - bat_d / 2 - cradle_out, floor_t - eps], [bat_cy + bat_d / 2 + cradle_out, bat_cz]);
    translate([bat_cy, bat_cz]) circle(d = bat_d + 2 * bat_clear);
}
// two ribs under the pin-free long edges, pads on top, solder pins hanging free between them
module pwm_ribs() for (sx = [-1, 1]) let (edge = pot_x + sx * pwm_pcb[1] / 2,        // long edge of the board
                                          inner = edge - sx * pwm_edge_free,        // where the solder pins start
                                          r0 = min(inner, inner + sx * pwm_rib), p0 = min(edge - sx * 0.3, inner + sx * 0.3)) {
    translate([r0, pwm_y0, floor_t - eps]) cube([pwm_rib, pwm_pcb[0] - 2, pwm_z0 - pwm_pad - floor_t + eps]);
    translate([p0, pwm_y0, pwm_z0 - pwm_pad - eps]) cube([pwm_edge_free - 0.6, pwm_pcb[0] - 2, pwm_pad + eps]);
}
module pot_cuts() {
    cyl_y([pot_x, pot_z], -1, pot_mount_t, (pot_bush[0] + pot_bush_cl) / 2);          // bushing through the flat outer face
    cyl_y([pot_x, pot_z], pot_mount_t, wall + eps, pot_recess_r);                     // round housing pocket from inside
    translate([pot_x - (pot_tab[0] + 2 * pot_tab_cl) / 2, -1, pot_z - pot_tab_z()[1]])
        cube([pot_tab[0] + 2 * pot_tab_cl, pot_mount_t + 1, pot_tab_z()[1] - pot_tab_z()[0]]);
    if (pwm_pcb_slot > 0.01) translate([pwm_x[0] - pot_pcb_cl, wall - pwm_pcb_slot, pwm_z0 - pot_pcb_cl])
        cube([pwm_pcb[1] + 2 * pot_pcb_cl, pwm_pcb_slot + eps, pwm_pcb[2] + 2 * pot_pcb_cl]);
}
module led_boss_body() cyl_y(led_xz, wall - eps, led_boss[1], led_boss[0] / 2);
module led_cut() {
    cyl_y(led_xz, -1, wall + eps, (led_d + led_cl) / 2);
    cyl_y(led_xz, wall, led_boss[1] + 1, (led_d + led_cl) / 2 + 0.5);                 // seat for the LED flange
}
// channel on the inside of the back wall, open at the top for the wires, on a 45 degree gusset
module usbc_channel() {
    difference() {
        translate([usbc_xz[0] - usbc[1] / 2 - usbc_cl - usbc_wall, usbc_y0 - 2, usbc_xz[1] - usbc[2] / 2 - usbc_cl - usbc_wall])
            cube([usbc[1] + 2 * (usbc_cl + usbc_wall), body_d - wall - usbc_y0 + 2, usbc[2] + 2 * usbc_cl + usbc_wall]);
        translate([usbc_xz[0] - usbc[1] / 2 - usbc_cl, usbc_y0 - 3, usbc_xz[1] - usbc[2] / 2 - usbc_cl])
            cube([usbc[1] + 2 * usbc_cl, body_d - usbc_y0 + 4, usbc[2] + 2 * usbc_cl + 2]);
        translate([usbc_xz[0] - usbc[1], body_d - wall - usbc[0] - 1, usbc_xz[1] - usbc[2] / 2 - usbc_cl - usbc_wall - 1])
            cube([2 * usbc[1], usbc[0] + 1 - usbc_floor, usbc_wall + 1]);   // floor only near the wall
    }
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
// front and right wall of the trough (left and back are the housing walls), the four screw posts, and a
// ledge along the back wall for the lid
module ballast_walls() {
    translate([ball[0], ball[2], floor_t - eps]) cube([ball[1] - ball[0], ball_wall, ball[3] - ball_rim - floor_t + eps]);
    for (q = ball_posts()) translate([q[0], q[1], floor_t - eps]) cylinder(d = ball_post, h = ball[3] - floor_t + eps);
}
module ballast_screw_holes() for (q = ball_posts())
    translate([q[0], q[1], ball[3] - pt_depth]) cylinder(d = pt_core, h = pt_depth + 1);
// lid: it rests on the two walls, the ledge and the four posts, and reaches ball_lip over the front wall
module ball_lid() difference() {
    // 0.2 mm off the two housing walls, and a chamfer where their inner corner is rounded
    translate([0, 0, ball[3]]) linear_extrude(ball_lid_t) difference() {
        translate([ball[0] + 0.2, ball[2] - ball_lip])
            square([ball[1] - ball[0] - 0.4, body_d - wall - 0.2 - ball[2] + ball_lip]);
        translate([ball[0], body_d - wall]) polygon([[0, 0], [5, 0], [0, -5]]);
        translate([ball[1], body_d - wall]) polygon([[0, 0], [-5, 0], [0, -5]]);
        translate([ball[1] - 5, ball[2] - 1]) square([6, 11]);   // clear of the switch well on the way out
    }
    for (q = ball_posts()) translate([q[0], q[1], ball[3] - 1]) {
        cylinder(d = screw_clear_d, h = ball_lid_t + 2);
        translate([0, 0, 1 + ball_lid_t - head_pocket[1]]) cylinder(d = head_pocket[0], h = head_pocket[1] + 1);
    }
    translate([(ball[0] + ball[1]) / 2, ball[2] + 6, ball[3] + ball_lid_t - ball_dish[1]])   // grip to slide it out
        cylinder(d = ball_dish[0], h = ball_dish[1] + 1);
}
module ball_lid_print_pose() translate([-ball[0], -(ball[2] - ball_lip), -ball[3]]) children();
// What the trough holds: its interior minus the housing itself, so the foot boss, the posts and the
// rounded inner corners are cut out of it and the reported mass is what really fits.
module ballast_env() difference() {
    translate([ball[0], ball[2] + ball_wall, floor_t])
        cube([ball[1] - ball[0], body_d - wall - ball[2] - ball_wall, ball[3] - floor_t]);
    base();
    // the insert pockets of the rear feet are sealed voids under a 2 mm cap: no resin gets in there
    for (p = foot_xy) translate([p[0], p[1], -1]) cylinder(d = insert_hole_d + 0.4, h = insert_depth + 1);
}
module tie_loops() for (p = tie_loop_xz) difference() {
    translate([p[0] - tie_loop[0] / 2, body_d - wall - tie_loop[2], p[1] - tie_loop[1] / 2])
        cube([tie_loop[0], tie_loop[2] + eps, tie_loop[1]]);
    translate([p[0] - tie_loop[3] / 2, body_d - wall - tie_loop[4], p[1] - tie_loop[1] / 2 - 1])
        cube([tie_loop[3], tie_loop[4] + eps, tie_loop[1] + 2]);
}
// bosses for the head screws: columns under the tilted rim in the corners, merged into both walls,
// with a 45 degree run-out below so they print without support
// The boss hangs under the rim where there is no wall, so it runs out to the nearest wall (p[2]) and its
// underside drops 45 degrees towards that wall: no island, nothing to support.
// The boss hangs under the rim: it merges into the nearest side wall and its underside drops 45 degrees
// towards that wall, so nothing starts in the air. The ramp runs along x, the axis the housing bends about.
module rim_boss_bodies() for (p = rim_bosses()) head_at()
    let (left = p[0] < body_w / 2, xw = left ? 0 : body_w - wall, dx = left ? p[0] - wall : body_w - wall - p[0])
    hull() {
        translate([p[0], p[1], base_h - rim_boss_len]) cylinder(d = rim_boss_d, h = rim_boss_len + 1);
        translate([xw, p[1] - rim_boss_d / 2, base_h - rim_boss_len - dx]) cube([wall, rim_boss_d, rim_boss_len + 1 + dx]);
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
module knob() translate([pot_x, -knob_gap, pot_z]) orient([0, -1, 0]) knob_local();
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
module magnets_env() for (p = mag_xz()) head_at() { cyl_y(p, 0, 3, mag[0] / 2 - 0.15); cyl_y(p, -3, 0, mag[0] / 2 - 0.15); }
module battery_env() {
    translate([bat_x0, bat_cy, bat_cz]) rotate([0, 90, 0]) cylinder(d = bat_d, h = bat_l);
    translate([bat_x0, bat_cy - bat_bms[0] / 2, bat_cz + bat_d / 4]) cube([bat_l, bat_bms[0], bat_d / 4 + bat_bms[1]]);
}
module pwm_board_env() translate([pwm_x[0], pwm_y0, pwm_z0]) {
    cube([pwm_pcb[1], pwm_pcb[0], pwm_pcb[2]]);
    translate([0, 1, pwm_pcb[2] - eps]) cube([pwm_pcb[1], pwm_pcb[0] - 1, pwm_comp_h + eps]);
    translate([pwm_edge_free, 1, -pwm_pins]) cube([pwm_pcb[1] - 2 * pwm_edge_free, pwm_pcb[0] - 1, pwm_pins + eps]);
}
module pot_local(nut = true) {       // local z along the shaft, z = 0 at the outer wall face; local -y is the board side
    translate([-pot_housing / 2, -pot_housing / 2, -pot_mount_t - pot_nose_len - 1])
        cube([pot_housing / 2 + pot_axis_h, pot_housing, pot_nose_len + 1]);
    translate([0, 0, -pot_mount_t - eps]) cylinder(d = pot_bush[0], h = pot_bush[1] + eps);
    if (nut) {
        cylinder(d = pot_washer[0], h = pot_washer[1]);
        translate([0, 0, pot_washer[1] - eps]) cylinder(d = pot_nut[0], h = pot_nut[1] + eps);
    }
    translate([0, 0, -pot_mount_t + pot_bush[1] - eps]) cylinder(d = pot_shaft_d, h = pot_shaft_free + eps);
}
module pot_env(nut = true) translate([pot_x, 0, pot_z]) orient([0, -1, 0]) rotate([0, 0, -90]) pot_local(nut);
module pot_nut_env() translate([pot_x, 0, pot_z]) orient([0, -1, 0]) difference() {
    union() {
        cylinder(d = pot_washer[0], h = pot_washer[1]);
        translate([0, 0, pot_washer[1] - eps]) cylinder(d = pot_nut[0], h = pot_nut[1] + eps);
    }
    translate([0, 0, -1]) cylinder(d = pot_bush[0] + 0.1, h = pot_washer[1] + pot_nut[1] + 2);
}
module chg_holder_at() head_at() chg_holder();
module chg_module_env() head_at() translate([chg_x0, chg_y, chg_z0]) {
    cube([chg_pcb[0], chg_pcb[2], chg_pcb[1]]);                        // PCB
    translate([0, chg_pcb[2] - eps, 0]) cube([chg_pcb[0], chg_comp_h + eps, chg_pcb[1]]);   // parts, towards the cover
}
// insulating pad and heatsink on the back of the board, facing into the fan's exhaust
module chg_sink_env() head_at() translate([chg_sink_cx - chg_sink[0] / 2, chg_y - chg_sink[3] - chg_sink[2], chg_cz - chg_sink[1] / 2])
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
module led_env() {
    cyl_y(led_xz, 0, led_boss[1], led_d / 2);
    cyl_y(led_xz, wall, wall + 1, 1.9);
}
module screw(len, socket = false) difference() {
    union() {
        translate([0, 0, -screw_head_h]) cylinder(d = screw_head_d, h = screw_head_h);
        translate([0, 0, -screw_head_h]) cylinder(r = 1.5, h = len + screw_head_h);
    }
    if (socket) translate([0, 0, -screw_head_h - eps]) cylinder(d = 2.5 / cos(30), h = 1, $fn = 6);
}
module screws_chg(socket = false) head_at() for (q = chg_screws()) translate([q[0], q[1], base_h + wall + chg_plate - head_pocket[1]]) orient([0, 0, -1]) screw(len_back, socket);
module screws_fan(socket = false) head_at() for (p = fan_holes()) translate([p[0], head_y[3], p[1]]) orient([0, -1, 0]) screw(len_fan, socket);
module screws_back(socket = false) head_at() for (p = head_bosses()) translate([p[0], body_d - head_pocket[1], p[1]]) orient([0, -1, 0]) screw(len_back, socket);
module screws_head(socket = false) head_at() for (p = rim_bosses()) translate([p[0], p[1], base_h + wall]) orient([0, 0, -1]) screw(len_head, socket);
module screws_feet(socket = false) for (p = foot_xy) translate([p[0], p[1], -foot[2] + foot_head_recess + screw_head_h]) orient([0, 0, 1]) screw(len_foot, socket);

// ---------- assembly ----------
module assembly(explode = 0) {
    color("#2b2d30") base();
    color("#2b2d30") head_at() translate([0, 0, explode * 1.4]) head_raw();
    color("#2b2d30") head_at() translate([0, explode * 2.4, explode * 1.4]) head_back_raw();
    color("#8c9196") head_at() translate([0, -explode * 1.6, explode * 1.4]) cassette_raw();
    color("#5a5f66") translate([0, -explode * 0.8, explode * 1.4]) filter_env();
    color("#8c9196") translate([0, -explode * 0.6, 0]) knob();
    color("#5a5f66") translate([0, 0, explode * 0.8]) ball_lid();
    color("#1a1b1d") translate([0, 0, -explode * 0.6]) place_feet();
    color("#3f4247") fan_visual();
}

// ---------- branches: the tools check that print_project.py PARTS matches them ----------
if      (part == "assembly") assembly();
else if (part == "exploded") assembly(18);
else if (part == "metrics") echo("PROJECT_METRICS", [
    ["wall", wall], ["tilt", tilt], ["body", [body_w, body_d]], ["head_h", head_h],
    ["fan_insert_front", lug_d - insert_depth], ["fan_thread", len_fan - fan_t],
    ["head_thread", len_head - wall], ["chamber", [chamber_sq, chamber_d]], ["open_sq", open_sq],
    ["magnet_pocket", mag], ["pot_mount_t", pot_mount_t], ["front_rim_z", base_top(0)],
    ["knob_top_z", pot_z + knob_d / 2], ["fan_axis_pitch", fan_pitch],
    ["foot_x", [foot_xy[0][0], foot_xy[1][0]]], ["foot_y", [foot_xy[0][1], foot_xy[2][1]]],
    ["foot_size", foot], ["insert_depth", insert_depth], ["insert_hole_d", insert_hole_d],
    ["insert_w_min", insert_w_min], ["opening_sq", chamber_sq], ["lug_leg", lug_leg()],
    ["lug_flank", lug_flank(head_y[2] - insert_depth)],
    ["base_h", base_h], ["joint_y", joint_y],
    ["foot_peg", foot_peg], ["ballast", ball], ["ballast_posts", ball_posts()], ["pt_core", pt_core], ["seat_y", head_y[2]], ["back_y", head_y[4]],
    ["fan_holes", fan_holes()], ["head_bosses", head_bosses()], ["rim_screws", rim_screws]]);
else if (part == "none") {}
else if (part == "base") base();
else if (part == "head") head_print_pose() head_raw();
else if (part == "head_back") head_back_print_pose() head_back_raw();
else if (part == "cassette") cassette_print_pose() cassette_raw();
else if (part == "knob") knob_print_pose() knob_local();
else if (part == "foot") foot_print_pose() foot_local();
else if (part == "ball_lid") ball_lid_print_pose() ball_lid();
else if (part == "chg_holder") chg_holder_print_pose() chg_holder();
