# Program for my noticeboard hardware

# See README.md for details

import datetime
import os
import picamera
import re
import select
import sys
import time
import yaml

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

# This is overwritten from /etc/noticeboard.conf if it's available
config = {
    'delays': {
        'lamp': 0.01,
        'motor': 0.01,
        'main_loop': 1.0,
        'activation': 2.0},
    'expected_occupancy': {
        # default for a 9-5 worker who stays in at weekends
        'Monday': ["06:00--08:30",
                   "17:30--23:30"],
        'Tuesday': ["06:00--08:30",
                    "17:30--23:30"],
        'Wednesday': ["06:00--08:30",
                      "17:30--23:30"],
        'Thursday': ["06:00--08:30",
                     "17:30--23:30"],
        'Friday': ["06:00--08:30",
                   "17:30--23:30"],
        'Saturday': ["08:00--23:30"],
        'Sunday': ["08:00--23:30"]},
    'camera': {
        'duration': 180,
        'directory': "/var/spool/camera"},
    'pir_log_file': "/var/log/pir"
}

pwm = None
camera = None

def power_on():
    GPIO.output(pin_psu, GPIO.HIGH.LOW)

def power_off():
    GPIO.output(pin_psu, GPIO.LOW)

last_brightness = 0

def lamps(brightness, fade, left, right):
    """Set lamp brightness.
Left and right lamps can be turned on and off separately, but the
brightness must be the same."""
    if brightness > 0 and (left or right):
        power_on()
        GPIO.output(pin_lamp_left, GPIO.HIGH if left else GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.HIGH if right else GPIO.LOW)
        if fade and brightness != last_brightness:
            step = brightness - last_brightness
            if step > 0:
                while last_brightness < brightness:
                    pwm.ChangeDutyCycle(pin_brightness, last_brightness)
                    time.sleep(config['delays']['lamp'])
                    last_brightness += step
            else:
                while last_brightness > brightness:
                    pwm.ChangeDutyCycle(pin_brightness, last_brightness)
                    time.sleep(config['delays']['lamp'])
                    last_brightness += step
        else:
            pwm.ChangeDutyCycle(pin_brightness, brightness)
    else:
        # just switch the lot off
        GPIO.output(pin_lamp_left, GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.LOW)
        pwm.ChangeDutyCycle(pin_brightness, 0)

def shine():
    """Switch the lamps on."""
    power_on()
    lamps(100, True, True, True)

def quench():
    """Switch the lamps off."""
    lamps(0, True, True, True)

def extend():
    """Slide the keyboard drawer out."""
    if not GPIO.input(pin_extended):
        GPIO.output(pin_motor_a, GPIO.LOW)
        GPIO.output(pin_motor_b, GPIO.HIGH)
        while not GPIO.input(pin_extended):
            time.sleep(config['delays']['motor'])
        GPIO.output(pin_motor_b, GPIO.LOW)

def retract():
    """Slide the keyboard drawer back in."""
    if not GPIO.input(pin_extended):
        GPIO.output(pin_motor_b, GPIO.LOW)
        GPIO.output(pin_motor_a, GPIO.HIGH)
        while not GPIO.input(pin_extended):
            time.sleep(config['delays']['motor'])
        GPIO.output(pin_motor_a, GPIO.LOW)

def report():
    PIR_active = GPIO.input(pin_pir)
    keyboard_extended = GPIO.input(pin_extended)
    keyboard_retracted = GPIO.input(pin_retracted)
    print "PIR:", PIR_active
    print "Keyboard extended:", keyboard_extended
    print "keyboard retracted:", keyboard_retracted
    print "expected_at_home():", expected_at_home()

def convert_interval(interval_string):
    """Convert a string giving start and end times into a tuple.
    For the input "07:30--09:15" the output would be (450, 555)."""
    matched = re.match("\\([0-2][0-9]\\):\\([0-5][0-9]\\)--\\([0-2][0-9]\\):\\([0-5][0-9]\\)", interval_string)
    return (((int(matched.group(1))*60 + int(matched.group(2))),
             (int(matched.group(3))*60 + int(matched.group(4))))
            if matched
            else None)

def expected_at_home():
    """Return whether there is anyone expected to be in the house."""
    # todo: use key-hook sensor
    # todo: see whether desktop computer is responding
    # todo: see whether users' phone is in range
    when = datetime.datetime.now()
    what_time = when.hour() * 60 + when.minute()
    for interval in expected_at_home_times[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][when.weekday()]]:
        if what_time >= interval[0] and what_time <= interval[1]:
            return True
    return False

photographing_duration = None
photographing = False

def handle_possible_intruder():
    """Actions to be taken when the PIR detects someone when no-one is expected to be in the house."""
    global photographing
    when = datetime.datetime.now()
    photographing = when + photographing_duration
    with open(config['pir_log_file'], 'w+') as logfile:
        logfile.write(datetime.datetime.now().isoformat() + "\n")
    # todo: send a remote notification e.g. email with the picture

def take_photo():
    """Capture a photo and store it with a timestamp in the filename."""
    image_filename = os.path.join(config['camera']['directory'], datetime.datetime.now().isoformat()+".jpg")
    camera.capture(image_filename)
    # todo: compare with previous photo in series, and drop any that are very nearly the same

actions = {
    "on": power_on,
    "off": power_off,
    "extend": extend,
    "retract": retract,
    "shine": shine,
    "quench": quench,
    "report": report
    }

# based on https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def rec_update(d, u, i=""):
    for k, v in u.iteritems():
        if isinstance(v, dict):
            d[k] = rec_update(d.get(k, {}), v, "  ")
        elif isinstance(v, list):
            d[k] = d.get(k, []) + [(ve if ve != 'None' else None) for ve in v]
        elif v == 'None':
            d[k] = None
        else:
            d[k] = v
    return d

def main():
    """Interface to the hardware of my noticeboard.
    This is meant for my noticeboard Emacs software to send commands to."""
    config_file_name = "/etc/noticeboard.conf"
    if os.path.isfile(config_file_name):
        with open(os.path.expanduser(os.path.expandvars(config_file_name))) as config_file:
            more_config = yaml.safe_load(config_file)
            rec_update(config, more_config)
    global expected_at_home_times
    expected_at_home_times = { day: [convert_interval(interval_string)
                                     for interval_string in interval_string_list]
                               for day, interval_string_list in config['expected_occupancy'].iteritems()}
    global photographing_duration
    photographing_duration = datetime.timedelta(0, config['camera']['duration'])
    global camera
    camera = picamera.PiCamera()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_pir, GPIO.IN)
    GPIO.setup(pin_retracted, GPIO.IN)
    GPIO.setup(pin_extended, GPIO.IN)
    GPIO.setup(pin_psu, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_a, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_b, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_brightness, GPIO.OUT, initial=GPIO.LOW)
    global pwm
    pwm = GPIO.PWM(pin_brightness, 1000)
    GPIO.setup(pin_lamp_left, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_lamp_right, GPIO.OUT, initial=GPIO.LOW)
    pir_seen_at = None
    main_loop_delay = config['delays']['main_loop']
    activation_delay = config['delays']['activation']
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
                    if expected_at_home():
                        extend()
                        shine()
                    else:
                        handle_possible_intruder()
            else:
                pir_seen_at = time.time()
        else:
            pir_seen_at = None
        if photographing:
            take_photo()
            if datetime.datetime.now() >= photographing:
                photographing = False

if __name__ == "__main__":
    main()
