// Spacers for gluing cork keys in noticeboard with a screen and keyboard embedded in it
// Time-stamp: <2016-04-03 12:45:54 jcgs>

/* The keypad is a cheap generic USB keypad, available from many suppliers */

/* I'm using the keypad rotated to landscape, so I've described it ready-rotated */
total_keypad_width = 94;
total_keypad_height = 75;
columns = 5;
rows = 4;

key_width = total_keypad_width / columns;
key_height = total_keypad_height / rows;
key_margin = 1;

key_depth = 10;
spacer_slot_depth = key_depth / 2;

module slot_array(n, s) {
     for (i = [1 : n]) {
	  translate([0,(i * s)]) square([spacer_slot_depth, key_margin * 2]);
     }
}

module long_spacer() {
     difference () {
	  square([key_depth, total_keypad_width]);
	  slot_array(4, key_width);
     }
}

module short_spacer() {
     difference () {
	  square([key_depth, total_keypad_height]);
	  slot_array(3, key_height);
     }
}

// slot_array(4, key_width);
// long_spacer();
// translate([0, total_keypad_width * 1.1]) short_spacer();

for (i = [ 1 : 4 ] ) {
     translate([i * key_depth * 1.1, 0]) long_spacer();
}
