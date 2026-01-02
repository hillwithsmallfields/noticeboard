from pathlib import Path

import cmd
import datetime
import os
import re
import sched
import shlex
import subprocess
import sys
import time

from collections import defaultdict

import RPi.GPIO as GPIO
import picamera

import pins
from lamp import Lamp

# General support for the noticeboard hardware

# see https://forums.raspberrypi.com/viewtopic.php?t=278003 for driving the lamps
# see https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20 for the temperature sensor

COUNTDOWN_START = 3

CLIPS_DIR = "/mnt/hdd0/motion/clips"

def oggplay(music_filename, begin=None, end=None):
    subprocess.Popen(["ogg123"]
                     + (["-k", str(begin)] if begin else [])
                     + (["-K", str(end)] if end else [])
                     + [music_filename],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)

DEFAULT_MUSIC_DIRECTORY = os.path.expanduser("~/Music")

music_files = {
}

def get_music_files():
    if not music_files:
        def get_music_files_in_dir(directory):
            for raw in os.listdir(directory):
                if raw.startswith('.'):
                    continue
                name = os.path.join(directory, raw)
                if os.path.isfile(name) and name.endswith('.ogg') and 'conflict' not in name:
                    base = os.path.splitext(raw)[0].lower().replace('_', ' ')
                    if (m := re.match("[0-9]+[._-](.+)", base)):
                        base = m.group(1)
                    music_files[base] = name
                elif os.path.isdir(name):
                    get_music_files_in_dir(name)
        get_music_files_in_dir(DEFAULT_MUSIC_DIRECTORY)

def filenames_for_music(partial_filename):
    get_music_files()
    partial_filename = partial_filename.lower().replace('_', ' ')
    if partial_filename in music_files:
        return music_files[partial_filename]
    else:
        possibles = set(music_files.keys())
        for word in partial_filename.split(' '):
            possibles = {name for name in possibles if word in name}
        print(possibles)
        return list(possibles)[0]

class NoticeBoardHardware(cmd.Cmd):

    pass

    def __init__(self,
                 config,
                 scheduler,
                 expected_at_home_times,
                 speech_engine="espeak"):
        self.config = config
        self.scheduler = scheduler or sched.scheduler(time.time, time.sleep)
        self.expected_at_home_times = expected_at_home_times
        self.speech_engine = speech_engine
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
        self.speaker_off_countdown = COUNTDOWN_START

        self.user_status_automatic = False
        self.user_status = 'unknown'

        self.temperature = None

        self.config_updates = {}

        self.stdout = sys.stdout # needed for error messages by cmd

        self.logstream = open(os.path.expanduser("~/noticeboard.log"), 'a')

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

    def log(self, message, *message_data):
        log_text = datetime.datetime.now().isoformat() + ": " + (message % message_data)
        if self.logstream:
            self.logstream.write(log_text + "\n")
            self.logstream.flush()
        else:
            print(log_text)

    def do_on(self, arg=None):
        """Switch the 12V power on."""
        self.power(True)
        return False

    def do_off(self, arg=None):
        """Switch the 12V power off."""
        self.power(False)

    def do_speaker(self, arg=None):
        """Switch the speaker power on."""
        self.sound(True)
        return False

    def do_quiet(self, arg=None):
        """Switch the speaker power off."""
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
            pass # print('(message "keyboard already extended")')
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
            pass # print('(message "keyboard already retracted")')
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
        """Output the status of the noticeboard system."""
        PIR_active = GPIO.input(pins.PIN_PIR)
        keyboard_extended = self.extended()
        keyboard_retracted = self.retracted()
        print('(message "12V power on: %s")' % self.v12_is_on)
        print('(message "PIR: %s")' % PIR_active)
        print('(message "Keyboard status: %s")' % self.keyboard_status)
        print('(message "Music process: %s")' % self.music_process)
        print('(message "Speech process: %s")' % self.speech_process)
        print('(message "Countdown to switching speaker off: %d")' % self.speaker_off_countdown)
        print('(message "Time on server: %s")' % datetime.datetime.now().isoformat())
        if os.path.isdir(CLIPS_DIR):
            print('(message "Camera clips: %d bytes")' % int(subprocess.run(["du", "-b", CLIPS_DIR], capture_output=True)
                                                             .stdout
                                                             .split(b'\t')[0]))
            clips = sorted(n[13:] for n in os.listdir(CLIPS_DIR))
            if clips:
                print('(message "Most recent camera clip at: %s")' % clips[-1].split('.')[0])
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
        """Tell the event loop to finish."""
        self.logstream.close()
        self.logstream = None
        return True

    def do_config(self, arg):
        """Add a change to the config, for the event loop to update the config from."""
        argparts = shlex.split(arg)
        target = self.config_updates
        for level in argparts[:-2]:
            if level not in target:
                new_level = dict()
                target[level] = new_level
                target = new_level
        name = argparts[-2]
        value = argparts[-1]
        try:
            target[name] = int(value)
        except ValueError:
            try:
                target[name] = float(value)
            except ValueError:
                match value:
                    case 'True':
                        target[name] = True
                    case 'False':
                        target[name] = False
                    case other:
                        target[name] = value

    def do_say(self, text):
        """Pass the text to a TTS system.
        That goes via this module so we can control the speaker power switch."""
        if self.speech_process:
            self.speech_process.wait() # wait for the old one to finish
        self.sound(True)
        self.speech_process=subprocess.Popen([self.speech_engine, text])
        return False

    def do_play(self, music_filename, begin=None, end=None):
        """Pass a music file to a player.
        That goes via this module so we can control the speaker power switch."""
        if self.music_process:
            self.log("waiting for old music process to finish")
            self.music_process.wait() # wait for the old one to finish
        self.sound(True)
        if music_filename.endswith(".ogg"):
            self.log("playing ogg file %s", music_filename)
            self.music_process=oggplay(music_filename, begin, end)
        elif music_filename.endswith(".ly"):
            self.log("playing lilypond file %s", music_filename)
            midi_file = Path(music_filename).with_suffix(".midi")
            if not midi_file.exists():
                self.log("converting lilypond file %s to midi file %s", music_filename, midi_file)
                subprocess.run(["lilypond", music_filename],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            self.music_process=subprocess.Popen(["timidity", midi_file],
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL)
        elif music_filename.endswith(".midi"):
            self.log("playing midi file %s", music_filename)
            self.music_process=subprocess.Popen(["timidity", music_filename],
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL)
        else:
            music_files = filenames_for_music(music_filename)
            for music_file in music_files:
                self.music_process=oggplay(music_file)
                if self.music_process:
                    # TODO: non-blocking queuing system
                    self.log("waiting for old music process to finish when playing multiple tracks consecutively")
                    self.music_process.wait() # wait for the old one to finish
        return False

    def do_list_tracks(self, arg):
        """List music tracks."""
        get_music_files()
        for track in sorted([track for track in music_files.keys()]):
            if arg in track:
                print(track)

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
        """Switch the 12V PSU on or off."""
        GPIO.output(pins.PIN_PSU, GPIO.LOW if on else GPIO.HIGH)
        self.v12_is_on = on

    def sound(self, is_on):
        """Switch the active speaker power on or off."""
        GPIO.output(pins.PIN_SPEAKER, GPIO.LOW if is_on else GPIO.HIGH)

    def lamps(self, brightness):
        """Set the brightness of both lamps.
        The actual brightness will be adjusted in several steps."""
        self.brightness = float(brightness)
        if self.brightness > 0:
            self.power(True)
        for lamp in self._lamps:
            lamp.set(self.brightness)

    def extended(self):
        """Return whether the keyboard tray is extended, according to the limit switch."""
        return GPIO.input(pins.PIN_EXTENDED)

    def retracted(self):
        """Return whether the keyboard tray is retracted, according to the limit switch."""
        return GPIO.input(pins.PIN_RETRACTED)

    def check_temperature(self):
        # TODO: read the temperature from pins.PIN_TEMPERATURE into self.temperature
        pass

    def check_pir(self):
        """Check for state changes of the PIR detector."""
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
        """Operate the keyboard tray motor controller according to the required and actual positions."""
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
        """Check for any sound processes having finished.
        If they have all finished, switch the active speaker power off."""
        if self.speech_process and self.speech_process.poll() is not None: # non-None if it has exited
            self.log("speech process exited")
            self.speaker_off_countdown = COUNTDOWN_START
            self.speech_process = None

        if self.music_process and self.music_process.poll() is not None: # non-None if it has exited
            self.log("music process exited")
            self.speaker_off_countdown = COUNTDOWN_START
            self.music_process = None

        if self.music_process is None and self.speech_process is None:
            if self.speaker_off_countdown > 0:
                self.speaker_off_countdown -= 1
                self.log("countdown to switching speaker off: %d", self.speaker_off_countdown)
                if self.speaker_off_countdown == 0:
                    self.log("switching speaker off")
                    self.do_quiet()

    def step(self, active):
        """Perform one step of any active operations.
        Returns whether there's anything going on that needs
        the event loop to run fast."""

        for lamp in self._lamps:
            lamp.step()

        self.keyboard_step(self.config['delays']['step_max'])

        if not active:
            self.check_for_sounds_finishing()
            self.check_temperature()
            self.check_pir()

        return (self.keyboard_status in ('retracting', 'extending')
                or any(lamp.changing() for lamp in self._lamps))
