from app import  db
from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_user, logout_user, login_required
from app.auth.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, \
    ResetPasswordForm, VerifyForm
from app.models import User
from werkzeug.urls import url_parse
from app.auth.email import send_password_reset_email, thank_you_user
from app.twilio_verify_api import check_email_verification_token,request_email_verification_token
from app.auth import bp

def encrypt_password(password):
    from werkzeug.security import generate_password_hash
    password = generate_password_hash(password)
    return password


# ==========================================
# AUTHENTICATION
# ==========================================

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user.home')
        flash(f'Welcome {user.username}.')
        return redirect(next_page)
    return render_template(
        'auth/login.html',
        title='Login',
        form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        request_email_verification_token(form.email.data)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        session['username'] = form.username.data
        session['email'] = form.email.data
        session['password'] = encrypt_password(form.password.data)
        flash('A token has been sent to your email address. '
              'Enter it below to confirm you have access to your email address.')
        return redirect(url_for('auth.verify_email_token'))
    return render_template(
        'auth/register.html',
        title='Register',
        form=form)


@bp.route('/verify-email-token', methods=['GET', 'POST'])
def verify_email_token():
    """
    User verifies their email address by 
    providing token sent to their inbox
    """
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = VerifyForm()
    if form.validate_on_submit():
        try:
            username = session['username']
            email = session['email']
            password = session['password']

            if check_email_verification_token(email, form.token.data):
                user = User(username=username, email=email)
                user.password_hash = password
                db.session.add(user)
                db.session.commit()
                del session['username']
                del session['email']
                del session['password']

                # Send user a thank you email
                thank_you_user(username, email)

                flash('Registered successfully. Please check you inbox and login to continue.')
                return redirect(url_for('auth.login'))
            form.token.errors.append('Invalid token.')
        except KeyError as e:
            flash('Try registering again.')
            return redirect(url_for('auth.register'))
    return render_template(
        'auth/verify_email_token.html',
        title='Verify Your Email',
        form=form)


@bp.route('/request-password-reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Send user an email
            send_password_reset_email(user)
        # Conceal database information by giving general information
        flash("Check your email for the instructions to reset your password")
        return redirect(url_for("auth.login"))
    return render_template(
        'auth/request_password_reset.html',
        title='Request Password Reset',
        form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    # Verify request token
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    # If verified, proceed to allow for password reset
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset. Log in to continue")
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password.html',
        title='Reset Password',
        form=form)

# ==========================================
# END OF AUTHENTICATION
# ==========================================
