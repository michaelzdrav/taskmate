from flask import current_app, g
from werkzeug.exceptions import abort
from . import db
from .models import User, Task, TaskComment, Tenant


def get_active_tasks(user_id):
    current_app.logger.debug("Querying database for active tasks.")

    query = (
        Task.query.with_entities(
            Task.id,
            User.username,
            Task.author_id,
            Task.created,
            Task.due_date,
            Task.title,
            Task.body,
            Task.status,
            Task.tenant_id,
        )
        .join(User, Task.author_id == User.id)
        .filter(
            Task.author_id == user_id,
            Task.status != "DONE",
            User.tenant_id == g.get("tenant_id"),
            Task.tenant_id == g.get("tenant_id"),
        )
        .order_by(Task.created.desc())
    )
    return query.all()


def get_latest_task(user_id):
    current_app.logger.debug("Querying database for latest task.")

    return (
        Task.query.with_entities(
            Task.id,
            User.username,
            Task.author_id,
            Task.created,
            Task.due_date,
            Task.title,
            Task.body,
            Task.status,
            Task.tenant_id,
        )
        .join(User, Task.author_id == User.id)
        .filter(
            Task.author_id == user_id,
            Task.status != "DONE",
            User.tenant_id == g.get("tenant_id"),
            Task.tenant_id == g.get("tenant_id"),
        )
        .order_by(Task.created.desc())
        .first()
    )


def get_done_tasks(user_id):
    current_app.logger.debug("Querying database for done tasks.")

    return (
        Task.query.with_entities(
            Task.id,
            User.username,
            Task.author_id,
            Task.created,
            Task.due_date,
            Task.title,
            Task.body,
            Task.status,
            Task.tenant_id,
        )
        .join(User, Task.author_id == User.id)
        .filter(
            Task.author_id == user_id,
            Task.status == "DONE",
            User.tenant_id == g.get("tenant_id"),
            Task.tenant_id == g.get("tenant_id"),
        )
        .order_by(Task.created.desc())
        .all()
    )


def get_overdue_tasks(user_id):
    current_app.logger.debug("Querying database for overdue tasks.")

    return (
        Task.query.with_entities(Task.id, Task.status, Task.created)
        .join(User, Task.author_id == User.id)
        .filter(
            Task.author_id == user_id,
            Task.status == "OVERDUE",
            User.tenant_id == g.get("tenant_id"),
            Task.tenant_id == g.get("tenant_id"),
        )
        .order_by(Task.created.desc())
        .all()
    )


def get_comments_for_task(task_id):
    current_app.logger.debug("Querying database for comments for a single task.")

    return (
        db.session.query(
            TaskComment.id,
            TaskComment.task_id,
            TaskComment.content,
            TaskComment.created,
            TaskComment.tenant_id,
            Task.author_id,
            Task.tenant_id,
        )
        .join(Task, TaskComment.task_id == Task.id)
        .join(User, Task.author_id == User.id)
        .filter(
            TaskComment.task_id == task_id,
            User.tenant_id == g.get("tenant_id"),
            TaskComment.tenant_id == g.get("tenant_id"),
            Task.tenant_id == g.get("tenant_id"),
        )
        .order_by(TaskComment.task_id.asc())
        .all()
    )


def get_comments(user_id):
    current_app.logger.debug("Querying database for comments.")

    return (
        db.session.query(
            TaskComment.id,
            TaskComment.task_id,
            TaskComment.content,
            TaskComment.created,
            TaskComment.tenant_id,
        )
        .join(Task, TaskComment.task_id == Task.id)
        .filter(
            Task.author_id == user_id,
            Task.status != "DONE",
            Task.tenant_id == g.get("tenant_id"),
            TaskComment.tenant_id == g.get("tenant_id"),
        )
        .order_by(TaskComment.task_id.asc())
        .all()
    )


def delete_single_comment(id):
    current_app.logger.debug("Deleting comment id %s from db.", id)

    task_comment = TaskComment.query.filter_by(
        id=id, tenant_id=g.get("tenant_id")
    ).first()

    if task_comment:
        db.session.delete(task_comment)
        db.session.commit()


def get_task(id, check_user=True):
    current_app.logger.debug("Querying database for task %s.", id)

    task = Task.query.filter_by(id=id, tenant_id=g.get("tenant_id")).first()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_user and task.author_id != g.user.id:
        abort(403)

    return task


def get_latest_done_task(user_id):
    current_app.logger.debug("Querying database for latest task.")

    return (
        Task.query.with_entities(
            Task.id,
            User.username,
            User.tenant_id,
            Task.author_id,
            Task.created,
            Task.due_date,
            Task.title,
            Task.body,
            Task.status,
            Task.tenant_id,
        )
        .join(User, Task.author_id == User.id)
        .filter(
            Task.author_id == user_id,
            Task.status == "DONE",
            Task.tenant_id == g.get("tenant_id"),
            User.tenant_id == g.get("tenant_id"),
        )
        .order_by(Task.created.desc())
        .first()
    )


def get_status(id, check_user=True):
    current_app.logger.debug("Querying database for status of task %s.", id)

    status = (
        Task.query.with_entities(Task.id, Task.author_id, Task.status, Task.tenant_id)
        .join(User, Task.author_id == User.id)
        .filter(
            Task.id == id,
            Task.status == "DONE",
            User.tenant_id == g.get("tenant_id"),
            Task.tenant_id == g.get("tenant_id"),
        )
        .first()
    )

    if status is None:
        abort(404, f"Done task id {id} doesn't exist.")

    if check_user and status.author_id != g.user.id:
        abort(403)

    return status


def get_done_task(id, check_user=True):
    current_app.logger.debug("Querying database for done task %s.", id)

    task = (
        Task.query.with_entities(
            Task.id,
            Task.author_id,
            User.username,
            Task.created,
            Task.due_date,
            Task.title,
            Task.body,
            Task.status,
            Task.tenant_id,
            User.tenant_id,
        )
        .join(User, Task.author_id == User.id)
        .filter(
            Task.id == id,
            Task.status == "DONE",
            User.tenant_id == g.get("tenant_id"),
            Task.tenant_id == g.get("tenant_id"),
        )
        .first()
    )

    if task is None:
        abort(404, f"Done task id {id} doesn't exist.")

    if check_user and task.author_id != g.user.id:
        abort(403)

    return task


def set_task_overdue(id):
    current_app.logger.info("Setting task [id] %s as overdue", id)
    task = get_task(id)
    if task:
        task.status = "OVERDUE"
        db.session.commit()


def get_timezone_setting(tenant_id):
    try:
        tenant = None
        if tenant_id == g.get("tenant_id"):
            tenant = Tenant.query.get(tenant_id)

        if tenant:
            timezone = tenant.timezone
            current_app.logger.info(
                "Got timezone %s for [tenant_id] %s, User [id] %s.",
                timezone,
                tenant_id,
                g.user.id,
            )
            return timezone
        else:
            current_app.logger.error(
                "Tenant not found for [tenant_id] %s, User [id] %s.",
                tenant_id,
                g.user.id,
            )
            return None

    except Exception as e:
        current_app.logger.error(
            "An error occurred while getting the timezone: %s, for [tenant_id] %s, User [id] %s",
            str(e),
            tenant_id,
            g.user.id,
        )
        return None


def set_timezone_setting(tenant_id, timezone):
    try:
        tenant = Tenant.query.get(tenant_id)

        if tenant:
            tenant.timezone = timezone
            db.session.commit()
            current_app.logger.info(
                "Timezone set to %s for [tenant_id] %s, User [id] %s.",
                timezone,
                tenant_id,
                g.user.id,
            )
            return True
        else:
            current_app.logger.error(
                "Tenant not found for [tenant_id] %s, User [id] %s.",
                tenant_id,
                g.user.id,
            )
            return False
    except Exception as e:
        current_app.logger.error(
            "An error occurred while setting the timezone: %s, for [tenant_id] %s, User [id] %s",
            str(e),
            tenant_id,
            g.user.id,
        )
        return None
    pass
