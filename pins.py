
# Pin          BCM  Board
# input pins        #
PIN_PIR        = 17 # 11
PIN_RETRACTED  = 11 # 23
PIN_EXTENDED   =  5 # 29
PIN_PORCH_PIR  = 19 # 35
PIN_TEMPERATURE = 4 # 7
# output pins       #
PIN_PSU        =  8 # 24
PIN_SPEAKER    =  7 # 26
PIN_MOTOR_A    = 23 # 16
PIN_MOTOR_B    = 24 # 17
PIN_LAMP_LEFT  = 12 # 32
PIN_LAMP_RIGHT = 13 # 33
PIN_PORCH_LAMP =  2 # 3

INPUT_PINS_BY_NAME = {
    'pir': (PIN_PIR, 11),
    'retracted': (PIN_RETRACTED, 23),
    'extended': (PIN_EXTENDED, 29),
    'porch_pir': (PIN_PORCH_PIR, 35),
    'temperature': (PIN_TEMPERATURE, 7)
}

OUTPUT_PINS_BY_NAME = {
    'psu': (PIN_PSU, 24),
    'speaker': (PIN_SPEAKER, 26),
    'motor_a': (PIN_MOTOR_A, 16),
    'motor_b': (PIN_MOTOR_B, 17),
    'lamp_left': (PIN_LAMP_LEFT, 32),
    'lamp_right': (PIN_LAMP_RIGHT, 33),
    'porch_lamp': (PIN_PORCH_LAMP, 3)
}
