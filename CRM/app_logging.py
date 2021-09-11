import logging

from rest_framework.views import exception_handler

from base_app.error_codes import ApplicationErrorException
from common.util import get_client_ip
from common.util.http_helpers import bad_request
from users.models import Customer

logger = logging.getLogger('django')


def custom_exception_handler(exe, context):
    if not isinstance(exe, ApplicationErrorException):
        response = exception_handler(exe, context)
        return response

    request = context['request']
    ip = get_client_ip(request)
    username = 'anonymous'
    if not request.user.is_anonymous and type(request.user) != Customer:
        username = 'businessman with username ' + request.user.username
    elif not request.user.is_anonymous and type(request.user) == Customer:
        username = 'customer with phone ' + request.user.phone

    if exe.originalException is not None:
        logger.error('following error happened in user request')
        logger.error('user ip ' + ip)
        logger.error(username)
        logger.error(exe.http_message)
        logger.error(exe.originalException)
    else:
        logger.warning(exe.http_message)

    return bad_request(exe.http_message)
