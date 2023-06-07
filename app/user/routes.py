from app import db
from flask import render_template, url_for, redirect, request, flash, current_app
from flask_login import current_user, login_required
from app.user.forms import CreateTaskForm, TaskCommentForm
from app.models import Task, TaskComment
from datetime import date
from werkzeug.utils import secure_filename
import os
from app.user import bp

basedir = os.path.abspath(os.path.dirname(__file__))


# ==========================================
# AUTHENTICATED USER
# ==========================================

@bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = CreateTaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            body=form.body.data,
            file=form.file.data,
            due_date=form.due_date.data,
            status='Active',
            author=current_user)

         # Handling file uploads
        uploaded_file = form.file.data
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            if not os.path.exists('app/static/img/uploads'):
                os.mkdir('app/static/img/uploads')
            file_path = os.path.join(
                basedir, current_app.config['UPLOAD_PATH'], task.title + '_' + filename)
            uploaded_file.save(file_path)
            file_path_list = file_path.split('/')
            if 'static' in file_path_list:
                static_index = file_path_list.index('static') + 1
            file_path_list_from_static_folder = file_path.split('/')[static_index:]
            new_file_path = '/'.join(file_path_list_from_static_folder)
            task.file = new_file_path

        db.session.add(task)
        db.session.commit()
        flash('Task created.')
        return redirect(url_for('user.home'))

    # Get all tasks
    tasks = current_user.tasks.order_by(Task.timestamp.desc()).all()
    # Loop through all the tasks
    for new_task in tasks:

        # print('Due date: ', str(new_task.due_date.date()))
        # print('Today: ', str(date.today()))

        # Get the due date of each task
        date_obj = str(new_task.due_date.date())
        # Find the date today
        date_today = str(date.today())
        # Compare the difference in the dates
        if date_obj <= date_today:
            if new_task.status != 'Completed':
                # Update the status of each task
                new_task.status = "Overdue"
                db.session.commit()
                flash(f'The task {new_task.title} is overdue.')

    active_tasks = current_user.tasks.filter_by(status='Active').all()
    num_active_tasks = len(active_tasks)
    overdue_tasks = current_user.tasks.filter_by(status='Overdue').all()
    num_overdue_tasks = len(overdue_tasks)
    completed_tasks = current_user.tasks.filter_by(status='Completed').all()
    num_completed_tasks = len(completed_tasks)
    return render_template(
        'authenticated_user/home.html',
        title='Home',
        form=form,
        tasks=tasks,
        num_active_tasks=num_active_tasks,
        num_overdue_tasks=num_overdue_tasks,
        num_completed_tasks=num_completed_tasks)


@bp.route('/create-task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = CreateTaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            body=form.body.data,
            due_date=form.due_date.data,
            author=current_user)

        # Handling file uploads
        uploaded_file = form.file.data
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            if not os.path.exists('app/static/img/uploads'):
                os.mkdir('app/static/img/uploads')
            file_path = os.path.join(
                basedir, current_app.config['UPLOAD_PATH'], task.title + '_' + filename)
            uploaded_file.save(file_path)
            file_path_list = file_path.split('/')
            if 'static' in file_path_list:
                static_index = file_path_list.index('static') + 1
            file_path_list_from_static_folder = file_path.split('/')[static_index:]
            new_file_path = '/'.join(file_path_list_from_static_folder)
            task.file = new_file_path

        db.session.add(task)
        db.session.commit()
        flash('Task added.')
        return redirect(url_for('user.home'))
    # Get all tasks
    tasks = current_user.tasks.order_by(Task.timestamp.desc()).all()
    # Loop through all the tasks
    for new_task in tasks:

        # print('Due date: ', str(new_task.due_date.date()))
        # print('Today: ', str(date.today()))

        # Get the due date of each task
        date_obj = str(new_task.due_date.date())
        # Find the date today
        date_today = str(date.today())
        # Compare the difference in the dates
        if date_obj <= date_today:
            if new_task.status != 'Completed':
                # Update the status of each task
                new_task.status = "Overdue"
                db.session.commit()
                flash(f'The task {new_task.title} is overdue.')
    return render_template(
        'authenticated_user/create_task.html',
        title='Create Task',
        form=form)


@bp.route('/task-details/<title>', methods=['GET', 'POST'])
@login_required
def task_details(title):
    task = Task.query.filter_by(title=title).first()
    task_comment = TaskComment.query.filter_by(task_id=task.id).first()
    user_task_comments = task.task_comments.all()
    form = CreateTaskForm()
    comment_form = TaskCommentForm()
    # Edit task
    if form.submit.data and form.validate():
        task.title = form.title.data
        task.body = form.body.data
        task.due_date = form.due_date.data

        # Handling file uploads
        uploaded_file = form.file.data
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            if not os.path.exists('app/static/img/uploads'):
                os.mkdir('app/static/img/uploads')
            file_path = os.path.join(
                basedir, current_app.config['UPLOAD_PATH'], task.title + '_' + filename)
            uploaded_file.save(file_path)
            file_path_list = file_path.split('/')
            if 'static' in file_path_list:
                static_index = file_path_list.index('static') + 1
            file_path_list_from_static_folder = file_path.split('/')[static_index:]
            task.file = file_path_list_from_static_folder

        db.session.commit()
        flash('Edits saved.')
        return redirect(url_for('user.task_details', title=task.title))
    # Add a comment to a task
    if comment_form.submit_comment.data and comment_form.validate():
        task_comment = TaskComment(body=comment_form.body.data, task_id=task.id)
        db.session.add(task_comment)
        db.session.commit()
        flash(f'Comment to the task {task.title} saved.')
        return redirect(url_for('user.task_details', title=task.title))
    if request.method == 'GET':
        form.title.data = task.title
        form.body.data = task.body
        form.file.data = task.file
        form.due_date.data = task.due_date
    return render_template(
        'authenticated_user/task_details.html',
        title='Task Details',
        task=task,
        form=form,
        comment_form=comment_form,
        user_task_comments=user_task_comments)


@bp.route('/complete-task/<title>', methods=['GET', 'POST'])
@login_required
def complete_task(title):
    task = Task.query.filter_by(title=title).first()
    task.status='Completed'
    db.session.commit()
    flash(f'The task {task.title} completed.')
    return redirect(url_for('user.home'))


@bp.route('/delete-task/<title>', methods=['GET', 'POST'])
@login_required
def delete_task(title):
    task = Task.query.filter_by(title=title).first()
    db.session.delete(task)
    db.session.commit()
    flash(f'The task {task.title} deleted.')
    return redirect(url_for('user.home'))


# ==========================================
# END OF AUTHENTICATED USER
# ==========================================
