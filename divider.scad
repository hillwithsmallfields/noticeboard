ventilation_hole_diameter = 9.5;
ventilation_hole_spacing = ventilation_hole_diameter * 1.5;

overhang = 20;
divider_length = 150 + (2 * overhang);
divider_height = 50;
divider_thickness = 5;

buttress_length = 25;

module ventilation_hole_row(columns) {
     for (i=[0:columns-1]) {
          translate([i * ventilation_hole_spacing, 0]) circle(d=ventilation_hole_diameter);
     }
}

module ventilation_hole_grid(columns, rows) {
     for (i=[0:rows-1]) {
          offset = i % 2 == 0 ? 0 : ventilation_hole_spacing/2;
          translate([offset, i * ventilation_hole_spacing]) ventilation_hole_row(columns);
     }
}

module divider() {
     difference() {
          square([divider_length, divider_height]);
          translate([overhang - divider_thickness/2, divider_height/2])
               square([divider_thickness, divider_height/2]);
          translate([overhang + ventilation_hole_spacing, ventilation_hole_spacing * 0.7])
               ventilation_hole_grid(9, 3);
          translate([divider_length - overhang + divider_thickness/2, divider_height/2])
               square([divider_thickness, divider_height/2]);
     }
}

module buttress() {
     difference() {
          square([buttress_length, divider_height]);
          translate([buttress_length / 2, 0]) square([divider_thickness, divider_height/2]);
     }
}

module round_buttress() {
     difference() {
          intersection() {
               translate([divider_height, 0]) circle(r=divider_height);
               square([divider_height*2, divider_height]);
          };
          translate([divider_height - divider_thickness/2, 0]) square([divider_thickness, divider_height/2]);
     }
}

divider();
translate([195, 0]) round_buttress();
translate([300, 0]) round_buttress();
