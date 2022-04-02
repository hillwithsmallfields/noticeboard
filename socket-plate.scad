plate_length = 460;
gap_height = 28;
overlap = 18;
plate_height = gap_height + overlap;

half_height = gap_height / 2;

fixing_height = gap_height + overlap/2;

top_plate_length = 460;

/* TODO:
   button holes
   temperature sensor hole
 */

module screw_hole() {
     circle(d=4);
}

module motor_socket(outer) {
     circle(d=outer ? 16 : 25);
     translate([19, 0]) {
          children();
     }
}

module ethernet_socket() {
     square([22, 20]);
}

module usb_socket(outer) {
     length = outer ? 15 : 17;
     width = outer ? 7 : 10;
     translate([-width/2, -length/2]) square([width, length]);
}

module usb_sockets(outer, n_sockets) {
     per_socket = 13;
     for (i=[0:n_sockets-1]) {
          translate([per_socket*i, 0]) usb_socket(outer);
     }
     translate([per_socket * (n_sockets + 0.5), 0]) {
          children();
     }
}

module hdmi_socket(outer) {
     width = outer ? 18 : 31;
     depth = outer ? 9 : 10;    /* not sure about the 10 */
     translate([-width/2, -depth/2]) {
          square([width, depth]);
     }
     if (outer) {
          translate([-25/2, 0]) circle(d=4);
          translate([25/2, 0]) circle(d=4);
     }
     translate([25, 0]) {
          children();
     }
}

module iec(width, height, corner_depth, hole_spacing) {
     union([]) {
          translate([-width/2, -height/2])
               polygon(points=[[0, 0],
                               [0, height - corner_depth],
                               [corner_depth, height],
                               [width - corner_depth, height],
                               [width, height - corner_depth],
                               [width, 0],
                               [0, 0]]);
          translate([-hole_spacing/2, 0]) circle(d=4);
          translate([hole_spacing/2, 0]) circle(d=4);
     }
}

module mains_inlet() {
     iec(28, 20, 5, 40);
     translate([50, 0]) {
          children();
          }
}

module mains_outlet() {
     iec(34, 24, 8, 40);
}

module audio_socket() {
     circle(d=10.5);
     translate([20,0]) {
          children();
     }
}

module din_socket() {
     union() {
          circle(d=16);
          translate([-11.5, 0]) circle(d=3);
          translate([11.5, 0]) circle(d=3);
     }
     translate([40, 0]) {
          children();
     }
}

module rocker_switch(outer) {
     length = outer ? 29 : 35;
     translate([-length/2, -5.25]) square([length, 10.5]);}

module jst3(outer) {
     translate([0, -3]) {
          square([10, outer ? 6 : 15]);
     }
     translate([25, 0]) {
          children();
     }
}

module test_sockets() {
     translate([-3, -3]) {
          for (i = [0:1]) {
               for (j = [0:1]) {
                    translate([j*6, i*6]) {
                         circle(d=4);
                    }
               }
          }
     }
     translate([12, 0]) {
          children();
     }
}

module reset_button() {
     circle(d=13);
     translate([22.5, 0]) {
          children();
     }
}

module reset_button_mounting() {
     difference() {
          circle(d=24);
          circle(d=7);
     }
}

module reset_button_spacer() {
     difference() {
          circle(d=24);
          circle(d=13);
     }
}

module reset_button_nut_holder() {
     difference() {
          circle(d=24);
          circle($fn=6, d=11.05);
     }
}

ventilation_hole_diameter = 6;
ventilation_hole_spacing = ventilation_hole_diameter * 1.5;

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

module cooling_fan() {
     /* "Ultra-miniature Brushless Fan Electric DC 5V 6V 2507 Mini Micro Tiny Cooling NI" has 3mm holes in a 21mm square, and is 25mm overall */
     union() {
          circle(d=22);
          hole_place = 21/2;
          translate([hole_place, hole_place]) circle(d=3);
          translate([hole_place, -hole_place]) circle(d=3);
          translate([-hole_place, -hole_place]) circle(d=3);
          translate([-hole_place, hole_place]) circle(d=3);
     }
}

module screw_holes(n_holes, total_length) {
     spacing = total_length / (n_holes - 1);
     for (i = [0:n_holes]) {
          translate([i * spacing, 0]) screw_hole();
     }
}

module socket_plate(outer) {
     difference() {
          square([plate_length, plate_height]);
          translate([15, fixing_height]) screw_holes(5, plate_length-30);
          translate([150, 0]) ethernet_socket();
          translate([77, 14]) rocker_switch(outer);
          translate([30, 14]) {
               circle(d=12);
               translate([20, 0]) circle(d=12);
          }
          translate([120, 14]) mains_inlet();
          translate([195, 14]) hdmi_socket(outer);
          translate([plate_length/2, 14]) {
               motor_socket(outer) {
                    test_sockets() {
                         jst3(outer) {
                              reset_button() {
                                   audio_socket() {
                                        usb_sockets(true, 3) {
                                             din_socket() {
                                                  mains_outlet();
                                             }
                                        }
                                   }
                              }
                         }
                    }
               }
          }
          /* translate([290, 8]) ventilation_hole_grid(6, 3); */
     }
}

module usb_holder_plate(outer, n_sockets) {
     difference() {
          square([20*n_sockets-10, plate_height*0.6]);
          translate([10, 14]) {
               usb_sockets(outer, n_sockets);
          }
     }
}

module top_plate() {
     difference() {
          square([top_plate_length, plate_height]);
          translate([330, 0]) square([20, 4]);
          translate([15, fixing_height]) screw_holes(5, top_plate_length-30);
          translate([20, 10]) circle(d=10);
          translate([top_plate_length/2, 10]) circle(d=10);
          
          n_fans = 4;
          fan_spacing = top_plate_length / n_fans;
          translate([fan_spacing/2, half_height]) {
               for (ifan=[0:n_fans-1]) {
                    translate([fan_spacing*ifan, 0]) cooling_fan();
               }
          }
     }
}

socket_plate(true);
translate([0, plate_height + 3]) socket_plate(false);
translate([0, (plate_height + 3) * 2]) top_plate();
translate([20, (plate_height + 8) * 3]) {
     reset_button_mounting();
     translate([26, 0]) reset_button_spacer();
     translate([52, 0]) reset_button_nut_holder();
     translate([70, -15]) usb_holder_plate(true, 3);
     translate([130, -15]) usb_holder_plate(false, 3);
     translate([190, -15]) usb_holder_plate(false, 3);
}
