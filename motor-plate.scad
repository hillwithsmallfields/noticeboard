motor_diameter = 35.5;
gearbox_diameter = 37;

plate_width = 100;
plate_height = 50;

screw_hole_diameter = 4;
screw_hole_offset = 12;

module motor_plate() {
     difference() {
          square([plate_width, plate_height]);
          translate([plate_width/2, plate_height/2]) circle(d=motor_diameter, centre=true);
          translate([screw_hole_offset, screw_hole_offset]) circle(d=screw_hole_diameter, centre=true);
          translate([plate_width - screw_hole_offset, screw_hole_offset]) circle(d=screw_hole_diameter, centre=true);
          translate([screw_hole_offset, plate_height - screw_hole_offset]) circle(d=screw_hole_diameter, centre=true);
          translate([plate_width - screw_hole_offset, plate_height - screw_hole_offset]) circle(d=screw_hole_diameter, centre=true);
     }
}

motor_plate();
