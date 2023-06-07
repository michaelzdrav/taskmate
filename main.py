from app import create_app, db, cli
from app.models import User, Task, TaskComment

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    '''Access app instance and models via the flask shell command'''
    return dict(
        db=db,
        User=User,
        Task=Task,
        TaskComment=TaskComment
    )
