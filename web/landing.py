from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)

from web.auth import login_required
from web.db import get_db

from datetime import datetime, date
from .mail import send_new_task_email

bp = Blueprint("landing", __name__)
from .queries import (
    get_active_tasks,
    get_overdue_tasks,
    get_comments,
    get_task,
    set_task_overdue,
    get_done_tasks,
    delete_single_comment,
    get_latest_task,
    get_comments_for_task,
    get_latest_done_task,
    get_done_task,
    get_status,
)


@bp.route("/", methods=("GET",))
def index(id=None):
    try:
        if g.user["id"]:
            db = get_db()
            tasks = get_active_tasks(g.user["id"])
            overdue = get_overdue_tasks(g.user["id"])
            comments = get_comments(g.user["id"])

            latest_task = get_latest_task(g.user["id"])

            if id is not None:
                view_task = get_task(id)

                return render_template(
                    "landing/index.html",
                    tasks=tasks,
                    overdue=overdue,
                    comments=comments,
                    view=view_task,
                )
            else:
                return render_template(
                    "landing/index.html",
                    tasks=tasks,
                    overdue=overdue,
                    comments=comments,
                    view=latest_task,
                )
    except TypeError as e:
        current_app.logger.debug("User is not logged in.")
        return render_template("landing/index.html")


@bp.route("/<int:id>/view", methods=("POST",))
def load_view(id):
    return index(id)


@bp.route("/<int:id>/doneview", methods=("POST",))
def load_doneview(id):
    return done(id)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        due_date = request.form["due_date"]
        body = request.form["body"]
        error = None
        status = "ACTIVE"

        if due_date:
            try:
                date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
                date_today = date.today()

                if date_obj <= date_today:
                    status = "OVERDUE"
            except ValueError:
                error = "Invalid due date format. Please use YYYY-MM-DD."

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()

            if due_date == "" and body == "":
                current_app.logger.info(
                    "Inserting task [author_id] %s, [title] %s.", g.user["id"], title
                )
                db.execute(
                    "INSERT INTO task (author_id, title)" " VALUES (?, ?)",
                    (g.user["id"], title),
                )
                db.commit()

                # send_new_task_email(title)
                return redirect(url_for("landing.index"))

            if due_date == "" and body != "":
                current_app.logger.info(
                    "Inserting task [author_id] %s, [title] %s, [body] %s.",
                    g.user["id"],
                    title,
                    body,
                )
                db.execute(
                    "INSERT INTO task (author_id, title, body)" " VALUES (?, ?, ?)",
                    (g.user["id"], title, body),
                )
                db.commit()

                # send_new_task_email(title, body)
                return redirect(url_for("landing.index"))

            if due_date != "" and body == "":
                current_app.logger.info(
                    "Inserting task [author_id] %s, [title] %s, [due_date] %s, [status] %s.",
                    g.user["id"],
                    title,
                    due_date,
                    status,
                )
                db.execute(
                    "INSERT INTO task (author_id, due_date, title, status)"
                    " VALUES (?, ?, ?, ?)",
                    (g.user["id"], due_date, title, status),
                )
                db.commit()

                # send_new_task_email(title, due_date)
                return redirect(url_for("landing.index"))

            current_app.logger.info(
                "Inserting task [author_id] %s, [title] %s, [body] %s, [due_date] %s, [status] %s.",
                g.user["id"],
                title,
                body,
                due_date,
                status,
            )
            db.execute(
                "INSERT INTO task (author_id, due_date, title, body, status)"
                " VALUES (?, ?, ?, ?, ?)",
                (g.user["id"], due_date, title, body, status),
            )
            db.commit()

            # send_new_task_email(title, due_date, body)
            return redirect(url_for("landing.index"))
    return render_template("landing/create.html")


@bp.route("/done", methods=("GET",))
def done(id=None):
    try:
        if g.user["id"]:
            db = get_db()
            tasks = db.execute(
                "SELECT t.id, username, author_id, created, due_date, title, body, status"
                " FROM task t JOIN user u ON t.author_id = u.id"
                ' WHERE t.author_id = ? AND status = "DONE"'
                " ORDER BY created DESC",
                (g.user["id"],),
            ).fetchall()

            comments = db.execute(
                "SELECT tc.id, tc.task_id, tc.content, tc.created, t.author_id, u.id"
                " FROM task t JOIN user u ON t.author_id = u.id"
                " JOIN task_comment tc ON tc.task_id = t.id"
                ' WHERE t.author_id = ? AND status = "DONE"'
                " ORDER BY tc.task_id ASC",
                (g.user["id"],),
            ).fetchall()

            if id is not None:
                latest_task = get_done_task(id)
                return render_template(
                    "landing/done_tasks.html",
                    tasks=tasks,
                    comments=comments,
                    view=latest_task,
                )

            latest = get_latest_done_task(g.user["id"])
            return render_template(
                "landing/done_tasks.html", tasks=tasks, comments=comments, view=latest
            )
    except TypeError as e:
        current_app.logger.exception("An error occurred: %s", e)
        current_app.logger.info("User is not logged in.")
        return render_template("landing/index.html")


@bp.route("/<int:id>/comment", methods=("POST",))
@login_required
def add_comment(id):
    comment = request.form["comment"]
    current_app.logger.info("Task [id] %s, adding [comment] %s", id, comment)
    task = get_task(id)
    db = get_db()
    error = None

    if not comment:
        error = "Comment is required."

    db.execute(
        "INSERT INTO task_comment (task_id, content)" " VALUES (?, ?)", (id, comment)
    )

    db.commit()
    if task["status"] != "DONE":
        return load_view(id)
        # return redirect(url_for("landing.index"))
    else:
        return load_doneview(id)


@bp.route("/<int:id>/deletecomment/<int:task>", methods=("POST",))
@login_required
def delete_comment(id, task):
    current_app.logger.info("Deleting comment [id] %s", id)
    db = get_db()
    delete_single_comment(id)
    return load_view(task)


@bp.route("/<int:id>/done", methods=("POST",))
@login_required
def move_done(id):
    current_app.logger.info("Setting task [id] %s status to DONE", id)
    get_task(id)
    db = get_db()
    db.execute('UPDATE task SET status = "DONE" WHERE id = ?', (id,))

    db.commit()
    return redirect(url_for("landing.index"))


@bp.route("/<int:id>/update", methods=("POST", "GET"))
@login_required
def update_task(id):
    if request.method == "POST":
        title = request.form["title"]
        due_date = request.form["due_date"]
        body = request.form["body"]
        current_app.logger.info(
            "Updating task [id] %s, [title] %s, [due_date] %s, [body] %s ",
            id,
            title,
            due_date,
            body,
        )
        error = None
        status = "ACTIVE"

        if due_date != "":
            date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
            date_today = date.today()

            if date_obj <= date_today:
                status = "OVERDUE"

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            current_app.logger.info(
                "Updating task [id] %s, setting [title] %s, [due_date] %s, [body] %s, [status] %s.",
                id,
                title,
                due_date,
                body,
                status,
            )

            db.execute(
                "UPDATE task SET title = ?, due_date = ?, body = ?, status = ?"
                " WHERE id = ?",
                (title, due_date, body, status, id),
            )
            db.commit()

            return load_view(id)

    task = get_task(id)
    return render_template("landing/edit.html", task=task)


# TODO implement this to run with daily check
# @bp.route("/<int:id>/overdue", methods=("POST",))
# @login_required
# def move_overdue(id):
#     set_task_overdue(id)
#     return redirect(url_for("landing.index"))


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    task = get_task(id)
    if task["status"] == "ACTIVE" or task["status"] == "OVERDUE":
        current_app.logger.info("Deleting task [id] %s.", id)
        db = get_db()
        db.execute("DELETE FROM task WHERE id = ?", (id,))
        db.commit()
        return redirect(url_for("landing.index"))
    else:
        current_app.logger.info("Deleting task [id] %s.", id)
        db = get_db()
        db.execute("DELETE FROM task WHERE id = ?", (id,))
        db.commit()
        return redirect(url_for("landing.done"))
