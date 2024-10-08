from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, Task
import datetime
from routes import main as main_routes

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = '自分で好きなsecretkeyを設定してください。なんでもおっけいです'

db.init_app(app)
mail = Mail(app)

scheduler = BackgroundScheduler()

def send_reminder_email(task):
    msg = Message("Task Reminder", recipients=[task.assignee_email])
    msg.body = f"Reminder: Your task '{task.title}' is due on {task.due_date}."
    mail.send(msg)

def check_due_tasks():
    with app.app_context():
        tasks = Task.query.filter(Task.due_date <= datetime.datetime.now(), Task.is_completed == False).all()
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
    return render_template('index.html')

@app.route('/register_task', methods=['POST'])
def register_task():
    task_content = request.form.get('taskContent')
    username = request.form.get('username')
    shared_username = "自分のメールアドレスをいれてください"  # 仮のメールアドレス
    due_date = request.form.get('dueDate')
    remind_start_date = request.form.get('remindStartDate')
    remind_interval = request.form.get('remindInterval')

    new_task = Task(
        title=task_content,
        requester_email=username,
        assignee_email=shared_username,
        due_date=datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M'),
        remind_start_date=datetime.datetime.strptime(remind_start_date, '%Y-%m-%dT%H:%M'),
        remind_interval=remind_interval,
        is_completed=False
    )

    db.session.add(new_task)
    db.session.commit()

    flash('タスクが登録されました！', 'success')
    
    # タスク詳細ページのURLを生成
    task_detail_url = url_for('main.task_detail', task_id=new_task.id, _external=True)

    # メール通知を送信
    msg = Message("New Task Created", recipients=[shared_username])
    msg.body = f'Task "{task_content}" has been created.\n\nYou can view it here: {task_detail_url}'
    mail.send(msg)

    return jsonify({'message': 'タスクが登録されました！', 'task_id': new_task.id})

if __name__ == '__main__':
    app.run(debug=True)
