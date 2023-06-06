from app.models import Task, User
from app.email import overdue_task_email_notification


def send_overdue_task_reminder():
    users = User.query.all()
    overdue_tasks = Task.query.filter_by(status='Overdue').all()
    for user in users:
        for task in overdue_tasks:
            if user.tasks:
                overdue_task_email_notification(user, task)
