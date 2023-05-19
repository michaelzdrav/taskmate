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
)

@bp.route("/")
def index():
    try:
        if g.user["id"]:
            db = get_db()
            tasks = get_active_tasks(g.user["id"])
            overdue = get_overdue_tasks(g.user["id"])
            comments = get_comments(g.user["id"])

            return render_template(
                "landing/index.html", tasks=tasks, overdue=overdue, comments=comments
            )
    except TypeError as e:
        current_app.logger.exception("An error occurred: %s", e)
        current_app.logger.info("User is not logged in.")
        return render_template("landing/index.html")


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

                send_new_task_email(title)
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

                send_new_task_email(title, body)
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

                send_new_task_email(title, due_date)
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

            send_new_task_email(title, due_date, body)
            return redirect(url_for("landing.index"))
    return render_template("landing/create.html")


@bp.route("/done", methods=("GET",))
@login_required
def done():
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

            return render_template(
                "landing/done_tasks.html", tasks=tasks, comments=comments
            )
    except TypeError as e:
        current_app.logger.exception("An error occurred: %s", e)
        current_app.logger.info("User is not logged in.")
        return render_template("landing/index.html")


@bp.route("/<int:id>/comment", methods=("POST",))
@login_required
def add_comment(id):
    app = current_app._get_current_object()
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
        return redirect(url_for("landing.index"))
    else:
        return redirect(url_for("landing.done"))


@bp.route("/<int:id>/deletecomment", methods=("POST",))
@login_required
def delete_comment(id):
    current_app.logger.info("[Soft Error] delete_comment() not yet implemented.")
    return redirect(url_for("landing.index"))

    # current_app.logger.info("Deleting comment [id]", id)
    # # TODO add a get_task_comment
    # # task = get_task(id)
    # db = get_db()
    # error = None
    # task = db.execute(
    #     "SELECT t.id FROM task t JOIN task_comment tc ON t.id = tc.task_id"
    #     "  WHERE tc.task_id = ?",
    #     (id,),
    # ).fetchone

    # if not task:
    #     error = "Cannot find task."

    # if error is not None:
    #     flash(error)
    # else:
    #     db.execute("DELETE FROM task_comment WHERE task_id = ?", (id,))
    #     db.commit()

    # if task["status"] != "DONE":
    #     return redirect(url_for("landing.index"))
    # else:
    #     return redirect(url_for("landing.done"))


@bp.route("/<int:id>/done", methods=("POST",))
@login_required
def move_done(id):
    app = current_app._get_current_object()
    current_app.logger.info("Setting task [id] %s status to DONE", id)
    get_task(id)
    db = get_db()
    db.execute('UPDATE task SET status = "DONE" WHERE id = ?', (id,))

    db.commit()
    return redirect(url_for("landing.index"))


@bp.route("/<int:id>/update", methods=("POST", "GET"))
@login_required
def update_task(id):
    app = current_app._get_current_object()
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

            db.execute(
                "UPDATE task SET title = ?, due_date = ?, body = ?, status = ?"
                " WHERE id = ?",
                (title, due_date, body, status, id),
            )
            db.commit()

        return redirect(url_for("landing.index"))

    task = get_task(id)
    return render_template("landing/edit.html", task=task)


# TODO implement this to run with daily check
# @bp.route("/<int:id>/overdue", methods=("POST",))
# @login_required
# def move_overdue(id):
#     app = current_app._get_current_object()
#     set_task_overdue(id)
#     return redirect(url_for("landing.index"))


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    app = current_app._get_current_object()
    task = get_task(id)
    if task["status"] == "ACTIVE" or task["status"] == "OVERDUE":
        db = get_db()
        db.execute("DELETE FROM task WHERE id = ?", (id,))
        db.commit()
        return redirect(url_for("landing.index"))
    else:
        db = get_db()
        db.execute("DELETE FROM task WHERE id = ?", (id,))
        db.commit()
        return redirect(url_for("landing.done"))
