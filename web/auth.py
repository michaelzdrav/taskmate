import functools
from datetime import date, datetime
from pytz import timezone

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from . import convert_utc_to_timezone
from .models import User, Tenant, Task
from .timezones import get_timezones, get_gmt

bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_current_tenant_id():
    return session.get("tenant_id")


# Check expired tasks on user login
def check_for_expired_tasks():
    tz = session.get("timezone")

    if tz is not None:

        today = datetime.now(timezone("UTC")).date()

        tenants = db.session.query(Tenant).all()

        for tenant in tenants:
            tasks = db.session.query(Task).filter(Task.tenant_id == tenant.id).all()

            for task in tasks:
                if (
                    task.status != "OVERDUE"
                    and task.due_date
                    and task.due_date.date() <= today
                ):
                    task.status = "OVERDUE"

                    current_app.logger.info(
                        "Task Check set task [id] %s in tenancy [id] %s to OVERDUE",
                        task.id,
                        tenant.id,
                    )

            db.session.commit()
        db.session.commit()
    else:
        current_app.logger.info("GMT is none")


@bp.before_app_request
def set_current_tenant():
    g.tenant_id = get_current_tenant_id()


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        tenant_name = username + "_trial"
        timezone = request.form.get("timezone")

        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        # TODO enable below
        # elif not tenant_name:
        #     error = 'Tenant name is required.'

        if timezone in get_timezones():
            tenant_timezone = get_gmt(timezone)
        else:
            error = f"Timezone {timezone} is not a displayed choice."

        user = User.query.filter_by(username=username).first()
        if user is not None and user.username == username:
            error = f"User {username} is already registered."

        user = User.query.filter_by(username=username).first()
        if user is not None and user.username == username:
            error = f"User {username} is already registered."

        user_agent_string = request.headers.get("User-Agent")
        current_app.logger.info(
            "Registration attempt - Username: %s, IP: %s. User-Agent: %s",
            username,
            request.remote_addr,
            user_agent_string,
        )

        if error is None:
            try:
                new_tenancy = Tenant(name=tenant_name, timezone=tenant_timezone)
                db.session.add(new_tenancy)
                db.session.commit()
                current_app.logger.info(
                    "Tenancy %s has been created.", new_tenancy.name
                )
                new_user = User(
                    username=username,
                    password=generate_password_hash(password),
                    tenant_id=new_tenancy.get_id(),
                )
                db.session.add(new_user)
                db.session.commit()
            except db.IntegrityError:
                current_app.logger.info("User %s is already registered.", username)
                error = f"User {username} is already registered."
            else:
                current_app.logger.info("User %s has been registered.", username)
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html", timezones=get_timezones())


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None

        user = User.query.filter_by(username=username).first()

        if user is None:
            current_app.logger.info("Failed login - Incorrect username: %s", username)
            error = "Incorrect username or password."

        elif not check_password_hash(user.password, password):
            current_app.logger.info(
                "Failed login - Incorrect password for username: %s", username
            )
            error = "Incorrect username or password."

        user_agent_string = request.headers.get("User-Agent")
        client_ip = request.headers.get('X-Forwarded-For')
        current_app.logger.info(
            "Log In attempt - Username: %s. IP: %s. User-Agent: %s",
            username,
            client_ip,
            user_agent_string,
        )

        current_app.logger.info(
            "Log In attempt - %s, %s, %s",
            request.headers.get('X-Forwarded-For'),
            request.headers.get('X-Real-IP'),
            request.headers.get('X-Client-IP'),
        )
        if error is None:
            tenancy = Tenant.query.filter_by(id=user.tenant_id).first()
            session.clear()
            session["user_id"] = user.id
            session["username"] = username
            session["tenant_id"] = user.tenant_id
            session["timezone"] = tenancy.timezone
            current_app.logger.info(
                "Tenancy %s, User_id %s, User %s has logged in. Timezone: %s",
                user.tenant_id,
                user.id,
                username,
                tenancy.timezone,
            )
            check_for_expired_tasks()
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    tenant_id = session.get("tenant_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter(
            User.id == user_id, User.tenant_id == tenant_id
        ).first()


@bp.route("/logout")
def logout():
    user_agent_string = request.headers.get("User-Agent")
    current_app.logger.info(
        "Log Out attempt - Username: %s. IP: %s. User-Agent: %s",
        session.get("username"),
        request.remote_addr,
        user_agent_string,
    )

    tenant = session.get("tenant_id")
    user_id = session.get("user_id")
    username = session.get("username")

    session.clear()

    current_app.logger.info(
        "Tenancy %s, User_id %s, User %s has logged out.",
        tenant,
        user_id,
        username,
    )
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # Handle the case where the user is not authenticated
            error = "Please log in to continue."
            flash(error)

            return redirect(url_for("auth.login"))

        if g.tenant_id is None:
            # Handle the case where the tenant is not set
            error = "Error receiving your tenancy."
            flash(error)

            return render_template("error.html")

        return view(**kwargs)

    return wrapped_view
