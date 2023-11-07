from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

from src.auth.routes import auth as auth_blueprint
from src.ping.routes import ping as ping_blueprint

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(ping_blueprint)

    return app
