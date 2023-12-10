import logging
import os.path
import flask_migrate

from flask import Flask
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from unittest import TestLoader, TextTestRunner
import click

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


@click.command(name='test')
@click.option('-u', is_flag=True, default=False, help='Run unit tests')
@click.option('-i', is_flag=True, default=False, help='Run integration tests')
@click.option('-v', is_flag=True, default=False, help='Verbose tests')
def launch_unit_tests(u, i, v):
    test_loader = TestLoader()
    verbosity = 1

    if v:
        verbosity = 2

    runner = TextTestRunner(verbosity=verbosity)
    unit_tests = None

    if u:
        unit_tests = test_loader.discover(start_dir='tests/unit')

    if i:
        unit_tests = test_loader.discover(start_dir='tests/integration')

    if unit_tests is None:
        unit_tests = test_loader.discover(start_dir='tests/unit')

    runner.run(unit_tests)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    main_logger = logging.getLogger('main_logger')

    db.init_app(app)
    migrate.init_app(app, db)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        file_handler_main = RotatingFileHandler('logs/app.log', maxBytes=10240, encoding='utf-8')
        file_handler_main.setFormatter(formatter)
        file_handler_main.setLevel(logging.INFO)
        main_logger.addHandler(file_handler_main)
        main_logger.setLevel(logging.INFO)
        app.logger.addHandler(file_handler_main)
        app.logger.setLevel(logging.WARNING)

        with app.app_context():
            db.create_all()

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

    app.cli.add_command(launch_unit_tests)

    return app


from app import models
