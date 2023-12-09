from faker import Faker
from app.message.func import create_message, update_message

fake = Faker()


def generate_messages_text(number_text):
    text_lst = []
    for i in range(number_text):
        text_lst.append(fake.text())

    return text_lst


def clear_messages_text(text_messages):
    text_messages.clear()
    return text_messages


def create_message_for_test(text_list, user_login):
    messages_id_list = []

    for message_text in text_list:
        messages_id_list.append(create_message(message_text, user_login))

    return messages_id_list


def update_message_for_test(message_id_list, text_list, user_id):
    for item in range(len(message_id_list)):
        update_message(message_id_list[item], user_id, text_list[item])
