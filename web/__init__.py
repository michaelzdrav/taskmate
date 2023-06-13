import os

from flask import Flask, render_template, make_response
from dotenv import load_dotenv
from flask_mail import Mail
from logging.config import dictConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from .scheduler import start_scheduler
from datetime import datetime, timedelta
from flask_talisman import Talisman

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
scheduler = BackgroundScheduler()


def create_app(test_config=None):
    load_dotenv()

    # create and configure the app
    app = Flask(
        __name__,
        instance_path=os.path.join(os.getcwd(), "instance"),
        instance_relative_config=True,
        template_folder="./Templates",
    )

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )

    if os.getenv("SECRET_KEY"):
        app.logger.info("Loaded SECRET_KEY.")
    else:
        app.logger.error("The SECRET_KEY environment variable needs to be set.")

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI")
        or "sqlite:////instance/web.sqlite",
        # CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL"),
        # CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND"),
        # DATABASE=os.path.join(app.instance_path, 'web.sqlite'),
        # MAIL_SERVER = os.environ.get('MAIL_SERVER'),
        # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25),
        # ADMINS = ['your-email@example.com'],
    )

    if os.environ.get("SMTP_ENABLED") == "True":
        app.logger.info("SMTP is enabled.")
        MAIL_SERVER = os.environ.get("MAIL_SERVER")
        MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
        mail = Mail(app)
    else:
        app.logger.info("SMTP is not enabled.")

    app.logger.info("Using database at %s", app.config["SQLALCHEMY_DATABASE_URI"])

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    # mail = Mail(app)

    from . import auth

    app.register_blueprint(auth.bp)

    @app.route("/sitemap.xml", methods=["GET"])
    def sitemap():
        try:
            """Generate sitemap.xml. Makes a list of urls and date modified."""
            pages = []
            ten_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
            # static pages
            # TODO change url to https after SSL is enabled
            for rule in app.url_map.iter_rules():
                if "GET" in rule.methods and len(rule.arguments) == 0:
                    pages.append(
                        ["http://taskmate.digital" + str(rule.rule), ten_days_ago]
                    )

            sitemap_xml = render_template("sitemap_template.xml", pages=pages)
            response = make_response(sitemap_xml)
            response.headers["Content-Type"] = "application/xml"
            return response
        except Exception as e:
            return str(e)

    from . import landing

    app.register_blueprint(landing.bp)
    app.add_url_rule("/", endpoint="index")

    # TODO enable scheduler when completed
    # start_scheduler(scheduler)

    # TODO enable Talisman once SSL is enabled
    # Talisman(app, content_security_policy=None)

    return app
