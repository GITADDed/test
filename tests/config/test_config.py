from config import Config
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class TestMessageConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../unit/test.db')
    WTF_CSRF_ENABLED = False


class TestAuthConfig(TestMessageConfig):
    SERVER_NAME = 'localhost:8000'
