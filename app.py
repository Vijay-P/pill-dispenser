#!/usr/bin/env python3
from flask import Flask, jsonify, make_response, abort, render_template, request
from multiprocessing import Process, Queue

import embedded
import time

app = Flask(__name__)

cylinders = {
    "0": {},
    "1": {},
    "2": {},
    "3": {},
    "4": {},
    "5": {},
}
# TODO: fix dosage

INPUTQ = Queue()
PP = Process(target=embedded.mainthread, args=(INPUTQ,))
PP.start()

@app.route('/')
def index():
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
    # INPUTQ.close()
    # INPUTQ.join_thread()
    print(embedded.mainthread)
    return render_template('index.html')


@app.route('/api/v1/medications', methods=['GET'])
def get_medications():
    # msg = INPUTQ.get()
    # print("reading msg from queue")
    # print(msg)
    # PP.join()
    print("INPUTQ.get()")
    global INPUTQ
    if (not INPUTQ.empty()):
        msg = INPUTQ.get()
        print("reading msg from queue")
        print(msg)

    return jsonify({'cylinders': cylinders}), 200

@app.route('/api/v1/medication', methods=['POST'])
def create_medication():
    updatetuple = (
        (
            (16, 4, 0, 0),
            (22, 27, 0, 1),
            (16, 4, 0, 2),
            (16, 4, 0, 3),
            (16, 4, 0, 4),
            (16, 4, 0, 5)
        )
    )

    print("putting stuff in queue")
    global INPUTQ
    INPUTQ.put(updatetuple)
    print(INPUTQ)
    # INPUTQ.put(updatetuple)
    # print(INPUTQ)
    # if not request.json or not 'title' in request.json:
    #     abort(400)
    cylinders[str(int(request.json['cylinder_number']) % 6)] = {  # Mod it by 6
        # 'id': tasks[-1]['id'] + 1,
        'name': request.json['name'],
        'pills': int(request.json['pills']),
        'hours': int(request.json['hours']),
    }
    return jsonify({'cylinders': cylinders}), 201

if __name__ == '__main__':
    app.run(debug=True)
