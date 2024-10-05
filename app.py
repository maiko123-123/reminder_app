from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, Task
import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

scheduler = BackgroundScheduler()

def send_reminder_email(task):
    msg = Message("Task Reminder",
                  recipients=[task.requester_email, task.assignee_email])
    msg.body = f"Reminder: Your task '{task.title}' is due on {task.due_date}."
    mail.send(msg)

def check_due_tasks():
    with app.app_context():
        tasks = Task.query.filter(Task.due_date <= datetime.datetime.now()).all()
        for task in tasks:
            send_reminder_email(task)

scheduler.add_job(check_due_tasks, 'interval', minutes=1)
scheduler.start()

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_task', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
