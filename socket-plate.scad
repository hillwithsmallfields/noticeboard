total_width = 426;
total_height = 28;

net_height = 21.5;
net_width = 21.5;

mains_height = 19;
mains_width = 27;
mains_screw_offset = 7;
mains_screw_diameter = 3;

keyboard_diameter = 15;
     
module ethernet_hole() {
     square([net_height, net_width]);
}

module mains_hole() {
     union() {
	  difference() {
	       square([mains_height, mains_width]);
	       translate([0, -8]) rotate([0,0,45]) square([10,10]);
	       translate([0, mains_width -6]) rotate([0,0,45]) square([10,10]);
	  }
	  translate([mains_height / 2, -mains_screw_offset]) circle(d=mains_screw_diameter, center=true);
	  translate([mains_height / 2, mains_width + mains_screw_offset]) circle(d=mains_screw_diameter, center=true);
     }
}

module socket_plate() {
     difference() {
	  square([total_height, total_width]);
	  translate([(total_height - net_height) / 2, 25]) ethernet_hole();
	  translate([(total_height - mains_height) / 2, (total_width - mains_width) / 2]) mains_hole();
	  translate([total_height / 2, 75]) circle(d=keyboard_diameter/2, center=true);
	  }
}

socket_plate();
