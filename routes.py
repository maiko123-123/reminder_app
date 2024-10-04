from flask import Blueprint, request, jsonify
from models import db, Task, Comment
import datetime

main = Blueprint('main', __name__)

@main.route('/add_task', methods=['POST'])
def add_task():
    data = request.get_json()
    due_date = datetime.datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M')

    new_task = Task(
        title=data['title'],
        due_date=due_date,
        requester_email=data['requester_email'],
        assignee_email=data['assignee_email']
    )
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({'message': 'Task added'}), 201

@main.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    new_comment = Comment(
        task_id=data['task_id'],
        content=data['content']
    )
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment added'}), 201
