motor_diameter = 35.5;
gearbox_diameter = 37;

plate_width = 100;
plate_height = gearbox_diameter * 1.75;

float_distance = 6;
surround_thickness = 20;

outer_width = plate_width + surround_thickness * 2;
outer_height = plate_height + surround_thickness * 2;

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

module motor_float_surround() {
     difference() {
          square([outer_width, outer_height]);
          translate([surround_thickness-float_distance/2, surround_thickness-float_distance/2]) {
               square([plate_width+float_distance, plate_height+float_distance]);
          }
          translate([screw_hole_offset, screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([outer_width - screw_hole_offset, screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([screw_hole_offset, outer_height - screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([outer_width - screw_hole_offset, outer_height - screw_hole_offset])
               circle(d=screw_hole_diameter);
     }
}

module motor_backing_plate() {
    difference() {
          square([outer_width, outer_height]);
          translate([outer_width/2, outer_height/2])
               circle(d=gearbox_diameter + float_distance);
          translate([screw_hole_offset, screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([outer_width - screw_hole_offset, screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([screw_hole_offset, outer_height - screw_hole_offset])
               circle(d=screw_hole_diameter);
          translate([outer_width - screw_hole_offset, outer_height - screw_hole_offset])
               circle(d=screw_hole_diameter);
     }
}

// motor_plate();

motor_float_surround();

// motor_backing_plate();
