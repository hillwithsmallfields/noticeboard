#!/usr/bin/env python3

# experimenting to find why I can't import RPi.GPIO when running under runuser from init.d

import time

while True:
    print("in experiment.py, outputting once per minute")
    time.sleep(60)
