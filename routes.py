from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Task, Comment, db

main = Blueprint('main', __name__)

@main.route('/tasks')
def task_list():
    tasks = Task.query.all()
    return render_template('task_list.html', tasks=tasks)

@main.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    comments = Comment.query.filter_by(task_id=task_id).all()
    return render_template('task_detail.html', task=task, comments=comments)

@main.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)  # タスクを削除
    db.session.commit()
    flash('タスクが完了し、削除されました！', 'success')
    return redirect(url_for('main.task_list'))  # タスク一覧ページにリダイレクト
