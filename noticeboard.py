# Program for my noticeboard hardware

# See README.md for details

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

pwm = None

def PSU(power_state):
    GPIO.output(pin_psu, GPIO.HIGH if power_state else GPIO.LOW)

def keyboard(keyboard_state):
    PSU(True)
    # todo: move keyboard

last_brightness = 0

def lamps(brightness, fade, left, right):
    if brightness > 0 and (left or right):
        PSU(True)
        GPIO.output(pin_lamp_left, GPIO.HIGH if left else GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.HIGH if right else GPIO.LOW)
        if fade:
            # todo: set a step, and put a delay in
            for b in range(last_brightness, brightness):
                pwm.ChangeDutyCycle(pin_brightness, b)
        else:
            pwm.ChangeDutyCycle(pin_brightness, brightness)
    else:
        # just switch the lot off
        GPIO.output(pin_lamp_left, GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.LOW)
        pwm.ChangeDutyCycle(pin_brightness, 0)

def main():
    global pwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_pir, GPIO.IN)
    GPIO.setup(pin_psu, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_a, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_b, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_brightness, GPIO.OUT, initial=GPIO.LOW)
    pwm = GPIO.PWM(pin_brightness, 1000)
    GPIO.setup(pin_lamp_left, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_lamp_right, GPIO.OUT, initial=GPIO.LOW)

if __name__ == "__main__":
    main()
