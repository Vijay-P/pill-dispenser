#!/usr/bin/env python
from flask import Flask, jsonify, make_response, abort, render_template, request
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/medications', methods=['GET'])
def get_medications():
    return jsonify({'cylinders': cylinders}), 200


@app.route('/api/v1/medication', methods=['POST'])
def create_medication():
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
