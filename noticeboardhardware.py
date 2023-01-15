from pathlib import Path

import RPi.GPIO as GPIO
import picamera

import pins
from lamp import Lamp

# General support for the noticeboard hardware

# see https://forums.raspberrypi.com/viewtopic.php?t=278003 for driving the lamps
# see https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20 for the temperature sensor

class NoticeBoardHardware(object):

    pass

    def __init__(self, config):
        self.config = config
        self.power = False
        self._lamps = [Lamp(pins.PIN_LAMP_LEFT), Lamp(pins.PIN_LAMP_RIGHT)]
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
        GPIO.setup(pins.PIN_PIR, GPIO.IN)
        GPIO.setup(pins.PIN_PORCH_PIR, GPIO.IN)
        GPIO.setup(pins.PIN_RETRACTED, GPIO.IN)
        GPIO.setup(pins.PIN_TEMPERATURE, GPIO.IN)
        GPIO.setup(pins.PIN_EXTENDED, GPIO.IN)
        GPIO.setup(pins.PIN_PSU, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_SPEAKER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_RETRACT, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_EXTEND, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_PORCH_LAMP, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_LAMP_LEFT, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins.PIN_LAMP_RIGHT, GPIO.OUT, initial=GPIO.LOW)

    def on(self):
        """Switch the 12V power on."""
        print("switching 12V power on")
        GPIO.output(pins.PIN_PSU, GPIO.LOW)
        self.power = True

    def off(self):
        """Switch the 12V power off."""
        print("switching 12V power off")
        GPIO.output(pins.PIN_PSU, GPIO.HIGH)
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
        return GPIO.input(pins.PIN_EXTENDED)

    def retracted(self):
        return GPIO.input(pins.PIN_RETRACTED)

    def extend(self):
        """Slide the keyboard drawer out."""
        if self.keyboard_status == 'extended':
            print("keyboard already extended")
        else:
            if self.keyboard_status != 'extending':
                self.moving_steps = 0
            power_on()
            self.keyboard_status = 'extending'
            GPIO.output(pins.PIN_RETRACT, GPIO.LOW)
            GPIO.output(pins.PIN_EXTEND, GPIO.HIGH)

    def retract(self):
        """Slide the keyboard drawer back in."""
        if self.keyboard_status == 'retracted':
            print("keyboard already retracted")
        else:
            if self.keyboard_status != 'retracting':
                self.moving_steps = 0
            power_on()
            self.keyboard_status = 'retracting'
            GPIO.output(pins.PIN_EXTEND, GPIO.LOW)
            GPIO.output(pins.PIN_RETRACT, GPIO.HIGH)

    def pir_actions(self):
        pass

    def porch_pir_actions(self):
        pass

    def say(self, text):
        """Pass the text to a TTS system.
        That goes via this module so we can control the speaker power switch."""
        GPIO.output(pins.PIN_SPEAKER, GPIO.LOW)
        # TODO: first check there's no existing process
        # TODO: maybe we should have a sound queue?
        subprocess.run(["espeak", text])
        GPIO.output(pins.PIN_SPEAKER, GPIO.HIGH)

    def play(self, music_filename, begin=None, end=None):
        """Pass a music file to a player.
        That goes via this module so we can control the speaker power switch."""
        GPIO.output(pins.PIN_SPEAKER, GPIO.LOW)
        # TODO: start the player process asynchronously, switch speaker off at end
        if music_filename.endswith(".ogg"):
            subprocess.run(["ogg123"]
                           + (["-k", str(begin)] if begin else [])
                           + (["-K", str(end)] if end else [])
                           + [music_filename])
        elif music_filename.endswith(".ly"):
            midi_file = Path(music_filename).with_suffix(".midi")
            if not midi_file.exists():
                subprocess.run(["lilypond", music_filename])
            subprocess.run((["timidity"] + [midi_file]))
        elif music_filename.endswith(".midi"):
            subprocess.run((["timidity"] + [music_filename]))
        GPIO.output(pins.PIN_SPEAKER, GPIO.HIGH)

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
                GPIO.output(pins.PIN_EXTEND, GPIO.LOW)
                GPIO.output(pins.PIN_RETRACT, GPIO.LOW)
            else:
                self.moving_steps += 1
        elif self.keyboard_status == 'extending':
            if self.extended() or self.moving_steps > stepmax:
                self.keyboard_status = 'extended'
                GPIO.output(pins.PIN_EXTEND, GPIO.LOW)
                GPIO.output(pins.PIN_RETRACT, GPIO.LOW)
            else:
                self.moving_steps += 1

        if self.music_process:
            process_result = self.music_process.poll()
            if process_result:
                if self.speech_process is None:
                    GPIO.output(pins.PIN_SPEAKER, GPIO.LOW)
                self.music_process = None

        if self.speech_process:
            process_result = self.speech_process.poll()
            if process_result:
                GPIO.output(pins.PIN_SPEAKER, GPIO.LOW)
                self.speech_process = None

        # TODO: read the temperature from pins.PIN_TEMPERATURE into self.temperature

        if GPIO.input(pins.PIN_PIR):
            if self.pir_seen_at:
                if self.pir_seen_at + self.config['delays']['pir_delay'] < time.time():
                    self.pir_actions()
            else:
                self.pir_seen_at = time.time()
        else:
            self.pir_seen_at = 0

        if GPIO.input(pins.PIN_PORCH_PIR):
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
        PIR_active = GPIO.input(pins.PIN_PIR)
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
