from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from werkzeug.exceptions import abort

from web.auth import login_required
from web.db import get_db

from datetime import datetime, date

bp = Blueprint('landing', __name__)


@bp.route('/')
def index():
    try:
        if g.user['id']:
            db = get_db()
            tasks = db.execute(
                'SELECT t.id, username, author_id, created, due_date, title, body, status'
                ' FROM task t JOIN user u ON t.author_id = u.id'
                ' WHERE t.author_id = ? AND status != "DONE"'
                ' ORDER BY created DESC', (g.user['id'], )).fetchall()

            overdue = db.execute(
                'SELECT t.id, status, created'
                ' FROM task t JOIN user u ON t.author_id = u.id'
                ' WHERE t.author_id = ? AND status = "OVERDUE"'
                ' ORDER BY created DESC', (g.user['id'], )).fetchall()

            comments = db.execute(
                'SELECT tc.id, tc.task_id, tc.content, tc.created, t.author_id, u.id'
                ' FROM task t JOIN user u ON t.author_id = u.id'
                ' JOIN task_comment tc ON tc.task_id = t.id'
                ' WHERE t.author_id = ? AND status != "DONE"'
                ' ORDER BY tc.task_id ASC', (g.user['id'], )).fetchall()

            return render_template('landing/index.html',
                                   tasks=tasks,
                                   overdue=overdue,
                                   comments=comments)
    except TypeError:
        print("User is not logged in")
        return render_template('landing/index.html')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        due_date = request.form['due_date']
        body = request.form['body']
        print("due date is:", due_date)
        print("title is:", title)
        print("body is:", body)
        error = None
        status = "ACTIVE"

        if due_date != "":
            date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
            date_today = date.today()

            if date_obj <= date_today:
                status = "OVERDUE"

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()

            if due_date == "" and body == "":
                print("no body no due_date")  # no body but no due_date
                db.execute(
                    'INSERT INTO task (author_id, title)'
                    ' VALUES (?, ?)', (g.user['id'], title))
                db.commit()

                return redirect(url_for('landing.index'))

            if due_date == "" and body != "":
                print(
                    "have body but not due_date")  # have body but not due_date
                db.execute(
                    'INSERT INTO task (author_id, title, body)'
                    ' VALUES (?, ?, ?)', (g.user['id'], title, body))
                db.commit()

                return redirect(url_for('landing.index'))

            if due_date != "" and body == "":
                print("due_date not none and body is none"
                      )  # have due_date but not body
                db.execute(
                    'INSERT INTO task (author_id, due_date, title, status)'
                    ' VALUES (?, ?, ?, ?)',
                    (g.user['id'], due_date, title, status))
                db.commit()

                return redirect(url_for('landing.index'))

            print("have both due_date and body")  # have both due_date and body
            db.execute(
                'INSERT INTO task (author_id, due_date, title, body, status)'
                ' VALUES (?, ?, ?, ?, ?)',
                (g.user['id'], due_date, title, body, status))
            db.commit()

            return redirect(url_for('landing.index'))
    return render_template('landing/create.html')


@bp.route('/done', methods=('GET', ))
@login_required
def done():
    try:
        if g.user['id']:
            db = get_db()
            tasks = db.execute(
                'SELECT t.id, username, author_id, created, due_date, title, body, status'
                ' FROM task t JOIN user u ON t.author_id = u.id'
                ' WHERE t.author_id = ? AND status = "DONE"'
                ' ORDER BY created DESC', (g.user['id'], )).fetchall()

            comments = db.execute(
                'SELECT tc.id, tc.task_id, tc.content, tc.created, t.author_id, u.id'
                ' FROM task t JOIN user u ON t.author_id = u.id'
                ' JOIN task_comment tc ON tc.task_id = t.id'
                ' WHERE t.author_id = ? AND status = "DONE"'
                ' ORDER BY tc.task_id ASC', (g.user['id'], )).fetchall()

            return render_template('landing/done_tasks.html',
                                   tasks=tasks,
                                   comments=comments)
    except TypeError:
        print("User is not logged in")
        return render_template('landing/index.html')


@bp.route('/<int:id>/comment', methods=('POST', ))
@login_required
def add_comment(id):
    print("Adding comment on: ", id)
    task = get_task(id)
    db = get_db()
    comment = request.form['comment']
    print("comment is:", comment)
    error = None

    if not comment:
        error = 'Comment is required.'

    db.execute('INSERT INTO task_comment (task_id, content)'
               ' VALUES (?, ?)', (id, comment))

    db.commit()
    if task['status'] != "DONE":
        return redirect(url_for('landing.index'))
    else:
        return redirect(url_for('landing.done'))


@bp.route('/<int:id>/deletecomment', methods=('POST', ))
@login_required
def delete_comment(id):
    print("Deleting comment on: ", id)
    # TODO add a get_task_comment
    # task = get_task(id)
    db = get_db()
    error = None
    task = db.execute(
        'SELECT t.id FROM task t JOIN task_comment tc ON t.id = tc.task_id'
        '  WHERE tc.task_id = ?', (id, )).fetchone

    if not task:
        error = 'Cannot find task.'

    if error is not None:
        flash(error)
    else:
        db.execute('DELETE FROM task_comment WHERE task_id = ?', (id, ))
        db.commit()

    if task['status'] != "DONE":
        return redirect(url_for('landing.index'))
    else:
        return redirect(url_for('landing.done'))


@bp.route('/<int:id>/done', methods=('POST', ))
@login_required
def move_done(id):
    print("Moving task to done: ", id)
    get_task(id)
    db = get_db()
    db.execute('UPDATE task SET status = "DONE" WHERE id = ?', (id, ))

    db.commit()
    return redirect(url_for('landing.index'))


@bp.route('/<int:id>/update', methods=('POST', 'GET'))
@login_required
def update_task(id):
    if request.method == 'POST':
        title = request.form['title']
        due_date = request.form['due_date']
        body = request.form['body']
        print("new due date is:", due_date)
        print("new title is:", title)
        print("new body is:", body)
        error = None
        status = "ACTIVE"

        if due_date != "":
            date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
            date_today = date.today()

            if date_obj <= date_today:
                status = "OVERDUE"

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()

            db.execute(
                'UPDATE task SET title = ?, due_date = ?, body = ?, status = ?'
                ' WHERE id = ?', (title, due_date, body, status, id))
            db.commit()

        return redirect(url_for('landing.index'))

    print("Task edit: ", id)
    task = get_task(id)
    return render_template('landing/edit.html', task=task)


@bp.route('/<int:id>/overdue', methods=('POST', ))
@login_required
def move_overdue(id):
    print("Moving task to overdue: ", id)
    get_task(id)
    db = get_db()
    db.execute('UPDATE task SET status = "OVERDUE" WHERE id = ?', (id, ))

    db.commit()
    return redirect(url_for('landing.index'))


@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
    task = get_task(id)
    print("TASK IS:", task['status'])
    if task['status'] == "ACTIVE" or task['status'] == "OVERDUE":
        db = get_db()
        db.execute('DELETE FROM task WHERE id = ?', (id, ))
        db.commit()
        return redirect(url_for('landing.index'))
    else:
        db = get_db()
        db.execute('DELETE FROM task WHERE id = ?', (id, ))
        db.commit()
        return redirect(url_for('landing.done'))


def get_task(id, check_user=True):
    task = get_db().execute(
        'SELECT t.id, author_id, username, created, due_date, title, body, status'
        ' FROM task t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?', (id, )).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_user and task['author_id'] != g.user['id']:
        abort(403)

    return task
