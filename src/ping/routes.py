from flask import Blueprint

ping = Blueprint('ping', __name__)


@ping.route('/ping', methods=['GET'])
def is_server_live():
    return 'pong'
