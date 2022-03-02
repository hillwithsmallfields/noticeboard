#!/usr/bin/env python3

import argparse
import cmd
import time
import RPi.GPIO as GPIO
import pins

class GPIOtestShell(cmd.Cmd):

    """Test commands for probing GPIO pins."""

    prompt = "GPIO test> "

    def __init__(self, mark, space):
        """Set up the test shell."""
        super().__init__()
        self.mark = mark
        self.space = space
        self.active_pin = None
        self.active_board = None
        self.active_description = None
        self.watch_pin = None
        self.watch_board = None
        self.watch_description = None
        self.state = 0

    def postcmd(self, stop, _line):
        return stop

    def do_pin(self, pin_text, *_args):
        """Set which pin we are experimenting with."""
        (self.active_pin,
         self.active_board,
         self.active_description) = (pins.OUTPUT_PINS_BY_NAME[pin_text]
                                     if pin_text in pins.OUTPUT_PINS_BY_NAME
                                     else (int(pin_text), None))
        GPIO.setup(self.active_pin, GPIO.OUT)
        return False

    def do_watch(self, pin_text, *_args):
        """Set which pin we are watching."""
        (self.watch_pin,
         self.watch_board,
         self.watch_description) = (pins.INPUT_PINS_BY_NAME[pin_text]
                                    if pin_text in pins.INPUT_PINS_BY_NAME
                                    else (int(pin_text), None))
        GPIO.setup(self.watch_pin, GPIO.IN)
        return False

    def do_mark(self, mark_text):
        """Set the marking time."""
        self.mark = int(mark_text)

    def do_space(self, space_text):
        """Set the spacing time."""
        self.space = int(space_text)

    def do_blink(self, count_text, *_args):
        """Blink the pin a number of times."""
        for i in range(int(count_text)):
            print("on", i)
            GPIO.output(self.active_pin, 1)
            time.sleep(self.mark)
            print("off", i)
            GPIO.output(self.active_pin, 0)
            time.sleep(self.space)

    def do_names(self, *_args):
        """List the pin names."""
        print("Input pins:")
        for key, value in pins.INPUT_PINS_BY_NAME.items():
            print("  ", key, "BCM", value[0], "board", value[1])
        print("Output pins:")
        for key, value in pins.OUTPUT_PINS_BY_NAME.items():
            print("  ", key, "BCM", value[0], "board", value[1])

    def do_on(self, *_args):
        """Turn the active pin on."""
        self.state = 1
        self.apply_state()
        return False

    def do_off(self, *_args):
        """Turn the active pin off."""
        self.state = 0
        self.apply_state()
        return False

    def do_scan(self, *_args):
        """Scan all the pins."""
        for pin in range(1,26):
            print("Trying pin", pin)
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 1)
            time.sleep(self.mark)
            GPIO.output(pin, 0)
            time.sleep(self.space)
        return False

    def do_monitor(self,
                   *args_text):
        """Watch all the input pins."""
        args = args_text.split()
        count = int(args[0]) if len(args) >= 1 else 60
        delay = float(args[1]) if len(args) >= 2 else 1.0
        input_pins = [(pin_name,
                       pins.OUTPUT_PINS_BY_NAME[pin_name][0])
                      for pin_name in sorted(pins.OUTPUT_PINS_BY_NAME.keys())]
        for pin in input_pins:
            GPIO.setup(pin[1], GPIO.IN)
        while count > 0:
            print("; ".join(["%s: %d" % (p[0],
                                         GPIO.input(p[1]))
                             for p in input_pins]))
            time.sleep(delay)
            count -= 1

    def do_read(self, *_args):
        """Read all the pins."""
        for pin in range(1,26):
            GPIO.setup(pin, GPIO.IN)
            print("pin", pin, "is", GPIO.input(pin))
        if self.active_pin is not None:
            GPIO.setup(self.active_pin, GPIO.OUT)
        return False

    def do_quit(self, *_args):
        """Stop the program."""
        self.do_read()
        return True

    def apply_state(self):
        """Apply the current state."""
        GPIO.output(self.active_pin, self.state)
        if self.active_pin is not None:
            print("output pin", self.active_pin, "set to", self.state)
            print(self.active_description)
        if self.watch_pin is not None:
            print("input pin", self.watch_pin, "is", GPIO.input(self.watch_pin))
            print(self.watch_description)

def main():
    """GPIO pin test program."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mark", type=int, default=2)
    parser.add_argument("--space",type=int, default=3)
    args = parser.parse_args()

    GPIO.setmode(GPIO.BCM)

    GPIOtestShell(args.mark, args.space).cmdloop()

if __name__ == "__main__":
    main()
