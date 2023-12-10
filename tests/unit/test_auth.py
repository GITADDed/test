import unittest
from tests.config.test_config import TestAuthConfig
from app import create_app
from app.auth.func import *
from app.auth.forms import LoginForm

test_user_login = 'test_user_login'
test_user_email = 'test_user@test.test'
test_user_passwd = 'asonetuaoenustht'
test_user_text_list = []
number_text = 30


class TestAuthCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestAuthConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        u = User(login=test_user_login, email=test_user_email)
        u.set_password(test_user_passwd)
        db.session.add(u)
        db.session.commit()
        self.user = db.session.query(User).filter_by(login=test_user_login).first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_redirect_next_page_success_next_page_exist(self):
        next_page = 'message/create'
        response = redirect_next_page(next_page)

        self.assertEqual(302, response.status_code, 'Status code not redirect')
        self.assertEqual(next_page, response.location, 'Next page not equal next_page var')

    def test_redirect_next_page_fail_next_page_not_exist(self):
        next_page = url_for('auth.index')
        response = redirect_next_page('')

        self.assertEqual(302, response.status_code, 'Status code not redirect')
        self.assertEqual(next_page, response.location, 'Next page not equal next_page var')

    def test_valid_user_and_sign_in_success_correct_login_passwd(self):
        with self.app.test_request_context():
            login_form = LoginForm()
            login_form.login.data = test_user_login
            login_form.password.data = test_user_passwd
            is_sign_in = valid_user_and_sign_in(login_form)

            self.assertTrue(is_sign_in)

    def test_valid_user_and_sign_in_fail_incorrect_login(self):
        with self.app.test_request_context():
            login_form = LoginForm()
            login_form.login.data = 'blablalogin'
            login_form.password.data = test_user_passwd
            is_sign_in = valid_user_and_sign_in(login_form)

            self.assertFalse(is_sign_in)

    def test_valid_user_and_sign_in_fail_incorrect_passwd(self):
        with self.app.test_request_context():
            login_form = LoginForm()
            login_form.login.data = test_user_login
            login_form.password.data = 'blablapasswd'
            is_sign_in = valid_user_and_sign_in(login_form)

            self.assertFalse(is_sign_in)

    def test_save_user_success(self):
        user = User(login='login', email='email@email.email')
        user.set_password('password')

        save_user(user)

        self.assertEqual(db.session.get(User, user.id), user)

    def test_create_user_success(self):
        user = create_user(test_user_login, test_user_email, test_user_passwd)

        self.assertEqual(user.login, test_user_login)
        self.assertEqual(user.email, test_user_email)
        self.assertTrue(user.check_password(test_user_passwd))

