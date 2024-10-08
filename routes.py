from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Task, Comment

main = Blueprint('main', __name__)

@main.route('/task_list')
def task_list():
    tasks = Task.query.filter_by(is_completed=False).all()  # 未完了のタスクのみを取得
    return render_template('task_list.html', tasks=tasks)

@main.route('/task_detail/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get(task_id)
    comments = Comment.query.filter_by(task_id=task_id).all()
    return render_template('task_detail.html', task=task, comments=comments)

@main.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.is_completed = True  # 完了フラグを更新
        db.session.commit()
        flash('タスクが完了しました。', 'success')
    else:
        flash('タスクが見つかりませんでした。', 'error')
    
    return redirect(url_for('main.task_list'))
