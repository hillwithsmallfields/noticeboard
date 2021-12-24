#!/usr/bin/env python3

import argparse
import RPi.GPIO as GPIO
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--on", type=int, default=2)
    parser.add_argument("--off",type=int, default=3)
    args = parser.parse_args()

    GPIO.setmode(GPIO.BCM)

    for pin in range(1,26):
        print("Trying pin", pin)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)
        time.sleep(args.on)
        GPIO.output(pin, 0)
        time.sleep(args.off)

if __name__ == "__main__":
    main()
