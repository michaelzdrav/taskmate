from flask import render_template, current_app
from  app.email import send_email


# Password reset email

def send_password_reset_email(user):
    """Send password reset email"""
    token = user.get_reset_password_token()
    send_email(
        "[TaskMate] Reset Your Password",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template(
            "emails/auth/reset_password.txt", user=user, token=token),
        html_body=render_template(
            "emails/auth/reset_password.html", user=user, token=token))


# Thank you for registration

def thank_you_user(username, email):
    """Email sent to user"""
    send_email(
        "[TaskMate] Thank you for your registration.",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email],
        text_body=render_template(
            "emails/auth/thank_you_signup.txt", username=username),
        html_body=render_template(
            "emails/auth/thank_you_signup.html", username=username))
