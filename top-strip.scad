max_total_width = 642;
board_frame_depth = 19;

width = 580;
height = 50;

thickness = 6;

bulb_base_width = 16.5;
bulb_base_height = 10;

bracket_height = sqrt(height*height*2)/2;

spacing = width/3;

bracer_height = 16;
notch_height = 8;

arch_inner = 28;

arch_half = (height + arch_inner) / 2;

module notch() {
     translate([-thickness/2,0]) square([thickness, notch_height]);
}

module lamp_hole() {
     circle(d=35, centre=true);
}

module PIR_hole() {
     circle(d=25, centre=true);
}

module lamp_support_arch() {
     intersection() {
	  difference() {
	       /* outside of arch */
	       circle(r=height, centre=true);
	       /* inside of arch */
	       circle(r=arch_inner, centre=true);
	       /* cutout for bulb holder */
	       translate([- bulb_base_width/2, 26]) { square([bulb_base_width, bulb_base_height]); }
	       translate([-arch_half,0]) notch();
	       translate([arch_half,0]) notch();
	  }
	  /* cut it down to a semicircle */
	  translate([-height, 0]) square([height*2, height]);
     }
}

module frontage() {
     difference () {
	  union() {
	       /* one end curve */
	       intersection() {
		    square([height, height]);
		    translate([height, 0]) circle(r=height);
	       }
	       /* central strip */
	       translate([height, 0]) square([width-(2*height), height]);
	       /* the other end curve */
	       translate([width-height, 0]) {
		    intersection() {
			 square([height, height]);
			 circle(r=height);
		    }
	       }
	  }
	  /* holes for lamps and sensor */
	  translate([width/2, height/2]) {
	       translate([-spacing, 0]) lamp_hole();
	       PIR_hole();
	       translate([spacing, 0]) lamp_hole();
	  }
     }
}

inset = 5 + thickness;
bracket_back_height = height;

module bracket() {
     union() {
	  /* the part overhanging the edge of the board */
	  intersection() {
	       translate([bracket_height, 0]) {
		    rotate([0,0,45]) {
			 difference() {
			      square([height,height]);
			      translate([0, height/2]) rotate([0,0,90]) translate([0, -notch_height]) notch();
			 }
		    }
	       }
	       square([bracket_height, bracket_height]);
	  }
	  /* the back diagonal */
	  translate([bracket_height*2 + board_frame_depth, 0]) {
	       intersection() {
		    rotate([0,0,45]) translate([-height, 0])
			 square([height,height]);
		    translate([-bracket_height, 0])
			 square([bracket_height, bracket_height]);
	       }
	  }
	  /* the horizontal piece at the top */
	  translate([bracket_height, 0])
	       square([board_frame_depth, bracket_height]);
	  /* going down behind the board edging */
	  translate([bracket_height+board_frame_depth, - board_frame_depth])
	       square([bracket_height, board_frame_depth]);
	  /* the vertical part at the back */
	  translate([bracket_height+board_frame_depth + inset, - (board_frame_depth + height)]) {
	       difference() {
		    square([bracket_height - inset, bracket_back_height]);
		    translate([0,bracket_back_height-(thickness/2)]) rotate([0,0,-90]) notch();
	       }
	  }
     }
}

module bracer() {
     difference() {
	  intersection() {
	       circle(r=bracer_height, center=true);
	       translate([-bracer_height,0]) square([bracer_height*2, bracer_height]);
	  }
	  translate([0, bracer_height - notch_height]) notch();
     }
}

slide_in_width = 20;
slide_in_margin = 5;
slide_in_rect_width = slide_in_width + (2 * slide_in_margin);

module slide_in_plate(adjust) {
     /* the adjustment is so we can make a plate and a hole for the
      * plate to fit in, with a gap so it can be slid in and out */
     translate([0, -adjust/2]) square([height+adjust, slide_in_width+adjust]);
}

module slide_in_rect() {
	  square([height+slide_in_margin, slide_in_rect_width]);
}

module slide_in_cover() {
     difference() {
	  slide_in_rect();
	  translate([0, (slide_in_rect_width - thickness) / 2])
	       square([bracket_back_height, thickness]);
     }
}

module slide_in_surround() {
     difference() {
	  slide_in_rect();
	  translate([0, slide_in_margin]) slide_in_plate(+.5);
     }
}

frontage();
translate([310,140]) rotate([0,180,90]) bracket();
translate([35, 28]) rotate([0,0,90]) bracket();
translate([50,120]) lamp_support_arch();
translate([220,90]) lamp_support_arch();
translate([135,52]) rotate([0,0,90]) {
     slide_in_surround();
     translate([0, slide_in_margin]) slide_in_plate(-.5);
}
translate([167,52]) rotate([0,0,90]) {
     slide_in_surround();
     translate([0, slide_in_margin]) slide_in_plate(-.5);
}
translate([49,51]) {
      slide_in_cover();
}
translate([110,110]) {
      slide_in_cover();
}
translate([184,70]) {
     for (i = [0:2]) {
	  translate([(bracer_height*2+1)*i, 0]) bracer();
     }
}
translate([184,52]) {
     for (i = [0:3]) {
	  translate([(bracer_height*2+1)*i, 0]) bracer();
     }
}
translate([220,90]) bracer();

