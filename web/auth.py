import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User
# from web.old_db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        user = User.query.filter_by(username=username).first()
        if user is not None and user.username == username:
            error = f"User {username} is already registered."


        if error is None:
            try:
                new_user = User(username=username, password=generate_password_hash(password))    
                db.session.add(new_user)
                db.session.commit()
            except db.IntegrityError:

                current_app.logger.info("User %s is already registered.", username)
                error = f"User {username} is already registered."
            else:
                current_app.logger.info("User %s has been registered.", username)
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        user = User.query.filter_by(username=username).first()

        # user = db.execute(
        #     'SELECT * FROM user WHERE username = ?', (username,)
        # ).fetchone()

        if user is None:
            current_app.logger.info("Failed login - Incorrect username: %s", username)
            error = 'Incorrect username.'
            
        elif not check_password_hash(user.password, password):
            current_app.logger.info("Failed login - Incorrect password for username: %s", username)
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            session['username'] = username
            current_app.logger.info("User_id %s, User %s has logged in.", user.id, username)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter(User.id == user_id).first()

@bp.route('/logout')
def logout():
    current_app.logger.info("User_id %s, User %s has logged out.", session.get('user_id'), session.get('username'))
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

