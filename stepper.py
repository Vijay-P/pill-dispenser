#!/usr/bin/env python

import sys
import time
import random
import serial

from nanpy import SerialManager, ArduinoApi, Servo

# PINS
direction = 4
step = 5
sleep = 6
disp_pin = 3
reset = 2
photocell = 5  # A5
limit = 7
ms1 = 9
ms2 = 10
ms3 = 12
gate = 13
# PIN 1 broken

FULL_ROTATION = 200
STEP_DELAY = 0.001
GATE_OPEN = 120
GATE_CLOSED = 140


def step_mode():
    pass


def toggle(a):
    time.sleep(0.75)
    if a.digitalRead(sleep) == a.HIGH:
        print("Sleeping")
        a.digitalWrite(sleep, a.LOW)
    elif a.digitalRead(sleep) == a.LOW:
        print("Awake")
        a.digitalWrite(sleep, a.HIGH)


def translate(a, ccw, steps):
    if(ccw == True):
        a.digitalWrite(direction, a.HIGH)
    else:
        a.digitalWrite(direction, a.LOW)
    for inc in range(steps):
        a.digitalWrite(step, a.LOW)
        time.sleep(STEP_DELAY)
        a.digitalWrite(step, a.HIGH)
        time.sleep(STEP_DELAY)


def shake(a, iterations):
    toggle(a)
    for i in range(iterations):
        translate(a, True, 1)
        time.sleep(0.01)
        translate(a, False, 1)
        time.sleep(0.01)
    toggle(a)


def close_gate(servo):
    servo.write(GATE_CLOSED)


def open_gate(servo):
    servo.write(GATE_OPEN)


def dispense(a, servo):
    try:
        open_gate(servo)
        time.sleep(0.05)
        shake(a, 12)
        close_gate(servo)
        stime = time.time()
        a.digitalWrite(disp_pin, a.HIGH)
        print("DISPENSING")
        photocell_reading = sum([a.analogRead(photocell) for x in range(3)]) / 3
        new_reading = photocell_reading
        while(abs(photocell_reading - new_reading) < 50):
            if abs(time.time() - stime) > 5:
                a.digitalWrite(disp_pin, a.LOW)
                open_gate(servo)
                time.sleep(0.05)
                shake(a, 21)
                close_gate(servo)
                time.sleep(0.05)
                a.digitalWrite(disp_pin, a.HIGH)
                stime = time.time()
            new_reading = a.analogRead(photocell)
    except:
        print("ERROR")
    finally:
        a.digitalWrite(disp_pin, a.LOW)


def home(a):
    return a.digitalRead(limit) == 1


def reset_home(a):
    translate(A, True, 200 / 6)
    while(1):
        translate(A, True, 1)
        if(home(A)):
            time.sleep(0.25)
            translate(A, False, 4)
            print("home")
            break


def navigate(a, cylinder):
    toggle(a)
    reset_home(a)
    for cyl in range(cylinder):
        translate(a, False, 200 / 6)
    toggle(a)


def pinmode(a):
    # PIN SETUP
    a.pinMode(step, a.OUTPUT)  # Step
    a.pinMode(direction, a.OUTPUT)  # direction
    a.pinMode(disp_pin, a.OUTPUT)
    a.pinMode(reset, a.OUTPUT)
    a.pinMode(sleep, a.OUTPUT)
    a.pinMode(limit, a.INPUT)
    a.pinMode(ms1, a.OUTPUT)
    a.pinMode(ms2, a.OUTPUT)
    a.pinMode(ms3, a.OUTPUT)


def init(a, servo):
    # INITIAL STATE
    a.digitalWrite(disp_pin, a.LOW)
    a.digitalWrite(step, a.HIGH)
    a.digitalWrite(direction, a.HIGH)
    a.digitalWrite(sleep, a.LOW)
    a.digitalWrite(reset, a.HIGH)
    a.digitalWrite(ms1, a.LOW)
    a.digitalWrite(ms2, a.LOW)
    a.digitalWrite(ms3, a.LOW)
    close_gate(servo)

if __name__ == '__main__':
    # Nanpy Setup
    CONNECTION = SerialManager(device='/dev/ttyUSB0')
    A = ArduinoApi(connection=CONNECTION)
    SERVO = Servo(gate)
    pinmode(A)
    init(A, SERVO)
    navigate(A, 5)
    dispense(A, SERVO)
    # for cyl in range(6):
    #     print(cyl + 1)
    #     navigate(A, cyl)
    #     time.sleep(3)
