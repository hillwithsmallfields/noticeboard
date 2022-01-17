#!/usr/bin/env python3

import argparse
import cmd
import time
import RPi.GPIO as GPIO

class GPIOtestShell(cmd.Cmd):

    """Test commands for probing GPIO pins."""

    prompt = "GPIO test> "

    def __init__(self, mark, space):
        """Set up the test shell."""
        super().__init__()
        self.mark = mark
        self.space = space
        self.active_pin = None
        self.watch_pin = None
        self.state = 0

    def postcmd(self, stop, _line):
        return stop

    def do_pin(self, *args):
        """Set which pin we are experimenting with."""
        self.active_pin = int(*args[0])
        GPIO.setup(self.active_pin, GPIO.OUT)
        return False

    def do_watch(self, *args):
        """Set which pin we are watching."""
        self.watch_pin = int(*args[0])
        GPIO.setup(self.watch_pin, GPIO.IN)
        return False

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

    def do_read(self, *_args):
        """Read all the pins."""
        for pin in range(1,26):
            print("Trying pin", pin)
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
        if self.watch_pin is not None:
            print("input pin", self.watch_pin, "is", GPIO.input(self.watch_pin))

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
