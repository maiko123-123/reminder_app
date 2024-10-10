# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db, mail  # extensions.py からインポート
from models import Task, User, Comment
from flask_mail import Message
import logging
import datetime

main = Blueprint('main', __name__)

def get_completion_recipients(task):
    recipients = [task.requester.email]
    team_members = User.query.filter(
        User.team_id == task.assignee.team_id,
        User.id != task.assignee.id
    ).all()
    recipients += [member.email for member in team_members]
    return recipients
@main.route('/')
def index():
    users = User.query.all()  # ユーザー一覧を取得
    return render_template('index.html', users=users)

@main.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    comments = task.comments  # コメントの取得
    return render_template('task_detail.html', task=task, comments=comments)

@main.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.is_completed:
        flash('タスクは既に完了しています。')
        return redirect(url_for('main.task_detail', task_id=task_id))
    
    # タスクを完了に設定
    task.is_completed = True
    db.session.commit()
    flash('タスクを完了にしました。')

    # メール送信処理
    try:
        recipients = get_completion_recipients(task)
        msg = Message(
            subject="タスクが完了しました",
            recipients=recipients,
            body=f"タスク「{task.title}」が完了しました。\n\n依頼者: {task.requester.username}\n担当者: {task.assignee.username}\n完了日: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        mail.send(msg)
        logging.info(f"Completion email sent to: {recipients}")
    except Exception as e:
        logging.error(f"Error sending completion email: {e}")
        flash('タスク完了の通知メールの送信に失敗しました。')

    return redirect(url_for('main.task_detail', task_id=task_id))

@main.route('/add_comment/<int:task_id>', methods=['POST'])
def add_comment(task_id):
    content = request.form.get('comment')
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('ユーザーが見つかりません。')
        return redirect(url_for('main.task_detail', task_id=task_id))
    
    comment = Comment(task_id=task_id, user_id=user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    flash('コメントを追加しました。')
    return redirect(url_for('main.task_detail', task_id=task_id))

@main.route('/task_list')
def task_list():
    tasks = Task.query.all()
    return render_template('task_list.html', tasks=tasks)

    user = User.query.filter_by(username=username).first()

    if content and user:
        new_comment = Comment(task_id=task_id, user_id=user.id, content=content)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('main.task_detail', task_id=task_id))

@main.route('/register_task', methods=['POST'])
def register_task():
    title = request.form.get('taskContent')
    requester_id = request.form.get('requester_id')
    assignee_id = request.form.get('assignee_id')
    due_date = request.form.get('dueDate')
    remind_start_date = request.form.get('remindStartDate')
    remind_interval = request.form.get('remindInterval')

    new_task = Task(
        title=title,
        requester_id=requester_id,
        assignee_id=assignee_id,
        due_date=datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M'),
        remind_start_date=datetime.datetime.strptime(remind_start_date, '%Y-%m-%dT%H:%M'),
        remind_interval=remind_interval,
        is_completed=False
    )
    
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('main.task_list'))  # リダイレクトを追加
