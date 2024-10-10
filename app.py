# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, Task, User, Team, Comment
from flask_migrate import Migrate
from datetime import timedelta
import datetime
import logging

# 拡張機能のインポート
from extensions import db, mail, migrate
from routes import main as main_routes  # Blueprint のインポートは最後に行う

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = 'a_random_string_12345!@#'

# 拡張機能の初期化
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# Blueprint の登録（拡張機能の初期化後に行う）
app.register_blueprint(main_routes)

# スケジューラの初期化
scheduler = BackgroundScheduler()

def send_reminder_email(task):
    with app.app_context():
        try:
            recipients = get_remind(task)  # 仮の関数呼び出し
            msg = Message(subject="タスクのリマインダー",
                          recipients=recipients,
                          body=f"タスク: {task.title} のリマインダーです。")
            mail.send(msg)
            logging.info(f"Email sent to: {recipients}")  # ログを追加
        except Exception as e:
            logging.error(f"Error sending email: {e}")

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

    recipients = get_reminder_recipients(new_task)
    msg = Message("New Task Created", recipients=recipients)
    msg.body = f'Task "{task_content}" has been created and assigned to you.'
    mail.send(msg)

    task_list_url = url_for('main.task_list', _external=True)
    return jsonify({'redirect_url': task_list_url})

    # リマインドスケジュールを設定
    schedule_reminder(new_task)
    # ここでも次回のリマインドをスケジュール
    if new_task.remind_start_date <= datetime.datetime.now():
        schedule_reminder(new_task)

if __name__ == '__main__':
    app.run(debug=True)
