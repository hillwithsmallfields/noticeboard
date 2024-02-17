from pathlib import Path

import cmd
import datetime
import sched
import subprocess
import time

from collections import defaultdict

import RPi.GPIO as GPIO
import picamera

import pins
from lamp import Lamp

# General support for the noticeboard hardware

# see https://forums.raspberrypi.com/viewtopic.php?t=278003 for driving the lamps
# see https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20 for the temperature sensor

class NoticeBoardHardware(cmd.Cmd):

    pass

    def __init__(self, config, scheduler, expected_at_home_times):
        self.config = config
        self.scheduler = scheduler or sched.scheduler(time.time, time.sleep)
        self.expected_at_home_times = expected_at_home_times
        self.v12_is_on = False
        self.brightness = 0
        self.quench_scheduled = False
        self.keyboard_status = 'unknown'
        self.moving_steps = 0

        self.pir_already_on = False
        self.pir_on_for = 0
        self.pir_off_for = 0
        self.pir_on_actions = defaultdict(list)
        self.pir_off_actions = defaultdict(list)

        self.music_process = None
        self.speech_process = None

        self.user_status_automatic = False
        self.user_status = 'unknown'

        self.temperature = None

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pins.PIN_PIR, GPIO.IN)
        # GPIO.setup(pins.PIN_PORCH_PIR, GPIO.IN)
        GPIO.setup(pins.PIN_RETRACTED, GPIO.IN)
        GPIO.setup(pins.PIN_TEMPERATURE, GPIO.IN)
        GPIO.setup(pins.PIN_EXTENDED, GPIO.IN)
        GPIO.setup(pins.PIN_PSU, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_SPEAKER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_RETRACT, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_EXTEND, GPIO.OUT, initial=GPIO.LOW)
        # GPIO.setup(pins.PIN_PORCH_LAMP, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_LAMP_LEFT, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_LAMP_RIGHT, GPIO.OUT, initial=GPIO.LOW)
        self._lamps = [Lamp(pins.PIN_LAMP_LEFT), Lamp(pins.PIN_LAMP_RIGHT)]
        self.camera = picamera.PiCamera()

    def do_on(self, arg=None):
        """Switch the 12V power on."""
        self.power(True)
        return False

    def do_off(self, arg=None):
        """Switch the 12V power off."""
        self.power(False)

    def do_speaker(self, arg=None):
        self.sound(True)
        return False

    def do_quiet(self, arg=None):
        self.sound(False)
        return False

    def do_shine(self, arg=None):
        """Switch the lamps on."""
        self.lamps(100)
        return False

    def do_quench(self, arg=None):
        """Switch the lamps off."""
        self.lamps(0)
        return False

    def do_extend(self, arg):
        """Slide the keyboard drawer out."""
        if self.keyboard_status == 'extended':
            print('(message "keyboard already extended")')
        else:
            if self.keyboard_status != 'extending':
                self.moving_steps = 0
            self.power(True)
            self.keyboard_status = 'extending'
            print('(message "starting to extend keyboard tray")')
            GPIO.output(pins.PIN_RETRACT, GPIO.LOW)
            GPIO.output(pins.PIN_EXTEND, GPIO.HIGH)
        return False

    def do_retract(self, arg):
        """Slide the keyboard drawer back in."""
        if self.keyboard_status == 'retracted':
            print('(message "keyboard already retracted")')
        else:
            if self.keyboard_status != 'retracting':
                self.moving_steps = 0
            self.power(True)
            self.keyboard_status = 'retracting'
            print('(message "starting to retract keyboard tray")')
            GPIO.output(pins.PIN_EXTEND, GPIO.LOW)
            GPIO.output(pins.PIN_RETRACT, GPIO.HIGH)
        return False

    def do_report(self, arg):
        """Output the status of the noticeboard hardware."""
        PIR_active = GPIO.input(pins.PIN_PIR)
        keyboard_extended = self.extended()
        keyboard_retracted = self.retracted()
        print('(message "12V power on: %s")' % self.v12_is_on)
        print('(message "PIR: %s")' % PIR_active)
        print('(message "Keyboard status: %s")' % self.keyboard_status)
        return False

    def do_at_home(self, arg):
        """Tell the system I am at home."""
        self.user_status = 'home'
        self.user_status_automatic = False
        return False

    def do_away(self, arg):
        """Tell the system I am away."""
        self.user_status = 'away'
        self.user_status_automatic = False
        return False

    def do_auto(self, arg):
        """Tell the system I'm not telling it whether I'm at home."""
        self.user_status_automatic = True
        return False

    def do_quit(self, arg):
        return True

    def delayed(self, action, delay):
        self.scheduler.enter(delay=delay, priority=2, action=action, argument=[self])

    def do_say(self, text):
        """Pass the text to a TTS system.
        That goes via this module so we can control the speaker power switch."""
        if self.speech_process:
            self.speech_process.wait() # wait for the old one to finish
        self.sound(True)
        self.speech_process=subprocess.Popen(["espeak", text])
        return False

    def do_play(self, music_filename, begin=None, end=None):
        """Pass a music file to a player.
        That goes via this module so we can control the speaker power switch."""
        if self.music_process:
            self.music_process.wait() # wait for the old one to finish
        self.sound(True)
        if music_filename.endswith(".ogg"):
            self.music_process=subprocess.Popen(["ogg123"]
                                                + (["-k", str(begin)] if begin else [])
                                                + (["-K", str(end)] if end else [])
                                                + [music_filename],
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL)
        elif music_filename.endswith(".ly"):
            midi_file = Path(music_filename).with_suffix(".midi")
            if not midi_file.exists():
                subprocess.run(["lilypond", music_filename],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            self.music_process=subprocess.Popen(["timidity", midi_file],
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL)
        elif music_filename.endswith(".midi"):
            self.music_process=subprocess.Popen(["timidity", music_filename],
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL)
        return False

    def do_photo(self, arg):
        """Capture a photo and store it with a timestamp in the filename."""
        image_filename = os.path.join(self.config['camera']['directory'],
                                      datetime.datetime.now().isoformat()+".jpg")
        print('(message "taking photo into %s")' % image_filename)
        self.camera.capture(image_filename)
        return False
        # todo: compare with previous photo in series, and drop any that are very nearly the same
        return False

    def power(self, on):
        GPIO.output(pins.PIN_PSU, GPIO.LOW if on else GPIO.HIGH)
        self.v12_is_on = on

    def sound(self, is_on):
        GPIO.output(pins.PIN_SPEAKER, GPIO.LOW if is_on else GPIO.HIGH)

    def lamps(self, brightness):
        self.brightness = float(brightness)
        if self.brightness > 0:
            self.power(True)
        for lamp in self._lamps:
            lamp.set(self.brightness)

    def extended(self):
        return not GPIO.input(pins.PIN_EXTENDED)

    def retracted(self):
        return not GPIO.input(pins.PIN_RETRACTED)

    def check_temperature(self):
        # TODO: read the temperature from pins.PIN_TEMPERATURE into self.temperature
        pass

    def check_pir(self):
        if GPIO.input(pins.PIN_PIR):
            if self.pir_already_on:
                self.pir_on_for += 1
                if self.pir_on_for in self.pir_on_actions:
                    for command in self.pir_on_actions[self.pir_on_for]:
                        self.onecmd(command)
            else:
                self.pir_off_for = 0
            self.pir_already_on = True
        else:
            if self.pir_already_on:
                self.pir_on_for = 0
            else:
                self.pir_off_for += 1
                if self.pir_off_for in self.pir_off_actions:
                    for command in self.pir_off_actions[self.pir_off_for]:
                        self.onecmd(command)
            self.pir_already_on = False

    def add_pir_on_action(self, delay, action):
        """Arrange a command to be run some number of steps after the PIR detector goes on."""
        self.pir_on_actions[delay].append(action)

    def add_pir_off_action(self, delay, action):
        """Arrange a command to be run some number of steps after the PIR detector goes off."""
        self.pir_off_actions[delay].append(action)

    def keyboard_step(self, stepmax):
        if self.keyboard_status == 'retracting':
            if self.retracted() or self.moving_steps > stepmax:
                print('(message "stopping retracting %d %d")' % (self.moving_steps, stepmax))
                self.keyboard_status = 'retracted'
                GPIO.output(pins.PIN_EXTEND, GPIO.LOW)
                GPIO.output(pins.PIN_RETRACT, GPIO.LOW)
                self.moving_steps = 0
            else:
                self.moving_steps += 1
        elif self.keyboard_status == 'extending':
            if self.extended() or self.moving_steps > stepmax:
                print('(message "stopping extending %d %d")' % (self.moving_steps, stepmax))
                self.keyboard_status = 'extended'
                GPIO.output(pins.PIN_EXTEND, GPIO.LOW)
                GPIO.output(pins.PIN_RETRACT, GPIO.LOW)
                self.moving_steps = 0
            else:
                self.moving_steps += 1

    def check_for_sounds_finishing(self):
        if self.speech_process and self.speech_process.poll() is not None: # non-None if it has exited
            self.speech_process = None

        if self.music_process and self.music_process.poll() is not None: # non-None if it has exited
            self.music_process = None

        if self.music_process is None and self.speech_process is None:
            self.do_quiet()

    def step(self):
        """Perform one step of any active operations.
        Returns whether there's anything going on that needs
        the event loop to run fast."""

        for lamp in self._lamps:
            lamp.step()

        self.keyboard_step(self.config['delays']['step_max'])

        self.check_for_sounds_finishing()

        self.check_temperature()

        self.check_pir()

        return (self.keyboard_status in ('retracting', 'extending')
                    or any(lamp.changing() for lamp in self._lamps))
