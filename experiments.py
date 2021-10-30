#!/usr/bin/python3

import argparse

import RPi.GPIO as GPIO
import time

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)    # board pin 12 i.e. 6th pin from end away from sockets, on side nearer edge of board
    pwm = GPIO.PWN(18, 1000)
    pwm.start(0)
    for i in range(30):
        brightness = 0
        for up in (True, False):
            brightness += 1 if up else -1
            pwm.ChangeDutyCycle(brightness)
            sleep(0.01)
    pwm.stop()

if __name__ == '__main__':
    main()
