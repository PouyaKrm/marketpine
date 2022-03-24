from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from users.models import Businessman, BusinessCategory


def has_business_category(user: Businessman) -> bool:
    return BusinessCategory.objects.filter(businessman=user).exists()


def _check_username_is_unique(*args, username: str):
    exist = Businessman.objects.filter(username=username).exists()
    if exist:
        raise ApplicationErrorException(ApplicationErrorCodes.USERNAME_IS_NOT_UNIQUE)


def _check_email_is_unique(*args, email: str):
    exist = Businessman.objects.filter(email=email).exists()
    if exist:
        raise ApplicationErrorException(ApplicationErrorCodes.EMAIL_IS_NOT_UNIQUE)


def _check_phone_is_unique(phone: str):
    exist = Businessman.objects.filter(phone=phone).exists()
    if exist:
        raise ApplicationErrorException(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)
