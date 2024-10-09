# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    members = db.relationship('User', backref='team', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remind_start_date = db.Column(db.DateTime, nullable=False)
    remind_interval = db.Column(db.String(10), nullable=False)  # "daily" or "weekly"
    is_completed = db.Column(db.Boolean, default=False)  # タスクのステータス

    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_tasks')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
