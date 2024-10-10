from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Task, Comment, User
import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    users = User.query.all()  # ユーザー一覧を取得
    return render_template('index.html', users=users)

@main.route('/task_list')
def task_list():
    tasks = Task.query.filter_by(is_completed=False).all()
    return render_template('task_list.html', tasks=tasks)

@main.route('/task_detail/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get(task_id)
    comments = Comment.query.filter_by(task_id=task_id).all()
    return render_template('task_detail.html', task=task, comments=comments, requester=task.requester)

@main.route('/add_comment/<int:task_id>', methods=['POST'])
def add_comment(task_id):
    content = request.form.get('comment')
    username = request.form.get('username')

    user = User.query.filter_by(username=username).first()

    if content and user:
        new_comment = Comment(task_id=task_id, user_id=user.id, content=content)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('main.task_detail', task_id=task_id))

@main.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.is_completed = True
        db.session.commit()
        flash('タスクが完了しました。', 'success')
    else:
        flash('タスクが見つかりませんでした。', 'error')
    
    return redirect(url_for('main.task_list'))

@main.route('/register_task', methods=['POST'])
def register_task():
    title = request.form.get('taskContent')
    requester_id = request.form.get('requester_id')
    assignee_id = request.form.get('assignee_id')
    due_date = request.form.get('dueDate')
    remind_start_date = request.form.get('remindStartDate')
    remind_interval = request.form.get('remindInterval')

    new_task = Task(
        title=title,
        requester_id=requester_id,
        assignee_id=assignee_id,
        due_date=datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M'),
        remind_start_date=datetime.datetime.strptime(remind_start_date, '%Y-%m-%dT%H:%M'),
        remind_interval=remind_interval,
        is_completed=False
    )
    
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('main.task_list'))  # リダイレクトを追加
