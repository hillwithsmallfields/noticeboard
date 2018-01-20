# Program for my noticeboard hardware

# See README.md for details

import select
import sys
import time

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print "Error importing RPi.GPIO!"

# Pin          BCM  Board
# input pins        #
pin_pir        = 4  # 7
pin_retracted  = 23 # 16
pin_extended   = 24 # 18
# output pins       #
pin_psu        = 17 # 11
pin_motor_a    = 27 # 13
pin_motor_b    = 22 # 15
pin_brightness = 5  # 29
pin_lamp_left  = 6  # 31
pin_lamp_right = 13 # 33

lamp_delay = 0.01
motor_delay = 0.01
main_loop_delay = 1.0

pwm = None

def power_on():
    GPIO.output(pin_psu, GPIO.HIGH.LOW)

def power_off():
    GPIO.output(pin_psu, GPIO.LOW)

last_brightness = 0

def lamps(brightness, fade, left, right):
    if brightness > 0 and (left or right):
        power_on()
        GPIO.output(pin_lamp_left, GPIO.HIGH if left else GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.HIGH if right else GPIO.LOW)
        if fade and brightness != last_brightness:
            step = brightness - last_brightness
            if step > 0:
                while last_brightness < brightness:
                    pwm.ChangeDutyCycle(pin_brightness, last_brightness)
                    time.sleep(lamp_delay)
                    last_brightness += step
            else:
                while last_brightness > brightness:
                    pwm.ChangeDutyCycle(pin_brightness, last_brightness)
                    time.sleep(lamp_delay)
                    last_brightness += step
        else:
            pwm.ChangeDutyCycle(pin_brightness, brightness)
    else:
        # just switch the lot off
        GPIO.output(pin_lamp_left, GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.LOW)
        pwm.ChangeDutyCycle(pin_brightness, 0)

def shine():
    power_on()
    lamps(100, True, True, True)

def quench():
    lamps(0, True, True, True)

def extend():
    if not GPIO.input(pin_extended):
        GPIO.output(pin_motor_a, GPIO.LOW)
        GPIO.output(pin_motor_b, GPIO.HIGH)
        while not GPIO.input(pin_extended):
            time.sleep(motor_delay)
        GPIO.output(pin_motor_b, GPIO.LOW)

def retract():
    if not GPIO.input(pin_extended):
        GPIO.output(pin_motor_b, GPIO.LOW)
        GPIO.output(pin_motor_a, GPIO.HIGH)
        while not GPIO.input(pin_extended):
            time.sleep(motor_delay)
        GPIO.output(pin_motor_a, GPIO.LOW)

actions = {
    "on": power_on,
    "off": power_off,
    "extend": extend,
    "retract", retract,
    "shine", shine,
    "quench", quench
    }

activation_delay = 2.0

def main():
    global pwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_pir, GPIO.IN)
    GPIO.setup(pin_retracted, GPIO.IN)
    GPIO.setup(pin_extended, GPIO.IN)
    GPIO.setup(pin_psu, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_a, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_b, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_brightness, GPIO.OUT, initial=GPIO.LOW)
    pwm = GPIO.PWM(pin_brightness, 1000)
    GPIO.setup(pin_lamp_left, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_lamp_right, GPIO.OUT, initial=GPIO.LOW)
    pir_seen_at = None
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], main_loop_delay)
        if sys.stdin in ready:
            command = sys.stdin.readline()
            if command in actions:
                actions[command]()
            else:
                print '(error "Unknown noticeboard command" ', command, ')'
        if GPIO.input(pin_pir):
            if pir_seen_at:
                if time.time() > pir_seen_at + activation_delay:
                    print "(pir_triggered)"
                    extend()
                    shine()
            else:
                pir_seen_at = time.time()
        else:
            pir_seen_at = None

if __name__ == "__main__":
    main()
