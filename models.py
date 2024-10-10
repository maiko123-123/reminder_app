# models.py
from extensions import db

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
    remind_interval = db.Column(db.String(10), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_tasks')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')
    
    # コメントとのリレーションシップを追加
    comments = db.relationship('Comment', backref='task', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)

    user = db.relationship('User', backref='user_comments')  # 名前を変更して競合を避ける
