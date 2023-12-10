from unittest import TestCase
from tests.config.test_config import TestAuthConfig
from app import create_app, db
from app.models import User
from flask_login import login_user

test_user_login = 'user_login'
test_user_email = 'email@email.email'
test_user_passwd = 'test_password'


class TestAuthIntegrationCase(TestCase):

    def setUp(self):
        self.app = create_app(TestAuthConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        self.test_request_context = self.app.test_request_context()
        db.drop_all()
        db.create_all()
        u = User(login=test_user_login, email=test_user_email)
        u.set_password(test_user_passwd)
        db.session.add(u)
        db.session.commit()

        self.user = u

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_get_index(self):
        response = self.test_client.get('/login')

        self.assertTrue(response.status_code == 200)
        self.assertIn('Login', str(response.data))

    def test_login_post_success(self):
        response = self.test_client.post('/login', data=dict(login=test_user_login, password=test_user_passwd),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Logout', str(response.data))

    def test_login_post_fail_incorrect_password(self):
        response = self.test_client.post('/login', data=dict(login=test_user_login, password='IncorrectPassword'),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Invalid login or password', str(response.data))

    def test_login_post_fail_incorrect_login(self):
        response = self.test_client.post('/login', data=dict(login='IncorrectLogin', password=test_user_passwd),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Invalid login or password', str(response.data))

    def test_logout_post(self):
        with self.test_client and self.test_request_context:
            login_user(self.user)
            response = self.test_client.post('/login', follow_redirects=True)
            self.assertTrue(response.status_code == 200)
            self.assertIn('Logout', str(response.data))

            response = self.test_client.post('/logout', follow_redirects=True)
            self.assertTrue(response.status_code == 200)
            self.assertIn('Login', str(response.data))

    def test_register_success(self):
        email = 'new_test_email@email.email'
        login = 'new_test_login'
        passwd = 'new_test_passwd'
        response = self.test_client.post('/register',
                                         data=dict(email=email, login=login, password=passwd, password_repeat=passwd),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Congratulations, you are now a registered user!', str(response.data))

    def test_register_fail_passwd_incorrect_repeat(self):
        email = 'new_test_email@email.email'
        login = 'new_test_login'
        passwd = 'new_test_passwd'
        response = self.test_client.post('/register',
                                         data=dict(email=email, login=login, password=passwd, password_repeat='bla'),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Field must be equal to password.', str(response.data))

    def test_register_fail_email_registered(self):
        login = 'new_test_login'
        passwd = 'new_test_passwd'

        response = self.test_client.post('/register',
                                         data=dict(email=test_user_email, login=login, password=passwd,
                                                   password_repeat=passwd),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Please use a different email', str(response.data))

    def test_register_fail_login_registered(self):
        email = 'new_test_email@email.email'
        passwd = 'new_test_passwd'

        response = self.test_client.post('/register',
                                         data=dict(email=email, login=test_user_login, password=passwd,
                                                   password_repeat=passwd),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Please use a different login', str(response.data))
