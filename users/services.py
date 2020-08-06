from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from common.util.kavenegar_local import APIException, HTTPException
from customers.services import customer_service
from users.exceptions import AuthenticationException
from common.util.sms_panel.message import SystemSMSMessage
from users.models import CustomerOneTimePasswords
import secrets
import logging

logger = logging.getLogger(__name__)

customer_one_time_password_exp_delta = settings.CUSTOMER_ONE_TIME_PASSWORD_EXPIRE_DELTA

class CustomerOneTimePasswordService:

    def generate_new_one_time_password(self, phone: str) -> CustomerOneTimePasswords:
        r = secrets.randbelow(1000000)
        if r < 100000:
            r += 100000
        return CustomerOneTimePasswords.objects.create(customer_phone=phone, code=r, expiration_time=timezone.now() + customer_one_time_password_exp_delta)


class CustomerAuthService:

    def __init__(self):
        self._one_time_password_service = CustomerOneTimePasswordService()

    def send_login_code(self, phone: str):
        p = None
        try:
            c = customer_service.get_customer_by_phone(phone)
            p = self._one_time_password_service.generate_new_one_time_password(phone)
            SystemSMSMessage().send_customer_one_time_password(c.phone, p.code)
        except ObjectDoesNotExist as e:
            logger.error(e)
            AuthenticationException.for_customer_by_phone_does_not_exist()
        except (APIException, HTTPException) as e:
            logger.error(e)
            p.delete()
            AuthenticationException.for_password_send_failed()


customer_auth_service = CustomerAuthService()
