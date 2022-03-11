
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
PIN_RETRACT    = 23 # 16
PIN_EXTEND     = 24 # 17
PIN_MOTOR_2_A  = 27 # 13
PIN_MOTOR_2_B  = 22 # 15
PIN_LAMP_LEFT  = 12 # 32
PIN_LAMP_RIGHT = 13 # 33
PIN_PORCH_LAMP =  2 # 3
PIN_FANS       =  6 # 31

INPUT_PINS_BY_NAME = {
    'pir': (PIN_PIR, 11, "5V: IC2p2; 3V3: IC2p3"),
    'retracted': (PIN_RETRACTED, 23, "5V: IC2p12; 3V3: IC2p11"),
    'extended': (PIN_EXTENDED, 29, "5V: IC2p9; 3V3: IC2p8"),
    'porch_pir': (PIN_PORCH_PIR, 35, "5V: IC2p5; 3V3: IC2p6"),
    'temperature': (PIN_TEMPERATURE, 7, "GPIO p7")
}

OUTPUT_PINS_BY_NAME = {
    'psu': (PIN_PSU, 24, "3V3: IC3p12; 5V: IC3p11"),
    'speaker': (PIN_SPEAKER, 26, "3V3: IC3p9; 5V: IC3p8"),
    'retract': (PIN_RETRACT, 16, "3V3: IC3p2; 5V: IC3p3"),
    'extend': (PIN_EXTEND, 17, "3V3: IC3p5: 5V: IC3p6"),
    'spare_a': (PIN_MOTOR_2_A, 27, "3V3: IC1p2; 5V: IC1p3"),
    'spare_b': (PIN_MOTOR_2_B, 22, "3V3: IC1p5; 5V: IC1p6"),
    'lamp_left': (PIN_LAMP_LEFT, 32, "3V3: IC4p2; 5V: IC4p3"),
    'lamp_right': (PIN_LAMP_RIGHT, 33, "3V3: IC4p5; 5V: IC4p6"),
    'porch_lamp': (PIN_PORCH_LAMP, 3, "3V3: IC1p12; 5V: IC1p11")
}
