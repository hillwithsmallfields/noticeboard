#!/usr/bin/python3

# Program for my noticeboard hardware

# See README.md for details

import datetime
import functools
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
    print("Error importing RPi.GPIO!")

# Pin          BCM  Board
# input pins        #
pin_pir        = 16 # 36
pin_retracted  = 23 # 16
pin_extended   = 24 # 18
pin_temperature = 4 # 7fg
# output pins       #
pin_psu        = 17 # 11
pin_speaker    = 22 # 15
pin_motor_a    = 27 # 13
pin_motor_b    = 26 # 37
pin_lamp_left  = 6  # 31
pin_lamp_right = 5 # 29

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
power = None

def power_on():
    """Switch the 12V power on."""
    print("switching 12V power on")
    GPIO.output(pin_psu, GPIO.LOW)
    power = True

def power_off():
    """Switch the 12V power off."""
    print("switching 12V power off")
    GPIO.output(pin_psu, GPIO.HIGH)
    power = False

last_brightness = 0

def lamps(brightness, fade, left, right):
    """Set lamp brightness.
Left and right lamps can be turned on and off separately, but the
brightness must be the same."""
    global last_brightness
    print("lamps", left, right, "to brightness", brightness, "from last_brightness", last_brightness, "with fade", fade)
    if brightness > 0 and (left or right):
        power_on()
        GPIO.output(pin_lamp_left, GPIO.HIGH if left else GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.HIGH if right else GPIO.LOW)
        if fade and brightness != last_brightness:
            fade_delay = config['delays']['lamp']
            step = (brightness - last_brightness) / 10
            print("changing brightness from", last_brightness, "to", brightness, "in steps of", step, "at interval", fade_delay)
            if step > 0:
                while last_brightness < brightness:
                    print(last_brightness)
                    pwm.ChangeDutyCycle(last_brightness)
                    time.sleep(fade_delay)
                    last_brightness += step
            else:
                while last_brightness > brightness:
                    print(last_brightness)
                    pwm.ChangeDutyCycle(last_brightness)
                    time.sleep(fade_delay)
                    last_brightness -= step
        else:
            pwm.ChangeDutyCycle(brightness)
    else:
        # just switch the lot off
        GPIO.output(pin_lamp_left, GPIO.LOW)
        GPIO.output(pin_lamp_right, GPIO.LOW)
        pwm.ChangeDutyCycle(pin_brightness)

def shine():
    """Switch the lamps on."""
    power_on()
    print("switching lamps on")
    lamps(100, True, True, True)

def quench():
    """Switch the lamps off."""
    print("switching lamps off")
    lamps(0, False, False, False)

def extend():
    """Slide the keyboard drawer out."""
    if GPIO.input(pin_extended):
        print("keyboard already extended")
    else:
        power_on()
        step_time = config['delays']['motor']
        timeout = float(config['delays']['motor_timeout'])
        countdown = int(timeout / step_time)
        print("extending keyboard in", countdown, step_time, "time steps")
        GPIO.output(pin_motor_a, GPIO.LOW)
        GPIO.output(pin_motor_b, GPIO.HIGH)
        while not GPIO.input(pin_extended):
            countdown -= 1
            if countdown <= 0:
                print("timing out on keyboard motion")
                break
            time.sleep(step_time)
        GPIO.output(pin_motor_b, GPIO.LOW)

def retract():
    """Slide the keyboard drawer back in."""
    if GPIO.input(pin_retracted):
        print("keyboard already retracted")
    else:
        power_on()
        step_time = config['delays']['motor']
        timeout = float(config['delays']['motor_timeout'])
        countdown = int(timeout / step_time)
        print("retracting keyboard in", countdown, step_time, "time steps")
        GPIO.output(pin_motor_b, GPIO.LOW)
        GPIO.output(pin_motor_a, GPIO.HIGH)
        while not GPIO.input(pin_retracted):
            countdown -= 1
            if countdown <= 0:
                print("timing out on keyboard motion")
                break
            time.sleep(config['delays']['motor'])
        GPIO.output(pin_motor_a, GPIO.LOW)

def at_home():
    """Tell the system I am at home."""
    global manual_at_home
    global manual_away
    manual_at_home = True
    manual_away = False

def away():
    """Tell the system I am away."""
    global manual_at_home
    global manual_away
    manual_at_home = False
    manual_away = True

def auto():
    """Tell the system I'm not telling it whether I'm at home."""
    global manual_at_home
    global manual_away
    manual_at_home = False
    manual_away = False

def report():
    """Output the status of the noticeboard hardware."""
    PIR_active = GPIO.input(pin_pir)
    keyboard_extended = GPIO.input(pin_extended)
    keyboard_retracted = GPIO.input(pin_retracted)
    print("12V power on:", power)
    print("PIR:", PIR_active)
    print("Keyboard extended:", keyboard_extended)
    print("keyboard retracted:", keyboard_retracted)
    print("last_brightness", last_brightness)
    print("expected_at_home():", expected_at_home())

def convert_interval(interval_string):
    """Convert a string giving start and end times into a tuple.
    For the input "07:30--09:15" the output would be (450, 555)."""
    matched = re.match("([0-2][0-9]):([0-5][0-9])--([0-2][0-9]):([0-5][0-9])", interval_string)
    return (((int(matched.group(1))*60 + int(matched.group(2))),
             (int(matched.group(3))*60 + int(matched.group(4))))
            if matched
            else None)

manual_at_home = False
manual_away = False

def expected_at_home():
    """Return whether there is anyone expected to be in the house."""
    # todo: use key-hook sensor
    # todo: see whether desktop computer is responding
    # todo: see whether users' phone is in range
    if manual_at_home:
        return True
    if manual_away:
        return False
    when = datetime.datetime.now()
    what_time = when.hour * 60 + when.minute
    for interval in expected_at_home_times[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][when.weekday()]]:
        if interval is None:
            continue
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
    print("taking photo into", image_filename)
    camera.capture(image_filename)
    # todo: compare with previous photo in series, and drop any that are very nearly the same

def quit_controller():
    """Tell the main loop to quit."""
    global running
    running = False

def show_help():
    """List the commands."""
    maxlen = 1 + functools.reduce(max, map(len, actions.keys()))
    for command_name in sorted(actions.keys()):
        docstring = actions[command_name].__doc__
        if docstring is None:
            docstring = "Undocumented"
        print(command_name + ' '*(maxlen - len(command_name)), docstring)

actions = {
    "auto": auto,
    "away": away,
    "extend": extend,
    "help": show_help,
    "home": at_home,
    "off": power_off,
    "on": power_on,
    "photo": take_photo,
    "quench": quench,
    "quit": quit_controller,
    "report": report,
    "retract": retract,
    "shine": shine
    }

# based on https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def rec_update(d, u, i=""):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = rec_update(d.get(k, {}), v, "  ")
        elif isinstance(v, list):
            d[k] = d.get(k, []) + [(ve if ve != 'None' else None) for ve in v]
        elif v == 'None':
            d[k] = None
        else:
            d[k] = v
    return d

enable_pir = False
running = True

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
                               for day, interval_string_list in config['expected_occupancy'].items()}
    print("noticeboard hardware controller starting")
    global photographing
    global photographing_duration
    photographing_duration = datetime.timedelta(0, config['camera']['duration'])
    global camera
    camera = picamera.PiCamera()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_pir, GPIO.IN)
    GPIO.setup(pin_retracted, GPIO.IN)
    GPIO.setup(pin_extended, GPIO.IN)
    GPIO.setup(pin_psu, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_a, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_motor_b, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_brightness, GPIO.OUT, initial=GPIO.LOW)
    global pwm
    pwm = GPIO.PWM(pin_brightness, 1000) # TODO: change this; the hardware PWM isn't available when using the sound output jack
    GPIO.setup(pin_lamp_left, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_lamp_right, GPIO.OUT, initial=GPIO.LOW)
    pir_seen_at = None
    main_loop_delay = config['delays']['main_loop']
    activation_delay = config['delays']['activation']
    print("noticeboard hardware controller started")
    while running:
        ready, _, _ = select.select([sys.stdin], [], [], main_loop_delay)
        if sys.stdin in ready:
            command = sys.stdin.readline().strip()
            if command in actions:
                actions[command]()
            else:
                print('(error "Unknown noticeboard command" ', command, ')')
        if enable_pir and GPIO.input(pin_pir):
            if pir_seen_at:
                if time.time() > pir_seen_at + activation_delay:
                    print("(pir_triggered)")
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
    print("noticeboard hardware controller stopped")

if __name__ == "__main__":
    main()
