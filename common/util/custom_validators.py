import re

from django.core.exceptions import ValidationError



def phone_validator(value):

    result = re.match("^(\\+98|0)9\\d{9}$", value)

    if result is None:
        raise ValidationError("phone number is invalid")
