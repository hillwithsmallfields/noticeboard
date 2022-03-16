motor_diameter = 35.5;
gearbox_diameter = 37;

plate_width = 100;
plate_height = gearbox_diameter * 1.75;

screw_hole_diameter = 4;
screw_hole_offset = 12;

module motor_plate() {
     difference() {
          square([plate_width, plate_height]);
          translate([plate_width/2, plate_height/2])
               circle(d=gearbox_diameter);
          translate([screw_hole_offset, screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([plate_width - screw_hole_offset, screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([screw_hole_offset, plate_height - screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([plate_width - screw_hole_offset, plate_height - screw_hole_offset])
               circle(d=screw_hole_diameter);
     }
}

motor_plate();
