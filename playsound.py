#!/usr/bin/env python3

import argparse

import RPi.GPIO as GPIO

import pins

def sounds(on, off, soundfile):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins.PIN_SPEAKER, GPIO.OUT, initial=GPIO.LOW)

    if on:
        GPIO.output(pins.PIN_SPEAKER, GPIO.HIGH)
    if off:
        GPIO.output(pins.PIN_SPEAKER, GPIO.LOW)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--on", action='store_true')
    parser.add_argument("--off", action='store_true')
    parser.add_argument("soundfile")
    return vars(parser.parse_args())

if __name__ == "__main__":
    sounds(**get_args())
