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

def get_comment_recipients(task, commenter):
    """
    コメント通知の受信者を取得します。
    - 依頼者
    - 実行者
    - チームメンバー
    - コメントを追加したユーザーを除外
    """
    recipients = set()

    # 依頼者と実行者を追加
    if task.requester.email:
        recipients.add(task.requester.email)
    if task.assignee.email:
        recipients.add(task.assignee.email)

    # チームメンバーを追加（実行者を除外）
    team_members = User.query.filter(
        User.team_id == task.assignee.team_id,
        User.id != task.assignee.id
    ).all()
    for member in team_members:
        recipients.add(member.email)

    # コメントを追加したユーザーを除外
    if commenter.email in recipients:
        recipients.remove(commenter.email)

    return list(recipients)

@main.route('/')
def index():
    users = User.query.all()
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
        task_url = url_for('main.task_detail', task_id=task.id, _external=True)
        completed_at = datetime.datetime.now()
        msg = Message(
            subject="タスクが完了しました",
            recipients=recipients,
            html=render_template(
                'emails/task_completed.html',
                task=task,
                task_url=task_url,
                completed_at=completed_at
            )
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
    
    # コメントの作成と保存
    comment = Comment(task_id=task_id, user_id=user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    flash('コメントを追加しました。')
    
    # タスクの取得
    task = Task.query.get(task_id)
    
    # コメント通知の受信者を取得
    recipients = get_comment_recipients(task, user)
    
    # メール送信処理
    try:
        msg = Message(
            subject=f"新しいコメントがタスク「{task.title}」に追加されました",
            recipients=recipients,
            html=render_template(
                'emails/new_comment.html',
                commenter=user,
                task=task,
                comment=comment
            )
        )
        mail.send(msg)
        logging.info(f"Comment notification sent to: {recipients}")
    except Exception as e:
        logging.error(f"Error sending comment notification email: {e}")
        flash('コメントの通知メールの送信に失敗しました。')
    
    return redirect(url_for('main.task_detail', task_id=task_id))

@main.route('/task_list')
def task_list():
    tasks = Task.query.all()
    return render_template('task_list.html', tasks=tasks)

@main.route('/register_task', methods=['POST'])
def register_task():
    title = request.form.get('taskContent')
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
        title=title,
        requester_id=requester.id,
        assignee_id=assignee.id,
        due_date=datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M'),
        remind_start_date=datetime.datetime.strptime(remind_start_date, '%Y-%m-%dT%H:%M'),
        remind_interval=remind_interval,
        is_completed=False
    )
    
    db.session.add(new_task)
    db.session.commit()

    # タスク登録時のメール送信処理
    try:
        recipients = get_completion_recipients(new_task)
        task_url = url_for('main.task_detail', task_id=new_task.id, _external=True)
        msg = Message(
            subject="新しいタスクが作成されました",
            recipients=recipients,
            html=render_template(
                'emails/new_task.html',
                task=new_task,
                task_url=task_url
            )
        )
        mail.send(msg)
        logging.info(f"New task email sent to: {recipients}")
    except Exception as e:
        logging.error(f"Error sending new task email: {e}")
        flash('タスク登録の通知メールの送信に失敗しました。')

    return redirect(url_for('main.task_list'))

def send_reminder_email(task):
    with app.app_context():
        try:
            recipients = get_reminder_recipients(task)
            task_url = url_for('main.task_detail', task_id=task.id, _external=True)
            msg = Message(
                subject="タスクのリマインダー",
                recipients=recipients,
                html=render_template(
                    'emails/task_reminder.html',
                    task=task,
                    task_url=task_url
                )
            )
            mail.send(msg)
            logging.info(f"Reminder email sent to: {recipients}")
        except Exception as e:
            logging.error(f"Error sending reminder email: {e}")    