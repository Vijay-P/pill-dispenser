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


    # updatetuple = (
    #     (
    #         (16, 4, 0, 0),
    #         (21, 12, 0, 1),
    #         (16, 4, 0, 2),
    #         (16, 4, 0, 3),
    #         (16, 4, 0, 4),
    #         (16, 4, 0, 5)
    #     )
    # )
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

    print("putting stuff in queue")
    global INPUTQ

    print('request.json')
    print(request.json)
    print(type(request.json))

    tmpList = []
    for e in request.json:
        tmpList.append(tuple(e))

    updatetuple = (tuple(tmpList))
    # INPUTQ.put(updatetuple)
    # print(INPUTQ)
    # if not request.json or not 'title' in request.json:
    #     abort(400)
    # hoursText = request.json['hours']
    # dt = parser.parse(hoursText)
    # cylinders[str(int(request.json['cylinder_number']) % 6)] = {  # Mod it by 6
    #     # 'id': tasks[-1]['id'] + 1,
    #     'name': request.json['name'],
    #     'pills': int(request.json['pills']),
    #     'hours': request.json['hours'],
    # }

    # updatetuple = (())
    # (hour, minute, cylinder, number)
    # key should be cylinder + time
    # fake initialization
    # INPUTQ.get()
    # if (not INPUTQ.empty()):
        # updatetuple = INPUTQ.get()
        # print("reading msg from queue")
        # print(updatetuple)

    # print("coming in from API")
    # incoming = (dt.hour, dt.minute, request.json['cylinder_number'], int(request.json['pills']))
    # print(income)

    # else:
        # print("initialize new filler")
        # updatetuple = (())
        # tmpMap = {}
        # tu = updatetuple
        # print("assign tu with stuff")
        # print(tu)
        #
        # for item in tu:
        #     cylinder = item[2]
        #     tdt = str(item[0]) + ":" + str(item[1])
        #     k = str(cylinder) + '+' + tdt
        #     tmpMap[k] = item
        # tmpMapK = str(request.json['cylinder_number']) + '+' + str(dt.hour) + ':' + str(dt.minute)
        # tmpMap[tmpMapK] = (dt.hour, dt.minute, request.json['cylinder_number'], int(request.json['pills']))
        #
        # tmpArr = []
        # for k in tmpMap.keys():
        #     tmpArr.append(tmpMap[k])
        #
        # updatetuple = (tuple(tmpArr))
        #
    print('this is going into the queue')
    print(updatetuple)
    INPUTQ.put(updatetuple)
    return jsonify({'cylinders': cylinders}), 201

if __name__ == '__main__':
    app.run(debug=True)
