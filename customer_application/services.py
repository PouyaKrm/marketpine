import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from common.util.kavenegar_local import APIException, HTTPException
from customers.services import customer_service
from customer_application.exceptions import AuthenticationException
from common.util.sms_panel.message import SystemSMSMessage
from users.models import Customer
from .models import CustomerOneTimePasswords, CustomerLoginTokens
import secrets
import logging

logger = logging.getLogger(__name__)

customer_one_time_password_exp_delta = settings.CUSTOMER_ONE_TIME_PASSWORD_EXPIRE_DELTA
secret = settings.SECRET_KEY


class CustomerOneTimePasswordService:

    def generate_new_one_time_password(self, customer: Customer) -> CustomerOneTimePasswords:
        self._check_not_has_valid_one_time_password(customer)
        r = secrets.randbelow(1000000)
        if r < 100000:
            r += 100000
        self._send_one_time_password(customer.phone, r)
        return CustomerOneTimePasswords.objects.create(customer=customer, code=r,
                                                       expiration_time=timezone.now() + customer_one_time_password_exp_delta,
                                                       last_send_time=timezone.now())

    def check_one_time_password(self, customer: Customer, code) -> CustomerOneTimePasswords:
        try:
            return CustomerOneTimePasswords.objects.get(customer=customer, code=code, expiration_time__gt=timezone.now())
        except ObjectDoesNotExist:
            raise AuthenticationException.for_invalid_password()

    def _check_not_has_valid_one_time_password(self, customer: Customer):
        exist = CustomerOneTimePasswords.objects.filter(customer=customer, expiration_time__gt=timezone.now()).exists()
        if exist:
            AuthenticationException.for_one_time_password_already_sent()

    def resend_one_time_password(self, customer: Customer):
        try:
            p = CustomerOneTimePasswords.objects.get(customer=customer, expiration_time__gt=timezone.now(),
                                                     send_attempts__lt=2, last_send_time__lt=timezone.now() - timezone.timedelta(minutes=1))
            p.send_attempts += 1
            p.save()
            self._send_one_time_password(customer.phone, p.code)
        except ObjectDoesNotExist:
            AuthenticationException.for_invalid_password()

    def _send_one_time_password(self, phone, code):
        try:
            SystemSMSMessage().send_customer_one_time_password(phone, code)
        except (APIException, HTTPException) as e:
            logger.error(e)
            AuthenticationException.for_password_send_failed()


class CustomerLoginTokensService:

    def create_new_login_token(self, customer: Customer, user_agent: str) -> CustomerLoginTokens:
        t = jwt.encode({'customer_phone': customer.phone, 'customer_id': customer.id, 'iat': timezone.now().utcnow()}, secret, algorithm='HS256')
        return CustomerLoginTokens.objects.create(customer=customer, user_agent=user_agent, token=t)


class CustomerAuthService:

    def __init__(self):
        self._one_time_password_service = CustomerOneTimePasswordService()
        self._login_token_service = CustomerLoginTokensService()

    def send_login_code(self, phone: str):
        p = None
        try:
            c = self._get_customer(phone)
            p = self._one_time_password_service.generate_new_one_time_password(c)
        except (APIException, HTTPException) as e:
            logger.error(e)
            p.delete()
            AuthenticationException.for_password_send_failed()

    def login(self, phone: str, login_code: str, user_agent) -> str:
        c = self._get_customer(phone)
        p = self._one_time_password_service.check_one_time_password(c, login_code)
        t = self._login_token_service.create_new_login_token(c, user_agent)
        p.delete()
        return t.token

    def resend_one_time_password(self, phone):
        c = self._get_customer(phone)
        self._one_time_password_service.resend_one_time_password(c)

    def _get_customer(self, phone: str):
        try:
            return customer_service.get_customer_by_phone(phone)
        except ObjectDoesNotExist as e:
            logger.error(e)
            AuthenticationException.for_customer_by_phone_does_not_exist()


customer_auth_service = CustomerAuthService()

