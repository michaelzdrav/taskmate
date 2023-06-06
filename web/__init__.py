import os

from flask import Flask
from dotenv import load_dotenv
from flask_mail import Mail
from logging.config import dictConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app(test_config=None):
    load_dotenv() 

    # create and configure the app
    app = Flask(__name__, instance_path=os.path.join(os.getcwd(), 'instance'), instance_relative_config=True, template_folder='./Templates')

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    if os.getenv("SECRET_KEY"):
        app.logger.info('Loaded SECRET_KEY.')
    else:
        app.logger.error('The SECRET_KEY environment variable needs to be set.')
 
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI") or \
        "sqlite:////instance/web.sqlite",
        # DATABASE=os.path.join(app.instance_path, 'web.sqlite'),
        # MAIL_SERVER = os.environ.get('MAIL_SERVER'),
        # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25),
        # ADMINS = ['your-email@example.com'],
    )

    if os.environ.get('SMTP_ENABLED') == "True":
        app.logger.info('SMTP is enabled.')
        MAIL_SERVER = os.environ.get('MAIL_SERVER')
        MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
        mail = Mail(app)
    else:
        app.logger.info('SMTP is not enabled.')

    app.logger.info('Using database at %s', app.config['SQLALCHEMY_DATABASE_URI'])

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import landing
    app.register_blueprint(landing.bp)
    app.add_url_rule('/', endpoint='index')

    return app
