from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, Task, User, Team, Comment
import datetime
from routes import main as main_routes
from flask_migrate import Migrate
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
            recipients = get_remind(task)  # 仮の関数呼び出し
            msg = Message(subject="タスクのリマインダー",
                          recipients=recipients,
                          body=f"タスク: {task.title} のリマインダーです。")
            mail.send(msg)
        except Exception as e:
            logging.error(f"Error sending email: {e}")

# ルートを登録
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True)
