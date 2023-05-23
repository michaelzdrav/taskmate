from flask_mail import Message
from . import mail
from flask import render_template, g, current_app

# TODO extend mail to be sent under all use-cases, not just title, due_date and description
# TODO generalise to send_email, and pass in msg.body, msg.html as well
def send_new_task_email(title, due_date=None, description=None):
    app = current_app._get_current_object()
    # TODO get sender from ADMIN config
    # TODO parameterise recipients
    msg = Message('[TaskMate] New task created', sender="admin@gmail.com", recipients=['your-email@example.com', 'michael@gmail.com'])
    body = {"title": "", "due_date": "", "description": ""}
    if title:
        body['title'] = title
    # TODO add status
    # if status:
    #     body['status'] = status
    if due_date:
        body['due_date'] = due_date
    if description:
        body['description'] = description
    if not g:
        exit(0)

    msg.body = render_template('email/new_task.txt',user=g.user,body=body)
    msg.html = render_template('email/new_task.html',user=g.user,body=body)

    app.logger.info('Sending email %s to %s', body['title'])
    mail.send(msg)
