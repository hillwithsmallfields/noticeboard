class fakePWM(object):

    def __init__(self, rate):
        self.rate = rate
        self.duty = 0

    def ChangeDutyCycle(self, duty):
        self.duty = duty

    def stop(self):
        self.duty = 0

class fakeGPIO(object):

    def __init__(self):
        self.direction = fakeGPIO.IN
        self.value = fakeGPIO.LOW

    def PWM(self, rate):
        return fakePWM(rate)

    def setup(self, direction, initial=LOW):
        self.direction = direction
        self.value = initial

    OUT = 1
    IN = 0
    LOW = 0
    HIGH = 1
