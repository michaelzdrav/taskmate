from datetime import datetime
from app.task_reminders import send_overdue_task_reminder


def register(app):
    '''
    Commandline enhancements
    
    Similar to: flask init, flask run etc
    
    These are custom CLI commands
    
    You can run this comamnd to see available commands:
    flask task --help 
    
    Once found, run the command as (example):
    flask task overdue

    This will send the overdue email notification to all db users with overdue tasks
    '''
    @app.cli.group()
    def task():
        """Remind users of their overdue tasks"""
        pass


    @task.command()
    def overdue():
        """Remind user of an overdue task"""
        send_overdue_task_reminder()
        print(str(datetime.utcnow()), 'Overdue task reminder sent to all users\n\n')
