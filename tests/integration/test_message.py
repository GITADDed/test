from unittest import TestCase
from tests.config.test_config import TestMessageConfig
from app import create_app, db
from app.models import User
from flask_login import login_user
from tests.utils.message import *
from app.message.func import create_message, delete_message

test_user_login = 'user_login'
test_user_email = 'email@email.email'
test_user_passwd = 'test_password'
test_user_text_message = []
number_messages = 30


class TestMessageIntegrationCase(TestCase):

    def setUp(self):
        self.app = create_app(TestMessageConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        self.test_request_context = self.app.test_request_context()
        db.drop_all()
        db.create_all()
        global test_user_text_message
        test_user_text_message = generate_messages_text(number_messages)
        u = User(login=test_user_login, email=test_user_email)
        u.set_password(test_user_passwd)
        db.session.add(u)
        db.session.commit()

        with self.test_request_context:
            login_user(u)

        self.user = u

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_message_index(self):
        response = self.test_client.get('/message/', follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Message input', str(response.data))

    def test_message_create_success(self):
        response = self.test_client.post('/message/create', data=dict(message_text='Hello test'), follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('Your message id:', str(response.data))

    def test_message_delete_success(self):
        test_user_text_id = 0
        message_id = create_message(test_user_text_message[test_user_text_id], self.user.login)

        response = self.test_client.post(f'/message/delete/{message_id}')

        self.assertTrue(response.status_code == 200)
        self.assertIn('{"code":"OK"}', str(response.data))

    def test_message_delete_fail_404_message_not_exist(self):
        message_id = 100

        response = self.test_client.post(f'/message/delete/{message_id}')

        self.assertTrue(response.status_code == 404)
        self.assertIn('{"code":"404"}', str(response.data))

    def test_message_delete_fail_404_message_deleted(self):
        test_user_text_id = 0
        message_id = create_message(test_user_text_message[test_user_text_id], self.user.login)

        response = self.test_client.post(f'/message/delete/{message_id}')

        self.assertTrue(response.status_code == 200)
        self.assertIn('{"code":"OK"}', str(response.data))

        response = self.test_client.post(f'/message/delete/{message_id}')

        self.assertTrue(response.status_code == 404)
        self.assertIn('{"code":"404"}', str(response.data))

    def test_message_update_success_message_exist(self):
        test_user_text_id = 0
        message_id = create_message(test_user_text_message[test_user_text_id], self.user.login)

        response = self.test_client.post(f'/message/update/{message_id}',
                                         json=dict(text=test_user_text_message[test_user_text_id + 1]),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 200)
        self.assertIn('{"code":"OK"}', str(response.data))

    def test_message_update_fail_message_not_exist(self):
        test_user_text_id = 0
        message_id = 100
        response = self.test_client.post(f'/message/update/{message_id}',
                                         json=dict(text=test_user_text_message[test_user_text_id + 1]),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 404)
        self.assertIn('{"code":"404"}', str(response.data))

    def test_message_update_fail_message_deleted(self):
        test_user_text_id = 0
        message_id = create_message(test_user_text_message[test_user_text_id], self.user.login)

        response = self.test_client.post(f'/message/delete/{message_id}')

        self.assertTrue(response.status_code == 200)
        self.assertIn('{"code":"OK"}', str(response.data))

        response = self.test_client.post(f'/message/update/{message_id}',
                                         json=dict(text=test_user_text_message[test_user_text_id + 1]),
                                         follow_redirects=True)

        self.assertTrue(response.status_code == 404)
        self.assertIn('{"code":"404"}', str(response.data))

    def test_history_success_one_created_message(self):
        test_user_text_id = 0
        message_id = create_message(test_user_text_message[test_user_text_id], self.user.login)

        response = self.test_client.get('/message/history', json=dict(message_id_from=message_id))

        self.assertTrue(response.status_code == 200)
        self.assertIn('"action":"CREATE"', str(response.data))
        self.assertIn(f'"message_id":{message_id}', str(response.data))
        self.assertIn(f'"user_login":"{self.user.login}"', str(response.data))

    def test_show_all_success(self):
        test_user_text_id = 0
        message_id = create_message(test_user_text_message[test_user_text_id], self.user.login)

        response = self.test_client.get('/message/show/all')

        self.assertTrue(response.status_code == 200)
        self.assertIn(f'"message_id":{message_id}', str(response.data))

    def test_show_deleted_success(self):
        test_user_text_id = 0
        message_id = create_message(test_user_text_message[test_user_text_id], self.user.login)
        message_id_deleted = create_message(test_user_text_message[test_user_text_id + 1], self.user.login)

        delete_message(message_id_deleted, self.user.login)

        response = self.test_client.get('/message/show/deleted')

        self.assertTrue(response.status_code == 200)
        self.assertIn(f'"message_id":{message_id_deleted}', str(response.data))
        self.assertTrue(f'"message_id":{message_id}' not in str(response.data))

    def test_show_message_by_id_success(self):
        message_id_list = create_message_for_test(test_user_text_message[number_messages - 5:number_messages],
                                                  self.user.login)

        response = self.test_client.get(f'/message/show/{message_id_list[2]}')

        self.assertTrue(response.status_code == 200)
        self.assertIn(f'"message_id":{message_id_list[2]}', str(response.data))
        for message_id in message_id_list:
            if message_id != message_id_list[2]:
                self.assertTrue(f'"message_id":{message_id}' not in str(response.data))

