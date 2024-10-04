from flask import Flask, render_template
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db
from routes import main as main_routes

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

app.register_blueprint(main_routes)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
