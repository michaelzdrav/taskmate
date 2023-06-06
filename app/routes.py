from app import app, db
from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, \
    ResetPasswordForm, CreateTaskForm, TaskCommentForm,VerifyForm
from app.models import User, Task, TaskComment
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, thank_you_user
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os
from app.twilio_verify_api import check_email_verification_token,request_email_verification_token

basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template(
        'index.html',
        title='Welcome To TaskMate!')

# ==========================================
# AUTHENTICATION
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        flash(f'Welcome {user.username}.')
        return redirect(next_page)
    return render_template(
        'auth/login.html',
        title='Login',
        form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        session['user'] = user
        request_email_verification_token(user.email)
        flash('A token has been sent to your email address. '
              'Enter it below to confirm you have access to your email address.')
        return redirect(url_for('verify_email_token'))
    return render_template(
        'auth/register.html',
        title='Register',
        form=form)


@app.route('/verify-email-token', methods=['GET', 'POST'])
def verify_email_token():
    """
    User verifies their email address by 
    providing token sent to their inbox
    """
    form = VerifyForm()
    if form.validate_on_submit():
        user = session['user']

        if check_email_verification_token(user.email, form.token.data):
            db.session.add(user)
            db.session.commit()
            del session['user']

            # Send user a thank you email
            thank_you_user(user)

            flash('Registered successfully. Please check you inbox.')
            return redirect(url_for('login'))
        form.token.errors.append('Invalid token.')
    return render_template(
        'auth/verify_email_token.html',
        title='Verify Your Email',
        form=form)


@app.route('/request-password-reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Send user an email
            send_password_reset_email(user)
        # Conceal database information by giving general information
        flash("Check your email for the instructions to reset your password")
        return redirect(url_for("login"))
    return render_template(
        'auth/request_password_reset.html',
        title='Request Password Reset',
        form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Verify request token
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    # If verified, proceed to allow for password reset
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset. Log in to continue")
        return redirect(url_for('login'))
    return render_template(
        'auth/reset_password.html',
        title='Reset Password',
        form=form)

# ==========================================
# END OF AUTHENTICATION
# ==========================================


# ==========================================
# AUTHENTICATED USER
# ==========================================

@app.route('/home', methods=['GET', 'POST'])
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
                basedir, app.config['UPLOAD_PATH'], task.title + '_' + filename)
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
        return redirect(url_for('home'))

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


@app.route('/create-task', methods=['GET', 'POST'])
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
                basedir, app.config['UPLOAD_PATH'], task.title + '_' + filename)
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
        return redirect(url_for('home'))
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


@app.route('/task-details/<title>', methods=['GET', 'POST'])
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
                basedir, app.config['UPLOAD_PATH'], task.title + '_' + filename)
            uploaded_file.save(file_path)
            file_path_list = file_path.split('/')
            if 'static' in file_path_list:
                static_index = file_path_list.index('static') + 1
            file_path_list_from_static_folder = file_path.split('/')[static_index:]
            task.file = file_path_list_from_static_folder

        db.session.commit()
        flash('Edits saved.')
        return redirect(url_for('task_details', title=task.title))
    # Add a comment to a task
    if comment_form.submit_comment.data and comment_form.validate():
        task_comment = TaskComment(body=comment_form.body.data, task_id=task.id)
        db.session.add(task_comment)
        db.session.commit()
        flash(f'Comment to the task {task.title} saved.')
        return redirect(url_for('task_details', title=task.title))
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


@app.route('/complete-task/<title>', methods=['GET', 'POST'])
@login_required
def complete_task(title):
    task = Task.query.filter_by(title=title).first()
    task.status='Completed'
    db.session.commit()
    flash(f'The task {task.title} completed.')
    return redirect(url_for('home'))


@app.route('/delete-task/<title>', methods=['GET', 'POST'])
@login_required
def delete_task(title):
    task = Task.query.filter_by(title=title).first()
    db.session.delete(task)
    db.session.commit()
    flash(f'The task {task.title} deleted.')
    return redirect(url_for('home'))


# ==========================================
# END OF AUTHENTICATED USER
# ==========================================
