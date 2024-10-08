from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    requester_email = db.Column(db.String(100), nullable=False)
    assignee_email = db.Column(db.String(100), nullable=False)
    remind_start_date = db.Column(db.DateTime, nullable=False)
    remind_interval = db.Column(db.String(10), nullable=False)  # "daily" or "weekly"
    is_completed = db.Column(db.Boolean, default=False)  # タスクのステータス

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
