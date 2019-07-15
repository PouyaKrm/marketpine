from random import Random

from django.template import Context, Template
from rest_framework_jwt.settings import api_settings

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


def generate_discount_code():

    rand = Random()
    code = ''
    for i in range(2):
        code += alphabets[rand.randrange(0, alphabets_length)] + alphabets[rand.randrange(0, alphabets_length)] + str(rand.randrange(10, 100))

    return code[:4] + '-' + code[4:]

