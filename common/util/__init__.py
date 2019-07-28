from enum import Enum
from random import Random

from django.template import Context, Template
from rest_framework_jwt.settings import api_settings
from strgen import StringGenerator

from users.models import Businessman, Customer
import string

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

#AVAILABLE_TEMPLATE_CONTEXT = {'phone': '09582562418', 'telegram_id': '@mohammad12', 'business_name': '', 'instagram_id': '@insta_test'}


def get_template_context(customer: Customer):

    return {'phone': customer.phone, 'telegram_id': customer.telegram_id,
               'instagram_id': customer.instagram_id, 'business_name': customer.businessman.business_name}


def get_fake_context(user: Businessman):

    return {'phone': '09582562418', 'telegram_id': '@mohammad12', 'business_name': user.business_name, 'instagram_id': '@insta_test'}


def render_template(template: str, context: dict):
    """
        reference: https://docs.djangoproject.com/en/2.2/ref/templates/api/#rendering-a-context
    """
    template = Template(template)
    context = Context(context)
    return template.render(context)


def render_template_with_customer_data(template: str, customer: Customer):

    return render_template(template, get_template_context(customer))


def custom_login_payload(user, **kwargs):

    payload = jwt_payload_handler(user)

    token = jwt_encode_handler(payload)

    kwargs['token'] = token

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
