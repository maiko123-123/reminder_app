# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, Task, User, Team, Comment
import datetime
from routes import main as main_routes
from flask_migrate import Migrate
from datetime import timedelta
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = 'a_random_string_12345!@#'

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# スケジューラの初期化
scheduler = BackgroundScheduler()

def send_reminder_email(task):
    with app.app_context():
        try:
            recipients = get_reminder_recipients(task)
            msg = Message("Task Reminder", recipients=recipients)
            msg.body = f"Reminder: Your task '{task.title}' is due on {task.due_date}."
            mail.send(msg)
            logging.info(f"Email sent to: {recipients}")  # ここにログを追加
        except Exception as e:
            logging.error(f"Error sending email: {e}")  # エラーの詳細をログに記録

def get_reminder_recipients(task):
    recipients = [task.assignee.email]
    team_members = User.query.filter(User.team_id == task.assignee.team_id, User.id != task.assignee.id).all()
    recipients += [member.email for member in team_members]
    return recipients

def check_due_tasks():
    with app.app_context():
        now = datetime.datetime.now()
        # タスクのリストを取得する条件を変更
        tasks = Task.query.filter(Task.is_completed == False).all()
        logging.info(f"Checking due tasks at {now}. Found tasks: {[task.title for task in tasks]}")  # ログ追加
        for task in tasks:
            # タスクが期日を過ぎている場合、またはリマインド開始日時を過ぎている場合に通知を送る
            if task.due_date <= now or task.remind_start_date <= now:
                send_reminder_email(task)
            
def schedule_reminder(task):
    # 次回のリマインド時間を計算
    if task.remind_interval == '1_minute':
        next_remind_time = datetime.datetime.now() + timedelta(minutes=1)
    elif task.remind_interval == 'daily':
        next_remind_time = datetime.datetime.now() + timedelta(days=1)
    elif task.remind_interval == 'every_three_days':
        next_remind_time = datetime.datetime.now() + timedelta(days=3)
    elif task.remind_interval == 'weekly':
        next_remind_time = datetime.datetime.now() + timedelta(weeks=1)

    # アプリケーションコンテキストを使用してジョブを追加
    with app.app_context():
        scheduler.add_job(send_reminder_email, 'date', run_date=next_remind_time, args=[task])

with app.app_context():
    db.create_all()
    # スケジューラにジョブを追加
    scheduler.add_job(check_due_tasks, 'interval', minutes=1)
    scheduler.start()
    logging.info("Scheduler started.")

# Blueprintの登録
app.register_blueprint(main_routes)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# タスクを登録する際の処理を維持します
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

    # リマインドスケジュールを設定
    schedule_reminder(new_task)
    # ここでも次回のリマインドをスケジュール
    if new_task.remind_start_date <= datetime.datetime.now():
        schedule_reminder(new_task)
        
if __name__ == '__main__':
    app.run(debug=True)