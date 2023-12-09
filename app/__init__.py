import logging
import os.path
import sys

from flask import Flask
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.logger = logging.getLogger('app_logger')
    main_logger = logging.getLogger('main_logger')

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler_main = RotatingFileHandler('logs/auth.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(formatter)
        file_handler_main.setFormatter(formatter)
        file_handler.setLevel(logging.WARNING)
        file_handler_main.setLevel(logging.INFO)
        console_handler = logging.StreamHandler(sys.stdout)
        main_logger.addHandler(file_handler_main)
        main_logger.setLevel(logging.INFO)
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    db.init_app(app)
    main_logger.info('Data base init in app')
    migrate.init_app(app, db)
    main_logger.info('Migration is on')
    login.init_app(app)

    login.login_view = 'auth.login'

    from app.auth import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.message import bp as message_blueprint
    app.register_blueprint(message_blueprint, url_prefix='/message')

    from swagger_ui import api_doc
    api_doc(app, config_path='./openapi.yaml', url_prefix='/docs', title='API doc')

    from app.errors.routes import not_found_error
    app.register_error_handler(404, not_found_error)

    from app.errors.routes import internal_error
    app.register_error_handler(500, internal_error)

    return app


from app import models
