# we may be running on a non-Pi while developing this program
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("Error importing RPi.GPIO!")
    import fakeGPIO as GPIO

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
