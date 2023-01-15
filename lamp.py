import RPi.GPIO as GPIO

class Lamp(object):

    pass

    def __init__(self, pin):
        self.gpio = pin
        self.target = 0
        self.current = 0
        print("making Lamp with gpio", self.gpio)
        self.pwm = GPIO.PWM(self.gpio, 1000, 42)
        GPIO.setup(self.gpio, GPIO.OUT, initial=GPIO.LOW)

    def set(self, brightness):
        self.target = int(brightness)

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
