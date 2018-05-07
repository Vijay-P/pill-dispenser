#!/usr/bin/env python
from multiprocessing import Process, Queue

import embedded

if __name__ == '__main__':
    inputq = Queue()
    p = Process(target=embedded.mainthread, args=(inputq,))
    p.start()
    # NOTE Must update all 6 cylinders at once. !!!!!!!!!!
    # Time is in 24 hour format.
    # Cylinders are numbered [0-5]
    #Format: ((hour, minute, cylinder, number), (hour, minute, cylinder, number), ...)
    updatetuple = (((16, 4, 0, 0), (16, 4, 0, 0)))
    inputq.put(updatetuple)
