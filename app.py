#!flask/bin/python
from flask import Flask, jsonify
from flask import make_response
from flask import abort
from flask import request

app = Flask(__name__)

cylinders = []
[
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]
# @app.route('/todo/api/v1.0/tasks', methods=['GET'])

@app.route('/api/v1/medications', methods=['GET'])
def get_medications():
    return jsonify({'cylinders': cylinders}), 201

@app.route('/api/v1/fill', methods=['POST'])
def create_medication():
    print "foooo"
    # if not request.json or not 'title' in request.json:
    #     abort(400)
    cylinder = {
        # 'id': tasks[-1]['id'] + 1,
        'title': request.json['name'],
        'dosage': request.json['dosage'],
        'cylinder_number': request.json['cylinder_number'],
    }
    cylinders.append(cylinder)
    return jsonify({'cylinders': cylinders}), 201

if __name__ == '__main__':
    app.run(debug=True)
