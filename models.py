from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    requester_email = db.Column(db.String(100), nullable=False)
    assignee_email = db.Column(db.String(100), nullable=False)
