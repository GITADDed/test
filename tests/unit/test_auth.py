import unittest
from tests.config.test_config import TestConfig
from app import create_app
from app.auth.func import *
from tests.utils.message import *

test_user_login = 'test_user_login'
test_user_email = 'test_user@test.test'
test_user_passwd = 'asonetuaoenustht'


class TestMainCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        generate_messages_text()
        u = User(login=test_user_login, email=test_user_email)
        u.set_password(test_user_passwd)
        db.session.add(u)
        db.session.commit()
        self.user = db.session.query(User).filter_by(login=test_user_login).first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
