from app import db
import logging
from app.models import Message, User, ActionEnum
from app.DTO.resopnses import HistoryResponseDTO, MessageResponseDTO
from werkzeug.exceptions import NotFound, BadRequest

logger = logging.getLogger('main_logger')


def create_message_obj(text, user):
    return Message(text=text, author=user)


def save_message(message):
    db.session.add(message)
    db.session.commit()


def create_message(text, user_login):
    if user_login is None:
        raise BadRequest(description='User login None')

    logger.info("Search user in database")

    user = User.query.filter_by(login=user_login).first()

    if text is None:
        raise BadRequest(description='Text not found')

    if user is None:
        raise NotFound(description=f'User {user_login} not found')

    message = create_message_obj(text, user)

    save_message(message)

    message_id = message.id

    # Сохранение id предка сообщения. Для того, чтобы потом получить историю сообщения.
    message.message_ancestor_id = message_id
    db.session.commit()

    logger.info(f'Message {message_id} created and saved in database')

    return message_id


def delete_message(message_id, user_login):
    if message_id is None:
        raise BadRequest(description='Incorrect message id')

    if user_login is None:
        raise BadRequest(description='Incorrect user login')

    message = Message.query.filter_by(id=message_id).first()
    logger.info("Search message in database")
    user = User.query.filter_by(login=user_login).first()
    logger.info("Search user in database")

    if message is None:
        raise NotFound(description=f'Message {message_id} not found for delete')

    if user is None:
        raise NotFound(description=f'User {user_login} not found for delete')

    if message.is_deleted:
        raise NotFound(description=f'Message {message_id} already deleted')

    ancestor_id = message.message_ancestor_id
    # Создание копии удаленного сообщения.(для отражения в истории сообщения)
    deleted_message = Message(text=message.text, author=user, action=message.action,
                              message_ancestor_id=ancestor_id)

    db.session.add(deleted_message)

    message.action = ActionEnum.DELETE
    message.is_deleted = True

    # Помечает флагом удаления всех сообщений, которые являются модификацией этого, путем поиска через id предка(
    # ancestor)
    messages_list = Message.query.filter_by(message_ancestor_id=ancestor_id).all()
    logger.info("Search messages with common ancestor")

    for item in messages_list:
        item.is_deleted = True

    db.session.commit()
    logger.info("Save deleted flag in db")

    logger.info(f'Message {ancestor_id} deleted')


def update_message(message_id, user_id, message_text):
    if message_id is None or user_id is None or message_text is None:
        raise BadRequest(description="Incorrect input arguments for message update")

    message = Message.query.filter_by(id=message_id).first()
    logger.info("Search message in database")

    if message is None:
        raise NotFound(description=f"Message {message_id} for update not found")

    if message.is_deleted:
        raise NotFound(description=f"Can't update deleted messages {message_id}")

    user = User.query.filter_by(id=user_id).first()
    logger.info("Search user in database")

    if user is None:
        raise NotFound(description="User is not found for message update")

    # Создает копию сообщения для отражения в истории
    updated_message = Message(text=message.text, author=user, action=message.action,
                              message_ancestor_id=message.message_ancestor_id)

    # Обновляет текст сообщения
    message.text = message_text
    message.action = ActionEnum.UPDATE
    db.session.add(updated_message)
    db.session.commit()
    logger.info("Save changes in message")


def show_history_message(message_id_from, message_id_to):
    response = []

    if message_id_from is None:
        raise BadRequest(description="Incorrect message id 'from'")

    if not message_id_to:
        message_id_to = message_id_from
    else:
        max_id = max(int(message_id_from), int(message_id_to))
        min_id = min(int(message_id_from), int(message_id_to))
        message_id_from = min_id
        message_id_to = max_id

    history_message = (Message.query.join(User, User.id == Message.user_id).add_columns(User.login)
                       .filter(message_id_from <= Message.message_ancestor_id)
                       .filter(Message.message_ancestor_id <= message_id_to)
                       .order_by(Message.message_ancestor_id.asc()).all())
    logger.info("Search history of message in database")

    for message in history_message:
        dto = HistoryResponseDTO(user_login=message.login, message_id=message[0].message_ancestor_id,
                                 text=message[0].text, action=message[0].action)
        response.append(dto)

    logger.info(f'Show history from ids {message_id_from} to {message_id_to}')

    return response


def show_all_messages_or_deleted(is_deleted):
    message_list = Message.query.filter(Message.message_ancestor_id == Message.id).filter(
        Message.is_deleted == is_deleted).all()
    log_msg = ("all", "deleted")[is_deleted]
    logger.info(f'Search {log_msg} messages in database')
    response_list = []

    for item in message_list:
        response_list.append(MessageResponseDTO(message_id=item.id, text=item.text))

    logger.info(f'Give response with {log_msg} messages')

    return response_list


def show_message(message_id):
    if message_id is None:
        raise BadRequest(description="Message id is None")

    message = Message.query.filter_by(id=message_id).first()
    logger.info(f"Search message by id {message_id} in database")

    if message is None:
        raise NotFound(description=f"Message by id {message_id} not found")

    return MessageResponseDTO(message_id=message.id, text=message.text)
