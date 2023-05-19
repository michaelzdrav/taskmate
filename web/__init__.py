import os

from flask import Flask
from dotenv import load_dotenv
from flask_mail import Mail
from logging.config import dictConfig

mail = Mail()

def create_app(test_config=None):
    load_dotenv() 

    # create and configure the app
    app = Flask(__name__, instance_path='/Users/mz/code/learning/task-mate/instance', instance_relative_config=True, template_folder='./Templates')

    # logging.config.dictConfig(dictConfig)
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
        DATABASE=os.path.join(app.instance_path, 'web.sqlite'),
        MAIL_SERVER = os.environ.get('MAIL_SERVER'),
        MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25),
        ADMINS = ['your-email@example.com']
    )

    app.logger.debug('Using database at %s', os.path.join(app.instance_path, 'web.sqlite'))

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

    from . import db
    db.init_app(app)
    mail = Mail(app)
    # mail.init_app(app)

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
