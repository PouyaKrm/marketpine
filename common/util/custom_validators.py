import re

from django.core.exceptions import ValidationError
from django.conf import settings


def phone_validator(value):

    result = re.match("^(\\+98|0)9\\d{9}$", value)

    if result is None:
        raise ValidationError("phone number is invalid")


def validate_logo_size(file):
    if file.size > settings.MAX_LOGO_SIZE:
        raise ValidationError('اندازه لگو بیش از حد مجاز است(200kb)')

    return file
