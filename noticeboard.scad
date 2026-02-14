// Cork noticeboard with a screen and keyboard embedded in it
// Time-stamp: <2016-04-06 07:02:59 jcgs>

total_width = 75;
total_height = 94;
columns = 4;
rows = 5;
key_width = total_width / columns;
key_height = total_height / rows;
key_x_margin = 3;
key_y_margin = 3;

/* I'm using the keypad rotated to landscape, so I've described it ready-rotated */
total_keypad_width = 94;
total_keypad_height = 75;
columns = 5;
rows = 4;

key_width = total_keypad_width / columns;
key_height = total_keypad_height / rows;
key_margin = 1;

/* The screen is a 7" bare LCD with a separate driver board, with no
 * frame or case; like the keypad, it's a generic commodity item */

screen_height = 100;
screen_width = 165;

screen_ribbon_height = 4;
screen_ribbon_width = 40;

/* The camera is a PiCam */

camera_height = 25;
camera_width = 24;

/* How far to offset the main parts from each other */
gap_between_keypad_and_screen = 25;
keypad_x_margin = (screen_width - total_keypad_width) / 2;
gap_between_camera_and_screen = 25;

module key(y, x, spacing) {
     translate([key_margin + y * (key_height + spacing), key_margin + x * (key_width + spacing)])
	  square([key_height - 2 * key_margin, key_width - 2 * key_margin]);
}

module keys(maxrow, maxcol, spacing) {
     for (i = [0 : maxrow - 1]) {
	  for (j = [0 : maxcol - 1]) {
	       key(i, j, spacing);
	  }
     }
}

module keypad() {
     difference() {
	  // todo: rounded corners?
	  square([total_keypad_height, total_keypad_width]);
	  keys(rows, columns, 0);
     }
}

module easy_cutting_keypad() {
	  square([total_keypad_height, total_keypad_width]);
	  keys(rows, columns, -2 * key_margin);
}

module screen() {
     square([screen_height, screen_width]);
}

module camera() {
     square([camera_height, camera_width]);
}

module screen_ribbon_cutout() {
     translate([(- screen_ribbon_height / 2),
		(screen_width / 2) - (screen_ribbon_width / 2)])
	  square([screen_ribbon_height, screen_ribbon_width]);
     }

module screen_backing() {
     difference() {
	  screen();
	  screen_ribbon_cutout();
     }
}


module main_corkboard_cuts() {
     translate([0, keypad_x_margin]) keypad();
     // translate([0, keypad_x_margin]) easy_cutting_keypad();
     translate([total_keypad_height + gap_between_keypad_and_screen, 0]) {
	  union() {
	       screen();
	       screen_ribbon_cutout();
	  }
     }
}

// scale([1,-1])
// main_corkboard_cuts();
/* translate([screen_height * 2.25, 0]) { */
/*      union () { */
/* 	  screen_backing(); */
/* 	  translate([screen_height * 1.2, 0]) screen_backing(); */
/*      } */
/* } */

keypad();
