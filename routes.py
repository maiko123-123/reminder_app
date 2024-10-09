from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Task, Comment, User

main = Blueprint('main', __name__)

@main.route('/task_list')
def task_list():
    tasks = Task.query.filter_by(is_completed=False).all()
    return render_template('task_list.html', tasks=tasks)

@main.route('/task_detail/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get(task_id)
    comments = Comment.query.filter_by(task_id=task_id).all()
    return render_template('task_detail.html', task=task, comments=comments)

@main.route('/add_comment/<int:task_id>', methods=['POST'])
def add_comment(task_id):
    content = request.form.get('comment')
    username = request.form.get('username')  # 名前を取得

    user = User.query.filter_by(username=username).first()  # ユーザーを検索

    # デバッグ用の print 文
    print(f"Received comment: '{content}' from user: '{username}'")  # デバッグ用

    if content and user:
        new_comment = Comment(task_id=task_id, user_id=user.id, content=content)  # user_idを追加
        db.session.add(new_comment)
        db.session.commit()
        print(f"Comment added successfully!")  # 成功メッセージ
    else:
        print("Failed to add comment: Content or user not found.")  # エラーメッセージ
    
    return redirect(url_for('main.task_detail', task_id=task_id))

@main.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.is_completed = True
        db.session.commit()
        flash('タスクが完了しました。', 'success')
    else:
        flash('タスクが見つかりませんでした。', 'error')
    
    return redirect(url_for('main.task_list'))
