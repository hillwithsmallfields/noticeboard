#!/usr/bin/env python3

import argparse
import subprocess

import RPi.GPIO as GPIO

import pins

def say(no_on=False, no_off=False,
        text="Testing"):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins.PIN_SPEAKER, GPIO.OUT, initial=GPIO.LOW)

    if not no_on:
        GPIO.output(pins.PIN_SPEAKER, GPIO.LOW)
    subprocess.run(["espeak", text])
    if not no_off:
        GPIO.output(pins.PIN_SPEAKER, GPIO.HIGH)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-on", action='store_true')
    parser.add_argument("--no-off", action='store_true')
    parser.add_argument("--text")
    return vars(parser.parse_args())

if __name__ == "__main__":
    say(**get_args())
