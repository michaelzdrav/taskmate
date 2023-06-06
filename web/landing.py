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

from .models import Task, User, TaskComment
from web.auth import login_required
from . import db

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

from functools import wraps
from flask import current_app


def mobile_check():
    user_agent_string = request.headers.get("User-Agent")
    current_app.logger.info("IP: %s. User-Agent: %s", request.remote_addr, user_agent_string)
    if "Mobile" in user_agent_string or "iPhone" in user_agent_string:
        return True


@bp.route("/", methods=("GET",))
def index(id=None):
    try:
        if g.user and g.user.id:
            tasks = get_active_tasks(g.user.id)
            overdue = get_overdue_tasks(g.user.id)
            comments = get_comments(g.user.id)
            latest_task = get_latest_task(g.user.id)

            if id is not None:
                view_task = get_task(id)

                if mobile_check():
                    return render_template(
                        "mobile/index.html",
                        tasks=tasks,
                        overdue=overdue,
                        comments=comments,
                        view=latest_task,
                        status="Active"
                    )

                return render_template(
                    "landing/index.html",
                    tasks=tasks,
                    overdue=overdue,
                    comments=comments,
                    view=view_task,
                )
            else:
                if mobile_check():

                    return render_template(
                        "mobile/index.html",
                        tasks=tasks,
                        overdue=overdue,
                        comments=comments,
                        view=latest_task,
                        status="Active",
                    )

                return render_template(
                    "landing/index.html",
                    tasks=tasks,
                    overdue=overdue,
                    comments=comments,
                    view=latest_task,
                )
        else:
            current_app.logger.debug("User is not logged in.")
            return render_template("landing/index.html")
    except TypeError as e:
        current_app.logger.debug("User is not logged in.")
        return render_template("landing/index.html")


@bp.route("/<int:id>/view", methods=("POST",))
def load_view(id):
    if id is not None and mobile_check():
        return redirect(url_for("landing.task_view", id=id,status="Active"))

    return index(id)

@bp.route("/<int:id>/doneview", methods=("POST",))
def load_doneview(id):
    if id is not None and mobile_check():
        return redirect(url_for("landing.task_view", id=id,status="Done"))

    return done(id)

@bp.route("/mobile/<int:id>")
def task_view(id):
    if g.user and g.user.id:
        if id is not None:
            view_task = get_task(id)
            comments = get_comments_for_task(id)
            status = request.args.get("status") 

            return render_template(
                "mobile/task.html",
                view=view_task,
                comments=comments,
                status=status
            )

    return render_template("mobile/index.html", )


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
            if due_date == "" and body == "":
                current_app.logger.info(
                    "Inserting task [author_id] %s, [title] %s.", g.user.id, title
                )
                task = Task(author_id=g.user.id, title=title)
                db.session.add(task)
                db.session.commit()

                # send_new_task_email(title)
                return redirect(url_for("landing.index"))

            if due_date == "" and body != "":
                current_app.logger.info(
                    "Inserting task [author_id] %s, [title] %s, [body] %s.",
                    g.user.id,
                    title,
                    body,
                )
                task = Task(author_id=g.user.id, title=title)
                db.session.add(task)
                db.session.commit()

                # send_new_task_email(title, body)
                return redirect(url_for("landing.index"))

            if due_date != "" and body == "":
                current_app.logger.info(
                    "Inserting task [author_id] %s, [title] %s, [due_date] %s, [status] %s.",
                    g.user.id,
                    title,
                    due_date,
                    status,
                )

                task = Task(
                    author_id=g.user.id, due_date=due_date, title=title, status=status
                )
                db.session.add(task)
                db.session.commit()

                # send_new_task_email(title, due_date)
                return redirect(url_for("landing.index"))

            current_app.logger.info(
                "Inserting task [author_id] %s, [title] %s, [body] %s, [due_date] %s, [status] %s.",
                g.user.id,
                title,
                body,
                due_date,
                status,
            )

            task = Task(
                author_id=g.user.id,
                due_date=due_date,
                title=title,
                body=body,
                status=status,
            )
            db.session.add(task)
            db.session.commit()

            # send_new_task_email(title, due_date, body)
            return redirect(url_for("landing.index"))
    return render_template("landing/create.html")


@bp.route("/done", methods=("GET",))
def done(id=None):
    try:
        if g.user.id:
            tasks = (
                Task.query.join(User)
                .filter(
                    Task.author_id == User.id,
                    Task.author_id == g.user.id,
                    Task.status == "DONE",
                )
                .order_by(Task.created.desc())
                .all()
            )

            comments = (
                TaskComment.query.join(Task)
                .join(User)
                .filter(Task.author_id == g.user.id, Task.status == "DONE")
                .order_by(TaskComment.task_id.asc())
                .with_entities(
                    TaskComment.id,
                    TaskComment.task_id,
                    TaskComment.content,
                    TaskComment.created,
                )
                .all()
            )

            if id is not None:
                latest_task = get_done_task(id)

                if mobile_check():
                    return render_template(
                        "mobile/index.html",
                        tasks=tasks,
                        comments=comments,
                        view=latest_task,
                        status="Done"
                    )

                return render_template(
                    "landing/done_tasks.html",
                    tasks=tasks,
                    comments=comments,
                    view=latest_task,
                )

            latest = get_latest_done_task(g.user.id)

            if mobile_check():
                return render_template(
                    "mobile/index.html",
                    tasks=tasks,
                    comments=comments,
                    view=latest,
                    status="Done"
                )

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
    error = None

    if not comment:
        error = "Comment is required."
    if error is not None:
        flash(error)

    task_comment = TaskComment(task_id=id, content=comment)
    db.session.add(task_comment)
    db.session.commit()

    if task.status != "DONE":
        return load_view(id)
        # return redirect(url_for("landing.index"))
    else:
        return load_doneview(id)


@bp.route("/<int:id>/deletecomment/<int:task>", methods=("POST",))
@login_required
def delete_comment(id, task):
    current_app.logger.info("Deleting comment [id] %s", id)
    error = None
    print("id is: ", id)
    print("taskid is: ", task)
    if not Task.query.get(task):
        error = "Cannot delete comment as task does not exist."
    if not TaskComment.query.get(id):
        error = "Cannot delete comment as comment does not exist."
    else:
        delete_single_comment(id)
    if error is not None:
        flash(error)

    received_task = get_task(task)
    if received_task.status == "DONE":
        return load_doneview(task)
    else:
        return load_view(task)


@bp.route("/<int:id>/done", methods=("POST",))
@login_required
def move_done(id):
    current_app.logger.info("Setting task [id] %s status to DONE", id)
    error = None
    if not get_task(id):
        error = "Task cannot be move to done as it does not exist."
    else:
        task = get_task(id)
        task.status = "DONE"
        db.session.commit()
    if error is not None:
        flash(error)

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

        if not get_task(id):
            error = "Task does not exist."
        else:
            task = get_task(id)

        if not title:
            error = "Title is required."
        else:
            task.title = title

        if body:
            task.body = body

        if error is not None:
            flash(error)
        else:
            current_app.logger.info(
                "Updating task [id] %s, setting [title] %s, [due_date] %s, [body] %s, [status] %s.",
                id,
                title,
                due_date,
                body,
                status,
            )

            if due_date != "":
                date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
                date_today = date.today()
                task.due_date = due_date
                if date_obj <= date_today:
                    status = "OVERDUE"
            else:
                task.due_date = None

            task.status = status
            db.session.commit()

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
    if task.status == "ACTIVE" or task.status == "OVERDUE":
        # if task["status"] == "ACTIVE" or task["status"] == "OVERDUE":
        current_app.logger.info("Deleting task [id] %s.", id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for("landing.index"))
    else:
        current_app.logger.info("Deleting task [id] %s.", id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for("landing.done"))
