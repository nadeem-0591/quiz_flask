from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['quizdb']
quizzes = db['quizzes']


@app.route('/quizzes', methods=['POST'])
def create_quiz():
    data = request.json
    question = data['question']
    options = data['options']
    right_answer = data['rightAnswer']
    start_date = datetime.strptime(data['startDate'], '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(data['endDate'], '%Y-%m-%d %H:%M:%S')

    quiz = {
        'question': question,
        'options': options,
        'right_answer': right_answer,
        'start_date': start_date,
        'end_date': end_date,
        'status': 'inactive'
    }
    quiz_id = quizzes.insert_one(quiz).inserted_id

    return jsonify({'message': 'Quiz created successfully', 'id': str(quiz_id)}), 201


@app.route('/quizzes/active', methods=['GET'])
def get_active_quiz():
    now = datetime.now()

    quiz = quizzes.find_one({
        'start_date': {'$lte': now},
        'end_date': {'$gte': now},
        'status': 'active'
    })

    if quiz:
        quiz['_id'] = str(quiz['_id'])
        return jsonify(quiz), 200
    else:
        return jsonify({'message': 'No active quiz found'}), 404


@app.route('/quizzes/<string:id>/result', methods=['GET'])
def get_quiz_result(id):
    quiz = quizzes.find_one({
        '_id': id,
        'status': 'finished'
    })

    if quiz:
        return jsonify({'rightAnswer': quiz['options'][quiz['right_answer']]}), 200
    else:
        return jsonify({'message': 'Quiz not found or not finished'}), 404


@app.route('/quizzes/all', methods=['GET'])
def get_all_quizzes():
    all_quizzes = []
    for quiz in quizzes.find():
        quiz['_id'] = str(quiz['_id'])
        all_quizzes.append(quiz)

    return jsonify(all_quizzes), 200


if __name__ == '__main__':
    app.run(debug=True)
