import logging

from base_app.error_codes import ApplicationErrorException

logger = logging.getLogger('django')


def log_app_error_exception(ex: ApplicationErrorException):
    logger.warning(ex.http_message)
    if ex.originalException is not None:
        logger.error(ex.originalException)
