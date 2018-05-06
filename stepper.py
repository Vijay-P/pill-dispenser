#!/usr/bin/env python

# Native packages
import time
# External pakages
from nanpy import SerialManager, ArduinoApi, Servo

# TIMING AND OTHER CONSTANTS
FULL_ROTATION = 200
STEP_DELAY = 0.001
GATE_OPEN = 137
GATE_CLOSED = 155
PILL_DETECT = 35
SHAKE_DEL = 0.01
SLEEP_TIME = 0.05

# ARDUINO PINS
# PINS 1 and 11 broken
PINS = {
    'direction': 4,
    'step': 5,
    'sleep': 6,
    'dispense': 3,
    'reset': 2,
    'photocell': 5,  # A5
    'limit': 7,
    'ms1': 9,
    'ms2': 10,
    'ms3': 12,
    'gate': 13
}


def toggle(a):
    time.sleep(SLEEP_TIME)  # .75
    if a.digitalRead(PINS['sleep']) == a.HIGH:
        print("Sleeping")
        a.digitalWrite(PINS['sleep'], a.LOW)
    elif a.digitalRead(PINS['sleep']) == a.LOW:
        print("Awake")
        a.digitalWrite(PINS['sleep'], a.HIGH)


def translate(a, ccw, steps):
    if ccw:
        a.digitalWrite(PINS['direction'], a.HIGH)
    else:
        a.digitalWrite(PINS['direction'], a.LOW)
    for _ in range(steps):
        a.digitalWrite(PINS['step'], a.LOW)
        time.sleep(STEP_DELAY)
        a.digitalWrite(PINS['step'], a.HIGH)
        time.sleep(STEP_DELAY)


def shake(a, iterations):
    toggle(a)
    for _ in range(iterations):
        translate(a, True, 1)
        time.sleep(SHAKE_DEL)
        translate(a, False, 1)
        time.sleep(SHAKE_DEL)
    translate(a, True, 1)
    toggle(a)


def close_gate(servo):
    servo.write(GATE_CLOSED)


def open_gate(servo):
    servo.write(GATE_OPEN)


def dispense(a, servo):
    try:
        open_gate(servo)
        time.sleep(SLEEP_TIME)
        shake(a, 12)
        close_gate(servo)
        stime = time.time()
        a.digitalWrite(PINS['dispense'], a.HIGH)
        print("DISPENSING")
        photocell_reading = sum([a.analogRead(PINS['photocell']) for _ in range(3)]) / 3
        new_reading = photocell_reading
        numshakes = 14
        while abs(photocell_reading - new_reading) < PILL_DETECT:
            if abs(time.time() - stime) > 5:
                a.digitalWrite(PINS['dispense'], a.LOW)
                open_gate(servo)
                time.sleep(SLEEP_TIME)
                shake(a, numshakes)
                numshakes += 7
                close_gate(servo)
                time.sleep(SLEEP_TIME)
                a.digitalWrite(PINS['dispense'], a.HIGH)
                stime = time.time()
            new_reading = a.analogRead(PINS['photocell'])
    except Exception as exc:
        print("ERROR", exc)
    finally:
        a.digitalWrite(PINS['dispense'], a.LOW)


def home(a):
    return a.digitalRead(PINS['limit']) == 1


def reset_home(a):
    translate(a, True, 200 / 6)
    while 1:
        translate(a, True, 1)
        if home(a):
            time.sleep(SLEEP_TIME)  # .25
            translate(a, False, 4)
            print("home")
            break


def navigate(a, cylinder):
    toggle(a)
    reset_home(a)
    for _ in range(cylinder):
        translate(a, False, 200 / 6)
    toggle(a)


def reload(a, cylinder):
    if cylinder < 3:
        cylinder += 3
    else:
        cylinder %= 3
    navigate(a, cylinder)
    translate(a, False, 7)


def pinmode(a):
    # PIN SETUP
    a.pinMode(PINS['step'], a.OUTPUT)  # Step
    a.pinMode(PINS['direction'], a.OUTPUT)  # direction
    a.pinMode(PINS['dispense'], a.OUTPUT)
    a.pinMode(PINS['reset'], a.OUTPUT)
    a.pinMode(PINS['sleep'], a.OUTPUT)
    a.pinMode(PINS['limit'], a.INPUT)
    a.pinMode(PINS['ms1'], a.OUTPUT)
    a.pinMode(PINS['ms2'], a.OUTPUT)
    a.pinMode(PINS['ms3'], a.OUTPUT)


def init(a, servo):
    # INITIAL STATE
    a.digitalWrite(PINS['dispense'], a.LOW)
    a.digitalWrite(PINS['step'], a.HIGH)
    a.digitalWrite(PINS['direction'], a.HIGH)
    a.digitalWrite(PINS['sleep'], a.LOW)
    a.digitalWrite(PINS['reset'], a.HIGH)
    a.digitalWrite(PINS['ms1'], a.LOW)
    a.digitalWrite(PINS['ms2'], a.LOW)
    a.digitalWrite(PINS['ms3'], a.LOW)
    close_gate(servo)

if __name__ == '__main__':
    # Nanpy Setup
    CONNECTION = SerialManager(device='/dev/ttyUSB0')
    A = ArduinoApi(connection=CONNECTION)
    SERVO = Servo(PINS['gate'])
    pinmode(A)
    init(A, SERVO)
    reload(a, 0)
    A.digitalWrite(PINS['sleep'], A.LOW)
