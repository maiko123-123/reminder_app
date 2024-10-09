# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, Task, User, Team, Comment  # User と Team をインポート
import datetime
from routes import main as main_routes
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = 'a_random_string_12345!@#'

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

scheduler = BackgroundScheduler()

def send_reminder_email(task):
    recipients = get_reminder_recipients(task)
    msg = Message("Task Reminder", recipients=recipients)
    msg.body = f"Reminder: Your task '{task.title}' is due on {task.due_date}."
    mail.send(msg)

def get_reminder_recipients(task):
    # 実行者のメールアドレス
    recipients = [task.assignee.email]
    # 実行者のチームメンバーのメールアドレス（実行者自身を除く）
    team_members = User.query.filter(User.team_id == task.assignee.team_id, User.id != task.assignee.id).all()
    recipients += [member.email for member in team_members]
    return recipients

def check_due_tasks():
    with app.app_context():
        now = datetime.datetime.now()
        tasks = Task.query.filter(Task.due_date <= now, Task.is_completed == False).all()
        for task in tasks:
            send_reminder_email(task)

scheduler.add_job(check_due_tasks, 'interval', minutes=1)
scheduler.start()

with app.app_context():
    db.create_all()

# Blueprintの登録
app.register_blueprint(main_routes)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)  # ユーザーリストをテンプレートに渡す

@app.route('/register_task', methods=['POST'])
def register_task():
    task_content = request.form.get('taskContent')
    requester_id = request.form.get('requester_id')
    assignee_id = request.form.get('assignee_id')
    due_date = request.form.get('dueDate')
    remind_start_date = request.form.get('remindStartDate')
    remind_interval = request.form.get('remindInterval')

    requester = User.query.get(requester_id)
    assignee = User.query.get(assignee_id)

    if not requester or not assignee:
        return jsonify({'error': '依頼者または実行者が見つかりません。'}), 400

    new_task = Task(
        title=task_content,
        requester_id=requester.id,
        assignee_id=assignee.id,
        due_date=datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M'),
        remind_start_date=datetime.datetime.strptime(remind_start_date, '%Y-%m-%dT%H:%M'),
        remind_interval=remind_interval,
        is_completed=False
    )

    db.session.add(new_task)
    db.session.commit()

    # 実行者とそのチームメンバーにメール通知を送信
    recipients = get_reminder_recipients(new_task)
    msg = Message("New Task Created", recipients=recipients)
    msg.body = f'Task "{task_content}" has been created and assigned to you.'
    mail.send(msg)

    # タスクリストのURLを返す
    task_list_url = url_for('main.task_list', _external=True)
    return jsonify({'redirect_url': task_list_url})

if __name__ == '__main__':
    app.run(debug=True)
