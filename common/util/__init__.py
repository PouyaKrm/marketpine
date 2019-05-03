from django.template import Context, Template
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def render_template(template: str, context: dict):
    """
        reference: https://docs.djangoproject.com/en/2.2/ref/templates/api/#rendering-a-context
    """
    template = Template(template)
    context = Context(context)
    return template.render(context)


def custom_login_payload(user, **kwargs):

    payload = jwt_payload_handler(user)

    token = jwt_encode_handler(payload)

    kwargs['token'] = token

    return kwargs
