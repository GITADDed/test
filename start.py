import logging

from app import create_app, db
from app.models import Message, User

logger = logging.getLogger('main_logger')

app = create_app()

logger.info('Application start up')


@app.route('/ping')
def ping():
    return 'pong'


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Message': Message}
