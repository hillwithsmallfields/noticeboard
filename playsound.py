#!/usr/bin/env python3

import argparse
import subprocess

import RPi.GPIO as GPIO

import pins

def sounds(no_on=False, no_off=False,
           begin=None,
           end=None,
           soundfile=None):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins.PIN_SPEAKER, GPIO.OUT, initial=GPIO.LOW)

    if not no_on:
        GPIO.output(pins.PIN_SPEAKER, GPIO.LOW)
    if soundfile:
        if soundfile.endswith(".ogg"):
            subprocess.run((["ogg123"]
                            + (["-k", str(begin)] if begin else [])
                            + (["-K", str(end)] if end else [])
                            + [soundfile]))
        elif soundfile.endswith(".midi"):
            midi_file = Path(soundfile).with_suffix(".midi")
            if not midi_file.exists():
                subprocess.run(["lilypond", soundfile])
            subprocess.run((["timidity"] + [midi_file]))
        elif soundfile.endswith(".ly"):
            subprocess.run((["timidity"] + [soundfile]))
    if not no_off:
        GPIO.output(pins.PIN_SPEAKER, GPIO.HIGH)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-on", action='store_true')
    parser.add_argument("--no-off", action='store_true')
    parser.add_argument("--begin", type=float)
    parser.add_argument("--end", type=float)
    parser.add_argument("--soundfile")
    return vars(parser.parse_args())

if __name__ == "__main__":
    sounds(**get_args())
