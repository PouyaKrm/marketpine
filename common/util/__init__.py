from enum import Enum
from rest_framework_jwt.settings import api_settings
from strgen import StringGenerator
import jwt

import string

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

#AVAILABLE_TEMPLATE_CONTEXT = {'phone': '09582562418', 'telegram_id': '@mohammad12', 'business_name': '', 'instagram_id': '@insta_test'}



def custom_login_payload(user, **kwargs):

    """
    Creates a dictionary that will be used as the response body of the refresh token request
    :param user: user model
    :param kwargs:
    :return: Dictionary for response body
    """

    payload = jwt_payload_handler(user)

    token = jwt_encode_handler(payload)

    expirationTime = jwt.decode(token, verify=False)['exp']

    kwargs['token'] = token
    kwargs['exp'] = expirationTime
    kwargs['exp_duration'] = api_settings.JWT_EXPIRATION_DELTA

    return kwargs


alphabets = list(string.ascii_uppercase)
alphabets_length = len(alphabets)


class DiscountType(Enum):
    FESTIVAL = 1
    INVITATION = 2
    INSTAGRAM = 3

def generate_discount_code(discount_type: DiscountType):

    code = StringGenerator("[A-Za-z0-9]{8}").render()

    if discount_type == DiscountType.FESTIVAL:
        code = 'f' + code

    elif discount_type == DiscountType.INVITATION:
        code = 'i' + code

    elif discount_type == DiscountType.INSTAGRAM:
        code = 'n' + code

    else:
        raise Exception('Value of discount_type is invalid')

    return code




class DaysOfWeek(Enum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7

    def to_django_weekday(self, value):

        return value + 1


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


