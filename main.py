from app import app, db
from app.models import User, Task, TaskComment


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Task=Task,
        TaskComment=TaskComment
    )
