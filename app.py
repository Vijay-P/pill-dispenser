#!/usr/bin/env python3
from flask import Flask, jsonify, make_response, abort, render_template, request
from multiprocessing import Process, Queue
import embedded
import time
from dateutil import parser

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
    return render_template('index.html')

@app.route('/api/v1/medications', methods=['GET'])
def get_medications():
    print("INPUTQ.get()")
    global INPUTQ
    if (not INPUTQ.empty()):
        msg = INPUTQ.get()
        print("reading msg from queue")
        print(msg)

    return jsonify({'cylinders': cylinders}), 200

@app.route('/api/v1/medication', methods=['POST'])
def create_medication():

    print("putting stuff in queue")

    tmpList = []
    for e in request.json:
        tmpList.append(tuple(e[0:4]))

    updatetuple = (tuple(tmpList))
    print('this is going into the queue')
    print(updatetuple)
    INPUTQ.put(updatetuple)
    return jsonify({'cylinders': cylinders}), 201

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=8000)
