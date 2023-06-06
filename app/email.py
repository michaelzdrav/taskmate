from flask_mail import Message
from flask import render_template
from app import mail, app



def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)



# Password reset email

def send_password_reset_email(user):
    """Send password reset email"""
    token = user.get_reset_password_token()
    send_email(
        "[Taskmate] Reset Your Password",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template(
            "emails/reset_password.txt", user=user, token=token),
        html_body=render_template(
            "emails/reset_password.html", user=user, token=token))


# New task email

def send_new_task_email(user):
    """Update user of new task"""
    send_email(
        "[Taskmate] New Task",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template(
            "emails/new_task.txt", user=user),
        html_body=render_template(
            "emails/new_task.html", user=user))