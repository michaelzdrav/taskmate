from flask import current_app, g
from web.db import get_db
from werkzeug.exceptions import abort

def get_active_tasks(user_id):
    current_app.logger.debug("Querying database for active tasks.")
    db = get_db()
    return db.execute(
        "SELECT t.id, username, author_id, created, due_date, title, body, status"
        " FROM task t JOIN user u ON t.author_id = u.id"
        ' WHERE t.author_id = ? AND status != "DONE"'
        " ORDER BY created DESC",
        (user_id,),
    ).fetchall()


def get_overdue_tasks(user_id):
    current_app.logger.debug("Querying database for overdue tasks.")
    db = get_db()
    return db.execute(
        "SELECT t.id, status, created"
        " FROM task t JOIN user u ON t.author_id = u.id"
        ' WHERE t.author_id = ? AND status = "OVERDUE"'
        " ORDER BY created DESC",
        (user_id,),
    ).fetchall()


def get_comments(user_id):
    current_app.logger.debug("Querying database for comments.")
    db = get_db()
    return db.execute(
        "SELECT tc.id, tc.task_id, tc.content, tc.created, t.author_id, u.id"
        " FROM task t JOIN user u ON t.author_id = u.id"
        " JOIN task_comment tc ON tc.task_id = t.id"
        ' WHERE t.author_id = ? AND status != "DONE"'
        " ORDER BY tc.task_id ASC",
        (user_id,),
    ).fetchall()

def get_task(id, check_user=True):
    current_app.logger.debug("Querying database for task %s.", id)
    db = get_db()
    task = (
        db.execute(
            "SELECT t.id, author_id, username, created, due_date, title, body, status"
            " FROM task t JOIN user u ON t.author_id = u.id"
            " WHERE t.id = ?",
            (id,),
        )
        .fetchone()
    )

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_user and task["author_id"] != g.user["id"]:
        abort(403)

    return task

def set_task_overdue(id):
    get_task(id)
    current_app.logger.info("Setting task [id] %s as overdue", id)
    db = get_db()
    db.execute('UPDATE task SET status = "OVERDUE" WHERE id = ?', (id,))
    db.commit()