from app.main import bp
from flask import render_template, url_for, redirect
from flask_login import current_user


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template(
        'index.html',
        title='Welcome To TaskMate!')
