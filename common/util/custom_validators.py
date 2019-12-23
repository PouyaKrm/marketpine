import os
import re

from django.core.exceptions import ValidationError
from django.conf import settings
from langdetect import detect


def phone_validator(value):

    result = re.match("^(\\+98|0)9\\d{9}$", value)

    if result is None:
        raise ValidationError("phone number is invalid")


def password_validator(value):

    result = re.match("^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{8,16}$", value)

    if result is None:
        raise ValidationError('کلمه عبور باید شامل یک حرف بزرگ، یک حرف کوچک و عدد و طول آن بین 8 تا 16 کاراکتر باشد')

    return value

def validate_logo_size(file):
    if file.size > settings.MAX_LOGO_SIZE:
        raise ValidationError('اندازه لگو بیش از حد مجاز است(200kb)')

    return file


def validate_sms_message_length(message: str):

    """
    validate sms message length based on kavenegar documentation
    for more information see `DOC <https://kavenegar.com/rest.html#basic-message>`
    :param message: text of sms message
    :raises: Validation error if message length is bigger than valid length based on language
    :return: message
    """

    if len(message) <= settings.SMS_PANEL['SMS_FA_MAX']:
        return message

    elif len(message) > settings.SMS_EN_MAX:
        raise ValidationError('طول پیامک حداکثر 612 کاراکتر است')

    elif (detect(message) == 'fa' or detect(message) == 'ur') and len(message) > settings.SMS_FA_MAX:
        raise ValidationError('طول پیامک فارسی حداکثر 268 کاراکتر است')

    else:
        return message


def pdf_file_validator(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in ".pdf":
        raise ValidationError('invalid file type (pdf is supported)')

