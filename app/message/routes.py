from app.message import bp
from flask import request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.message.forms import MessageForm
from app.message.func import (create_message, delete_message, update_message, show_history_message,
                              show_all_messages_or_deleted, show_message)
import logging

logger = logging.getLogger('main_logger')


@bp.route('/', methods=['GET'])
@login_required
def index():
    form = MessageForm()
    return render_template('message_index.html', form=form)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    logger.info("Get request to create message")
    text = request.form.get('message_text')
    message_id = create_message(text, current_user.login)
    flash(str(message_id))
    return redirect(url_for('message.index'))


@bp.route('/delete/<path_message_id>', methods=['POST'])
@login_required
def delete(path_message_id):
    logger.info("Get request to delete message")
    delete_message(path_message_id, current_user.login)
    return jsonify({'code': 'OK'})


@bp.route('/update/<message_id>', methods=['POST'])
@login_required
def update(message_id):
    logger.info("Get request to update message")
    message_text = request.json.get('text')
    update_message(message_id, current_user.id, message_text)
    return jsonify({'code': 'OK'})


@bp.route('/history', methods=['GET'])
def history():
    logger.info("Get request to show history message")
    message_id_from = request.json.get('message_id_from')
    message_id_to = request.json.get('message_id_to')
    return jsonify(show_history_message(message_id_from, message_id_to))


@bp.route('/show/all', methods=['GET'])
def show_all_messages():
    logger.info("Get request to show all messages")

    return jsonify(show_all_messages_or_deleted(False))


@bp.route('/show/deleted', methods=['GET'])
def show_deleted_messages():
    logger.info("Get request to show deleted messages")
    return jsonify(show_all_messages_or_deleted(True))


@bp.route('/show/<message_id>', methods=['GET'])
def show_message_by_id(message_id):
    logger.info(f"Get request to show message by id {message_id}")
    message = show_message(message_id)
    return jsonify(message)
