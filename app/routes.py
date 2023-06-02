from app import app, db
from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, \
    ResetPasswordForm, CreateTaskForm, TaskCommentForm
from app.models import User, Task, TaskComment
from werkzeug.urls import url_parse
from app.email import send_password_reset_email
from datetime import datetime, date


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
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        flash(f'Welcome {user.username}.')
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
        db.session.add(user)
        db.session.commit()
        flash('Successfully registered. Log in to continue.')
        return redirect(url_for('login'))
    return render_template(
        'auth/register.html',
        title='Register',
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
            due_date=form.due_date.data,
            status='Active',
            author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Task created.')
        return redirect(url_for('home'))
    tasks = current_user.tasks.order_by(Task.timestamp.desc()).all()
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
        db.session.commit()
        flash('Edits saved.')
        return redirect(url_for('edit_task', title=task.title))
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
    flash('Task completed.')
    return redirect(url_for('home'))


@app.route('/delete-task/<title>', methods=['GET', 'POST'])
@login_required
def delete_task(title):
    task = Task.query.filter_by(title=title).first()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.')
    return redirect(url_for('home'))


# ==========================================
# END OF AUTHENTICATED USER
# ==========================================
