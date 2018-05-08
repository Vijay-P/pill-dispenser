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
    #Format: ((hour, minute, cylinder, number), (hour, minute, cylinder, number), ...)
    updatetuple = (
        (
            (16, 4, 0, 0),
            (21, 12, 0, 1),
            (16, 4, 0, 2),
            (16, 4, 0, 3),
            (16, 4, 0, 4),
            (16, 4, 0, 5)
        )
    )
    inputq.put(updatetuple)

    print ("Start : %s" % time.ctime())
    time.sleep( 5 )
    print ("End : %s" % time.ctime())

    updatetuple = (
        (
            (16, 4, 0, 0),
            (22, 0, 0, 1),
            (16, 4, 0, 2),
            (16, 4, 0, 3),
            (16, 4, 0, 4),
            (16, 4, 0, 5)
        )
    )

    inputq.put(updatetuple)
