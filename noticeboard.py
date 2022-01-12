#!/usr/bin/env python3

# Program for my noticeboard hardware

# See README.md for details

import datetime
import functools
import os
import picamera
import subprocess
import re
import select
import shlex
import sys
import time
import yaml

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!")

# Pin          BCM  Board
# input pins        #
pin_pir        = 17 # 11
pin_retracted  = 11 # 23
pin_extended   =  5 # 29
pin_porch_pir  = 19 # 35
pin_temperature = 4 # 7
# output pins       #
pin_psu        =  8 # 24
pin_speaker    =  7 # 26
pin_motor_a    = 23 # 16
pin_motor_b    = 24 # 17
pin_lamp_left  = 12 # 32
pin_lamp_right = 13 # 33
pin_porch_lamp =  2 # 3

# see https://forums.raspberrypi.com/viewtopic.php?t=278003 for driving the lamps
# see https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20 for the temperature sensor

# This is overwritten from /etc/noticeboard.conf if it's available
config = {
    'delays': {
        'lamp': 0.01,
        'motor': 0.01,
        'main_loop': 1.0,
        'pir_delay': 2.0,
        'step_max': 200},
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

camera = None

class Lamp(object):

    pass

    def __init__(self, pin):
        self.gpio = pin
        self.target = 0
        self.current = 0
        self.pwm = GPIO.PWM(self.gpio, 1000)
        GPIO.setup(self.gpio, GPIO.OUT, initial=GPIO.LOW)

    def set(self, brightness):
        self.target = brightness

    def step(self):
        if self.current < self.target:
            if self.current == 0:
                self.pwm.start(0)
            self.current += 1
            self.pwm.ChangeDutyCycle(self.current)
        elif self.current > self.target:
            self.current -= 1
            if self.current == 0:
                self.pwm.stop()
            else:
                self.pwm.ChangeDutyCycle(self.current)

    def changing():
        return self.current != self.target

class NoticeBoardHardware(object):

    pass

    def __init__(self, config):
        self.config = config
        self.power = False
        self._lamps = [Lamp(pin_lamp_left), Lamp(pin_lamp_right)]
        self.keyboard_status = 'unknown'
        self.moving_steps = 0
        self.pir_seen_at = 0
        self.porch_pir_seen_at = 0
        self.music_process = None
        self.speech_process = None
        self.user_status = 'unknown'
        self.temperature = None
        self.camera = picamera.PiCamera()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_pir, GPIO.IN)
        GPIO.setup(pin_porch_pir, GPIO.IN)
        GPIO.setup(pin_retracted, GPIO.IN)
        GPIO.setup(pin_temperature, GPIO.IN)
        GPIO.setup(pin_extended, GPIO.IN)
        GPIO.setup(pin_psu, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_speaker, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_motor_a, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_motor_b, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_porch_lamp, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_lamp_left, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_lamp_right, GPIO.OUT, initial=GPIO.LOW)

    def on(self):
        """Switch the 12V power on."""
        print("switching 12V power on")
        GPIO.output(pin_psu, GPIO.LOW)
        self.power = True

    def off(self):
        """Switch the 12V power off."""
        print("switching 12V power off")
        GPIO.output(pin_psu, GPIO.HIGH)
        self.power = False

    def lamps(self, brightness):
        if brightness > 0:
            self.power_on()
        for lamp in self._lamps:
            lamp.set(brightness)

    def shine(self):
        """Switch the lamps on."""
        print("switching lamps on")
        lamps(100)

    def quench(self):
        """Switch the lamps off."""
        print("switching lamps off")
        lamps(0)

    def extended(self):
        return GPIO.input(pin_extended)

    def retracted(self):
        return GPIO.input(pin_retracted)

    def extend(self):
        """Slide the keyboard drawer out."""
        if self.keyboard_status == 'extended':
            print("keyboard already extended")
        else:
            if self.keyboard_status != 'extending':
                self.moving_steps = 0
            power_on()
            self.keyboard_status = 'extending'
            GPIO.output(pin_motor_a, GPIO.LOW)
            GPIO.output(pin_motor_b, GPIO.HIGH)

    def retract(self):
        """Slide the keyboard drawer back in."""
        if self.keyboard_status == 'retracted':
            print("keyboard already retracted")
        else:
            if self.keyboard_status != 'retracting':
                self.moving_steps = 0
            power_on()
            self.keyboard_status = 'retracting'
            GPIO.output(pin_motor_b, GPIO.LOW)
            GPIO.output(pin_motor_a, GPIO.HIGH)

    def pir_actions(self):
        pass

    def porch_pir_actions(self):
        pass

    def say(self, text):
        """Pass the text to a TTS system.
        That goes via this module so we can control the speaker power switch."""
        GPIO.output(pin_speaker, GPIO.HIGH)
        # TODO: first check there's no existing process
        # TODO: maybe we should have a sound queue?
        self.speech_process = subprocess.Popen(
            # TODO: fill in params
        )

    def play(self, music_filename):
        """Pass a music file to a player.
        That goes via this module so we can control the speaker power switch."""
        GPIO.output(pin_speaker, GPIO.HIGH)
        # TODO: start the player process asynchronously, switch speaker off at end
        self.music_process = subprocess.Popen(
            # TODO: fill in params
        )

    def photo(self):
        """Capture a photo and store it with a timestamp in the filename."""
        image_filename = os.path.join(self.config['camera']['directory'],
                                      datetime.datetime.now().isoformat()+".jpg")
        print("taking photo into", image_filename)
        self.camera.capture(image_filename)
        # todo: compare with previous photo in series, and drop any that are very nearly the same

    def step(self):
        """Perform one step of any active operations.
        Returns whether there's anything going on that needs
        the event loop to run fast."""

        for lamp in self._lamps:
            lamp.step()

        stepmax = self.config['delays']['step_max']
        if self.keyboard_status == 'retracting':
            if self.retracted() or self.moving_steps > stepmax:
                self.keyboard_status = 'retracted'
                GPIO.output(pin_motor_b, GPIO.LOW)
                GPIO.output(pin_motor_a, GPIO.LOW)
            else:
                self.moving_steps += 1
        elif self.keyboard_status == 'extending':
            if self.extended() or self.moving_steps > stepmax:
                self.keyboard_status = 'extended'
                GPIO.output(pin_motor_b, GPIO.LOW)
                GPIO.output(pin_motor_a, GPIO.LOW)
            else:
                self.moving_steps += 1

        if self.music_process:
            process_result = self.music_process.poll()
            if process_result:
                if self.speech_process is None:
                    GPIO.output(pin_speaker, GPIO.LOW)
                self.music_process = None

        if self.speech_process:
            process_result = self.speech_process.poll()
            if process_result:
                GPIO.output(pin_speaker, GPIO.LOW)
                self.speech_process = None

        # TODO: read the temperature from pin_temperature into self.temperature

        if GPIO.input(pin_pir):
            if self.pir_seen_at:
                if self.pir_seen_at + self.config['delays']['pir_delay'] < time.time():
                    self.pir_actions()
            else:
                self.pir_seen_at = time.time()
        else:
            self.pir_seen_at = 0

        if GPIO.input(pin_porch_pir):
            if self.porch_pir_seen_at:
                if self.porch_pir_seen_at + self.config['delays']['porch_pir_delay'] < time.time():
                    self.porch_pir_actions()
            else:
                self.porch_pir_seen_at = time.time()
        else:
            self.porch_pir_seen_at = 0

        return (self.keyboard_status in ('retracting', 'extending')
                    or any(lamp.changing() for lamp in self._lamps))

    def report(self):
        """Output the status of the noticeboard hardware."""
        PIR_active = GPIO.input(pin_pir)
        keyboard_extended = self.extended()
        keyboard_retracted = self.retracted()
        print("12V power on:", self.power)
        print("PIR:", PIR_active)
        print("Keyboard status:", self.keyboard_status)

    def at_home(self):
        """Tell the system I am at home."""
        self.user_status = 'home'

    def away(self):
        """Tell the system I am away."""
        self.user_status = 'away'

    def auto(self):
        """Tell the system I'm not telling it whether I'm at home."""
        self.user_status = 'automatic'

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

def quit():
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
    "auto",
    "away",
    "extend",
    "help",
    "home",
    "off",
    "on",
    "photo",
    "play",
    "quench",
    "quit",
    "report",
    "retract",
    "say",
    "shine"
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

    controller = NoticeBoardHardware(config)

    print("noticeboard hardware controller started")
    while running:
        active = controller.step()
        # if we're stepping through an activity, ignore commands for now:
        if active:
            time.sleep(self.config['delays']['motor'])
        else:
            ready, _, _ = select.select([sys.stdin], [], [], main_loop_delay)
            if sys.stdin in ready:
                command = shlex.parse(sys.stdin.readline().strip())
                if command[0] in actions:
                    getattr(controller, command)(command)
                else:
                    print('(error "Unknown noticeboard command" ', command, ')')

        # if photographing:
        #     take_photo()
        #     if datetime.datetime.now() >= photographing:
        #         photographing = False
    print("noticeboard hardware controller stopped")

if __name__ == "__main__":
    main()
