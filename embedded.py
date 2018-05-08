#!/usr/bin/env python3

# Native packages
import time
import sched
from datetime import datetime

from multiprocessing import Process, Queue

# External pakages
from nanpy import SerialManager, ArduinoApi, Servo

# TIMING AND OTHER CONSTANTS
FULL_ROTATION = 200
STEP_DELAY = 0.001
GATE_OPEN = 132
GATE_CLOSED = 150
PILL_DETECT = 30
SHAKE_DEL = 0.01
SLEEP_TIME = 0.05
SHAKE_DIST = 2

# ARDUINO PINS
# PINS 0, 1 and 11 broken
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

CONNECTION = SerialManager(device='/dev/ttyUSB0')
A = ArduinoApi(connection=CONNECTION)
SERVO = Servo(PINS['gate'])
JOBS = []
SCHED = sched.scheduler(time.time, time.sleep)


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
        a.digitalWrite(PINS['direction'], a.LOW)
    else:
        a.digitalWrite(PINS['direction'], a.HIGH)
    for _ in range(steps):
        a.digitalWrite(PINS['step'], a.LOW)
        time.sleep(STEP_DELAY)
        a.digitalWrite(PINS['step'], a.HIGH)
        time.sleep(STEP_DELAY)


def shake(a, iterations):
    for _ in range(iterations):
        translate(a, True, SHAKE_DIST)
        time.sleep(SHAKE_DEL)
        translate(a, False, SHAKE_DIST)
        time.sleep(SHAKE_DEL)


def close_gate(servo):
    servo.write(GATE_CLOSED)


def open_gate(servo):
    servo.write(GATE_OPEN)


def navigate(a, cylinder):
    reset_home(a)
    time.sleep(SLEEP_TIME)
    for _ in range(cylinder):
        translate(a, True, 200 / 6)
    if cylinder in [2, 3]:
        translate(a, True, 2)
    if cylinder in [0, 1, 4]:
        translate(a, True, 1)
    if cylinder in [5]:
        translate(a, True, 4)
    # if cylinder in [3]:
    #     translate(a, False, 1)
    time.sleep(SLEEP_TIME)


def dispense(a, servo, cylinder):
    try:
        toggle(a)
        navigate(a, cylinder)
        open_gate(servo)
        time.sleep(SLEEP_TIME)
        shake(a, 6)
        time.sleep(0.5)
        close_gate(servo)
        stime = time.time()
        a.digitalWrite(PINS['dispense'], a.HIGH)
        print("DISPENSING")
        photocell_reading = sum([a.analogRead(PINS['photocell']) for _ in range(3)]) / 3
        new_reading = photocell_reading
        numshakes = 6
        while abs(photocell_reading - new_reading) < PILL_DETECT:
            if abs(time.time() - stime) > 3:
                a.digitalWrite(PINS['dispense'], a.LOW)
                open_gate(servo)
                time.sleep(SLEEP_TIME)
                shake(a, numshakes)
                numshakes += 6
                close_gate(servo)
                time.sleep(SLEEP_TIME)
                a.digitalWrite(PINS['dispense'], a.HIGH)
                stime = time.time()
            new_reading = a.analogRead(PINS['photocell'])
        time.sleep(SLEEP_TIME)
        translate(A, True, 10)
    except Exception as exc:
        print("ERROR", exc)
    finally:
        toggle(a)
        a.digitalWrite(PINS['dispense'], a.LOW)


def home(a):
    return a.digitalRead(PINS['limit']) == 1


def reset_home(a):
    translate(a, False, 200 / 6)
    while 1:
        translate(a, False, 1)
        if home(a):
            time.sleep(0.25)  # .25
            translate(a, True, 3)
            time.sleep(0.1)
            print("home")
            break


def reload(a, cylinder):
    if cylinder < 3:
        cylinder += 3
    else:
        cylinder %= 3
    toggle(a)
    reset_home(a)
    for _ in range(cylinder):
        translate(a, False, 200 / 6)
        translate(a, False, 7)
    toggle(a)


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


def printest(a, b, c, d):
    print("DISPENSING ", d, " pills from cylinder ", c)


def create_job(a, servo, hour, minute, cylinder, number):
    currtime = datetime.now()
    medtime = currtime.replace(hour=hour, minute=minute, second=0)
    diff = time.mktime(medtime.timetuple()) - time.time()
    if(diff > 0):
        print("Job in ", diff)
        SCHED.enter(diff, 1, dispense, (a, servo, cylinder, number))
        # SCHED.enter(diff, 1, printest, (a, servo, cylinder, number))
    # else:
    #     try:
    #         medtime2 = medtime.replace(day=medtime.day + 1)
    #     except ValueError:
    #         medtime2 = medtime.replace(month=medtime.month + 1, day=1)
    #     finally:
    #         diff = time.mktime(medtime2.timetuple()) - time.time()
    #         event = SCHED.enter(diff, 1, dispense, )
    #         SCHED.run()


def reloadJobs():
    for x in JOBS:
        create_job(A, SERVO, x[0], x[1], x[2], x[3])
    currtime = datetime.now()
    reloadtime = currtime.replace(day=currtime.day + 1, hour=0, minute=0, second=0)
    diff = time.mktime(reloadtime.timetuple()) - time.time()
    SCHED.enter(diff, 1, reloadJobs, ())


def mainthread(inqueue):
    print('threadstart')
    global JOBS
    pinmode(A)
    init(A, SERVO)
    # reloadjobs at midnight
    currtime = datetime.now()
    reloadtime = currtime.replace(day=currtime.day + 1, hour=0, minute=0, second=0)
    diff = time.mktime(reloadtime.timetuple()) - time.time()
    SCHED.enter(diff, 1, reloadJobs, ())
    while 1:
        try:
            if not inqueue.empty():
                SCHED.run(False)
                newjobs = inqueue.get()
                print('newjobs')
                print(newjobs)
                assert isinstance(newjobs, tuple)
                # assert len(newjobs) >= 6
                JOBS = []
                for job in newjobs:
                    assert len(job) == 4
                    #hour, minute, cylinder, number
                    JOBS.append(job)
                    create_job(A, SERVO, *job)
            else:
                SCHED.run(False)
        except AssertionError:
            break
    A.digitalWrite(PINS['sleep'], A.LOW)

if __name__ == '__main__':
    pass
    # Nanpy Setup
    # CONNECTION = SerialManager(device='/dev/ttyUSB0')
    # A = ArduinoApi(connection=CONNECTION)
    # SERVO = Servo(PINS['gate'])
    # pinmode(A)
    # init(A, SERVO)
    # open_gate(SERVO)
    # toggle(A)
    # for x in range(6):
    #     navigate(A, x)
    #     time.sleep(3)
    # toggle(A)
    # dispense(A, SERVO, 0)
    # inputq = Queue()
    # p = Process(target=mainthread, args=(inputq))
    # p.start()
