import logging

from app import db

logger = logging.getLogger('main_logger')


def bad_request_error(error):
    logger.warning(error)
    return {'code': '400'}, 400


def not_found_error(error):
    logger.warning(error)
    return {'code': '404'}, 404


def internal_error(error):
    db.session.rollback()
    logger.exception(error)
    return {'code': '500'}, 500
