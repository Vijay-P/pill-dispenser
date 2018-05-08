#!/usr/bin/env python3
from multiprocessing import Process, Queue

import embedded
import time

if __name__ == '__main__':
    inputq = Queue()
    p = Process(target=embedded.mainthread, args=(inputq,))
    p.start()
    # NOTE Must update all 6 cylinders at once. !!!!!!!!!!
    # Time is in 24 hour format.
    # Cylinders are numbered [0-5]
    # "number" is number of pills to take
    #Format: ((hour, minute, cylinder, number), (hour, minute, cylinder, number), ...)
    # There should be a minimum of 6 tuples
    # If a dosage is more than 1 time (period?) per day, add a new tuple
    updatetuple = (
        (
            (3, 42, 0, 1),
        )
    )

    inputq.put(updatetuple)
