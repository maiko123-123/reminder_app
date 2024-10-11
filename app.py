from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, Task, User
from flask_migrate import Migrate
from datetime import datetime, timedelta
import logging
from flask_mail import Message
from extensions import db, mail, migrate
from routes import main as main_routes

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)

# 拡張機能の初期化
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# Blueprint の登録
app.register_blueprint(main_routes)

# スケジューラの初期化
scheduler = BackgroundScheduler()

def get_reminder_recipients(task):
    """リマインダー受信者を取得"""
    recipients = [task.assignee.email]
    team_members = User.query.filter(User.team_id == task.assignee.team_id, User.id != task.assignee.id).all()
    recipients += [member.email for member in team_members]
    return recipients

def send_reminder_email(task):
    """リマインダーのメールを送信"""
    with app.app_context():
        try:
            recipients = get_reminder_recipients(task)
            msg = Message(subject="終わってないタスクがあります！",
                          recipients=recipients,
                          body=f"こんにちは、タスク: {task.title} のリマインダーです！忘れないようにお願いします！")
            mail.send(msg)
            logging.info(f"Email sent to: {recipients}")
        except Exception as e:
            logging.error(f"Error sending email: {e}")

def get_due_tasks():
    """現在時刻を過ぎたタスクを取得"""
    now = datetime.now()
    return Task.query.filter(Task.remind_start_date <= now, Task.is_completed == False).all()

def check_due_tasks():
    """期限が過ぎたタスクをチェックしてリマインダーを送信"""
    with current_app.app_context():
        tasks = get_due_tasks()
        remind_interval_mapping = {
            '1_minute': timedelta(minutes=1),
            'daily': timedelta(days=1),
            'every_three_days': timedelta(days=3),
            'weekly': timedelta(weeks=1),
        }

        for task in tasks:
            last_remind_time = task.last_remind_time
            if last_remind_time is None or (datetime.now() - last_remind_time >= remind_interval_mapping[task.remind_interval]):
                send_reminder_email(task)
                task.last_remind_time = datetime.now()
                db.session.commit()
                schedule_reminder(task)

def schedule_reminder(task):
    """次回のリマインダーをスケジュール"""
    with app.app_context():
        remind_interval_mapping = {
            '1_minute': timedelta(minutes=1),
            'daily': timedelta(days=1),
            'every_three_days': timedelta(days=3),
            'weekly': timedelta(weeks=1),
        }
        if task.remind_interval in remind_interval_mapping:
            next_remind_time = datetime.now() + remind_interval_mapping[task.remind_interval]
            scheduler.add_job(send_reminder_email, 'date', run_date=next_remind_time, args=[task])

# APSchedulerでのタスク設定
scheduler.add_job(lambda: app.app_context().push() or check_due_tasks(), 'interval', minutes=1)
scheduler.start()
logging.info("Scheduler started.")

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

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
        due_date=datetime.strptime(due_date, '%Y-%m-%dT%H:%M'),
        remind_start_date=datetime.strptime(remind_start_date, '%Y-%m-%dT%H:%M'),
        remind_interval=remind_interval,
        is_completed=False
    )

    db.session.add(new_task)
    db.session.commit()

    # リマインダーをスケジュール
    schedule_reminder(new_task)

    # タスク登録のメールを送信
    recipients = get_reminder_recipients(new_task)
    task_url = url_for('main.task_detail', task_id=new_task.id, _external=True)
    msg = Message(
        subject="新しいタスクが作成されました",
        recipients=recipients,
        html=render_template('emails/new_task.html', task=new_task, task_url=task_url)
    )
    mail.send(msg)

    task_list_url = url_for('main.task_list', _external=True)
    return jsonify({'redirect_url': task_list_url})

if __name__ == '__main__':
    app.run(debug=True)
