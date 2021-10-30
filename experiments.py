#!/usr/bin/python3

import argparse

import RPi.GPIO as GPIO
import time

PIN = 12

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)
    pwm = GPIO.PWM(PIN, 1000)
    pwm.start(0)
    for i in range(30):
        brightness = 0
        for up in (True, False):
            for step in range(100):
                brightness += 1 if up else -1
                pwm.ChangeDutyCycle(brightness)
                time.sleep(0.01)
    pwm.stop()

if __name__ == '__main__':
    main()
