from flask import render_template, current_app
from  app.email import send_email


# Overdue task email

def overdue_task_email_notification(user, task):
    """Update user of new task"""
    send_email(
        "[TaskMate] Overdue Task",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template(
            "emails/user/overdue_task.txt", user=user, task=task),
        html_body=render_template(
            "emails/user/overdue_task.html", user=user, task=task))
