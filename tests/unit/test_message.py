import unittest
from app import create_app
from app.message.func import *
from tests.config.test_config import TestMessageConfig
from tests.utils.message import *

test_user_login = 'test_user'
test_user_email = 'test_user@test.test'
test_user_passwd = 'test_password'
test_user_text_message = []
number_messages = 30


class TestMessageCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestMessageConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        global test_user_text_message
        test_user_text_message = generate_messages_text(number_messages)

        u = User(login=test_user_login, email=test_user_email)
        u.set_password(test_user_passwd)
        db.session.add(u)
        db.session.commit()
        self.user = u

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        global test_user_text_message
        test_user_text_message = clear_messages_text(test_user_text_message)

    def test_create_message_success(self):
        test_user_text_id = 0

        message_id = create_message(test_user_text_message[test_user_text_id], test_user_login)

        test_message = db.session.get(Message, message_id)

        self.assertEqual(test_user_text_message[test_user_text_id], test_message.text, 'Message text not Equal '
                                                                                       'message text from database')

        test_user_owner_message = db.session.get(User, test_message.user_id)

        self.assertEqual(test_user_login, test_user_owner_message.login, 'User owner not Equal with User from database')

    def test_create_message_fail_404_not_found_user(self):
        test_user_text_id = 0
        unknown_user_login = 'unknown_login'
        self.assertRaises(NotFound, create_message, test_user_text_message[test_user_text_id], unknown_user_login)

    def test_create_message_fail_400_user_login_none(self):
        test_user_text_id = 0
        self.assertRaises(BadRequest, create_message, test_user_text_message[test_user_text_id], None)

    def test_create_message_fail_404_text_not_found(self):
        self.assertRaises(BadRequest, create_message, None, test_user_login)

    def test_update_message_success(self):
        orig_text_id = 3
        upd_text_id = 15
        message_id = create_message(test_user_text_message[orig_text_id], self.user.login)

        update_message(message_id, self.user.id, test_user_text_message[upd_text_id])

        message_list = db.session.query(Message).filter_by(message_ancestor_id=message_id).all()
        message = message_list[0]
        orig_message = message_list[1]

        self.assertEqual(test_user_text_message[upd_text_id], message.text, "Text don't equal with updated text")
        self.assertEqual(self.user.id, message.user_id, "User UPDATE action owner in database incorrect")
        self.assertEqual(ActionEnum.UPDATE, message.action, "Message action in database is not UPDATE")
        self.assertEqual(test_user_text_message[orig_text_id], orig_message.text, "Text in origin message don't equal")
        self.assertEqual(self.user.id, orig_message.user_id, "User CREATE action owner in database incorrect")
        self.assertEqual(ActionEnum.CREATE, orig_message.action, "Message action in database is not CREATE")

    def test_update_message_fail_404_message_not_found(self):
        message_id = 1
        text_id = 5
        self.assertRaises(NotFound, update_message, message_id, self.user.id, test_user_text_message[text_id])

    def test_update_message_fail_404_message_is_deleted(self):
        text_id = 1
        upd_text_id = 21
        message_id = create_message(test_user_text_message[text_id], self.user.login)

        message = db.session.get(Message, message_id)
        message.is_deleted = True
        db.session.commit()

        self.assertRaises(NotFound, update_message, message_id, self.user.id, test_user_text_message[upd_text_id])

    def test_update_message_fail_400_input_none(self):
        self.assertRaises(BadRequest, update_message, None, None, None)

    def test_update_message_fail_404_not_found_user(self):
        text_id = 1
        upd_text_id = 21
        unknown_user_id = 1387
        message_id = create_message(test_user_text_message[text_id], self.user.login)
        self.assertRaises(NotFound, update_message, message_id, unknown_user_id, test_user_text_message[upd_text_id])

    def test_delete_message_success(self):
        test_user_text_id = 0
        message_id_list = create_message_for_test(test_user_text_message[test_user_text_id:number_messages],
                                                  test_user_login)

        delete_message(message_id_list[test_user_text_id], test_user_login)

        deleted_message = db.session.get(Message, message_id_list[test_user_text_id])

        user_action_owner = db.session.get(User, deleted_message.user_id)

        self.assertTrue(deleted_message.is_deleted, 'Message have not deleted flag')
        self.assertEqual(test_user_login, user_action_owner.login, 'User login who delete message not equal')
        self.assertEqual(ActionEnum.DELETE, deleted_message.action, 'Action is not DELETE')

    def test_delete_message_with_updates_success(self):
        message_id_list = create_message_for_test(test_user_text_message[0:number_messages], test_user_login)
        update_message_for_test(message_id_list, test_user_text_message, self.user.id)

        for item in message_id_list:
            delete_message(item, self.user.login)

        messages = db.session.query(Message).all()

        for item in messages:
            self.assertTrue(item.is_deleted)

    def test_show_history_message_success_one_created_message(self):
        text_id = 5

        message_id = create_message(test_user_text_message[text_id], self.user.login)

        history = show_history_message(message_id, None)

        self.assertEqual(self.user.login, history[0].get('user_login'), "History user login incorrect")
        self.assertEqual(message_id, history[0].get('message_id'), "History message_id incorrect")
        self.assertEqual(test_user_text_message[text_id], history[0].get('text'), "History text incorrect")
        self.assertEqual(ActionEnum.CREATE, history[0].get('action'), "History action incorrect")

    def test_show_history_message_success_one_created_message_one_time_update(self):
        orig_text_id = 10
        upd_text_id = 13

        message_id = create_message(test_user_text_message[orig_text_id], self.user.login)

        update_message(message_id, self.user.id, test_user_text_message[upd_text_id])

        history = show_history_message(message_id, None)

        self.assertEqual(self.user.login, history[0].get('user_login'), "History user login incorrect")
        self.assertEqual(message_id, history[0].get('message_id'), "History message_id incorrect")
        self.assertEqual(test_user_text_message[upd_text_id], history[0].get('text'), "History text incorrect")
        self.assertEqual(ActionEnum.UPDATE, history[0].get('action'), "History action incorrect")

        self.assertEqual(self.user.login, history[1].get('user_login'), "History user login incorrect")
        self.assertEqual(message_id, history[1].get('message_id'), "History message_id incorrect")
        self.assertEqual(test_user_text_message[orig_text_id], history[1].get('text'), "History text incorrect")
        self.assertEqual(ActionEnum.CREATE, history[1].get('action'), "History action incorrect")

    def test_show_history_message_success_two_create_messages_three_updates_first_message_delete(self):
        message_1_orig_text_id = 1
        message_2_orig_text_id = 2

        message_1_upd_text_ids = [3, 4, 5]

        message_2_upd_text_ids = [6, 7, 8]

        message_1_id = create_message(test_user_text_message[message_1_orig_text_id], self.user.login)
        message_2_id = create_message(test_user_text_message[message_2_orig_text_id], self.user.login)

        for i in range(3):
            update_message(message_1_id, self.user.id, test_user_text_message[message_1_upd_text_ids[i]])
            update_message(message_2_id, self.user.id, test_user_text_message[message_2_upd_text_ids[i]])

        delete_message(message_1_id, self.user.login)

        history_message_1 = show_history_message(message_1_id, None)
        history_message_2 = show_history_message(message_2_id, None)
        history_message_2.append(history_message_2[0])

        self.assertEqual(self.user.login, history_message_1[0].get('user_login'), "History user login incorrect")
        self.assertEqual(message_1_id, history_message_1[0].get('message_id'), "History message_id incorrect")
        self.assertEqual(test_user_text_message[message_1_upd_text_ids[2]], history_message_1[0].get('text'),
                         "History text incorrect")
        self.assertEqual(ActionEnum.DELETE, history_message_1[0].get('action'), "History action incorrect")

        text_id = 0
        for i in range(2, 4):
            self.assertEqual(self.user.login, history_message_1[i].get('user_login'), "History user login incorrect")
            self.assertEqual(self.user.login, history_message_2[i].get('user_login'), "History user login incorrect")

            self.assertEqual(message_1_id, history_message_1[i].get('message_id'), "History message_id incorrect")
            self.assertEqual(message_2_id, history_message_2[i].get('message_id'), "History message_id incorrect")

            self.assertEqual(test_user_text_message[message_1_upd_text_ids[text_id]], history_message_1[i].get('text'),
                             "History text incorrect")
            self.assertEqual(test_user_text_message[message_2_upd_text_ids[text_id]], history_message_2[i].get('text'),
                             "History text incorrect")
            text_id += 1

            self.assertEqual(ActionEnum.UPDATE, history_message_1[i].get('action'), "History action incorrect")
            self.assertEqual(ActionEnum.UPDATE, history_message_2[i].get('action'), "History action incorrect")

        self.assertEqual(self.user.login, history_message_1[1].get('user_login'), "History user login incorrect")
        self.assertEqual(self.user.login, history_message_2[1].get('user_login'), "History user login incorrect")
        self.assertEqual(message_1_id, history_message_1[1].get('message_id'), "History message_id incorrect")
        self.assertEqual(message_2_id, history_message_2[1].get('message_id'), "History message_id incorrect")
        self.assertEqual(test_user_text_message[message_1_orig_text_id], history_message_1[1].get('text'),
                         "History text incorrect")
        self.assertEqual(test_user_text_message[message_2_orig_text_id], history_message_2[1].get('text'),
                         "History text incorrect")
        self.assertEqual(ActionEnum.CREATE, history_message_1[1].get('action'), "History action incorrect")
        self.assertEqual(ActionEnum.CREATE, history_message_2[1].get('action'), "History action incorrect")

    def test_show_history_message_success_three_created_messages_in_range_in_asc_order(self):
        msg_text_id_list = [0, 1, 2]
        msg_id_text_id_dict = {}
        for msg_text in msg_text_id_list:
            msg_id_text_id_dict.update([(create_message(test_user_text_message[msg_text], self.user.login), msg_text)])

        msg_list = list(msg_id_text_id_dict.keys())

        msg_list.sort()

        from_id = msg_list[0]
        to_id = msg_list[len(msg_list) - 1]

        history = show_history_message(from_id, to_id)
        message_id_in_list = 0
        for message_history in history:
            self.assertEqual(self.user.login, message_history.get('user_login'), "History user login incorrect")
            self.assertEqual(msg_list[message_id_in_list], message_history.get('message_id'),
                             "History message_id incorrect")
            self.assertEqual(test_user_text_message[msg_id_text_id_dict.get(msg_list[message_id_in_list])],
                             message_history.get('text'), "History text incorrect")
            self.assertEqual(ActionEnum.CREATE, message_history.get('action'), "History action incorrect")
            message_id_in_list += 1

    def test_show_history_message_success_three_created_messages_in_range_in_desc_order(self):
        msg_text_id_list = [0, 1, 2]
        msg_id_text_id_dict = {}
        for msg_text in msg_text_id_list:
            msg_id_text_id_dict.update([(create_message(test_user_text_message[msg_text], self.user.login), msg_text)])

        msg_list = list(msg_id_text_id_dict.keys())

        msg_list.sort()

        to_id = msg_list[0]
        from_id = msg_list[len(msg_list) - 1]

        history = show_history_message(from_id, to_id)
        message_id_in_list = 0
        for message_history in history:
            self.assertEqual(self.user.login, message_history.get('user_login'), "History user login incorrect")
            self.assertEqual(msg_list[message_id_in_list], message_history.get('message_id'),
                             "History message_id incorrect")
            self.assertEqual(test_user_text_message[msg_id_text_id_dict.get(msg_list[message_id_in_list])],
                             message_history.get('text'), "History text incorrect")
            self.assertEqual(ActionEnum.CREATE, message_history.get('action'), "History action incorrect")
            message_id_in_list += 1

    def test_show_history_message_success_no_exist_message(self):
        history = show_history_message(12, 33)
        self.assertEqual(0, len(history), "History is not empty")

    def test_show_history_message_fail_400_none_parameters(self):
        self.assertRaises(BadRequest, show_history_message, None, None)

    def test_show_all_messages_or_deleted_success_three_created_messages_with_out_deleted(self):
        msg_text_id_list = [0, 1, 2]
        msg_id_text_id_dict = {}
        for msg_text in msg_text_id_list:
            msg_id_text_id_dict.update([(create_message(test_user_text_message[msg_text], self.user.login), msg_text)])

        msg_list = list(msg_id_text_id_dict.keys())
        msg_list.sort()

        messages = show_all_messages_or_deleted(False)

        self.assertEqual(3, len(messages), "Messages is not three")
        self.assertEqual(msg_list[0], messages[0].get("message_id"), "Messages id incorrect")
        self.assertEqual(msg_list[1], messages[1].get("message_id"), "Messages id incorrect")
        self.assertEqual(msg_list[2], messages[2].get("message_id"), "Messages id incorrect")

    def test_show_all_messages_or_deleted_success_no_messages_show_all_messages(self):
        messages = show_all_messages_or_deleted(False)

        self.assertEqual(0, len(messages), "Response is not empty")

    def test_show_all_messages_or_deleted_success_no_messages_show_deleted_messages(self):
        messages = show_all_messages_or_deleted(True)

        self.assertEqual(0, len(messages), "Response is not empty")

    def test_show_all_messages_or_deleted_success_three_created_messages_1_deleted_show_deleted(self):
        msg_text_id_list = [0, 1, 2]
        msg_id_text_id_dict = {}
        for msg_text in msg_text_id_list:
            msg_id_text_id_dict.update([(create_message(test_user_text_message[msg_text], self.user.login), msg_text)])

        msg_list = list(msg_id_text_id_dict.keys())
        msg_list.sort()

        delete_message(msg_list[0], self.user.login)

        messages = show_all_messages_or_deleted(True)

        self.assertEqual(1, len(messages), "Response consist more than one message or zero")
        self.assertEqual(msg_list[0], messages[0].get("message_id"), "Not equal id message")

    def test_show_message_success(self):
        text_id = 12
        message_id = create_message(test_user_text_message[text_id], self.user.login)
        message = show_message(message_id)

        self.assertEqual(message_id, message.get("message_id"), "Show incorrect message id")
        self.assertEqual(test_user_text_message[text_id], message.get("text"), "Show incorrect message text")

    def test_show_message_fail_404(self):
        message_id = 12
        self.assertRaises(NotFound, show_message, message_id)

    def test_show_message_fail_400_parameter_none(self):
        message_id = None
        self.assertRaises(BadRequest, show_message, message_id)


if __name__ == '__main__':
    unittest.main()
