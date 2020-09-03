import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from common.util.kavenegar_local import APIException, HTTPException
from customers.services import customer_service
from customer_application.exceptions import CustomerServiceException
from common.util.sms_panel.message import SystemSMSMessage
from users.models import Customer, Businessman
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
            raise CustomerServiceException.for_invalid_password()

    def _check_not_has_valid_one_time_password(self, customer: Customer):
        exist = CustomerOneTimePasswords.objects.filter(customer=customer, expiration_time__gt=timezone.now()).exists()
        if exist:
            CustomerServiceException.for_one_time_password_already_sent()

    def resend_one_time_password(self, customer: Customer):
        try:
            p = CustomerOneTimePasswords.objects.get(customer=customer, expiration_time__gt=timezone.now(),
                                                     send_attempts__lt=2, last_send_time__lt=timezone.now() - timezone.timedelta(minutes=1))
            p.send_attempts += 1
            p.save()
            self._send_one_time_password(customer.phone, p.code)
        except ObjectDoesNotExist:
            CustomerServiceException.for_invalid_password()

    def _send_one_time_password(self, phone, code):
        try:
            SystemSMSMessage().send_customer_one_time_password(phone, code)
        except (APIException, HTTPException) as e:
            logger.error(e)
            CustomerServiceException.for_password_send_failed()


class CustomerLoginTokensService:

    def create_new_login_token(self, customer: Customer, user_agent: str) -> CustomerLoginTokens:
        t = jwt.encode({'customer_phone': customer.phone, 'customer_id': customer.id, 'iat': timezone.now().utcnow()}, secret, algorithm='HS256').decode('UTF-8')
        return CustomerLoginTokens.objects.create(customer=customer, user_agent=user_agent, token=t)

    def get_customer_by_token(self, token: str, user_agent: str) -> Customer:
        try:
            return CustomerLoginTokens.objects.get(token=token, user_agent=user_agent).customer
        except ObjectDoesNotExist:
            CustomerServiceException.for_login_token_does_not_exist()

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
            CustomerServiceException.for_password_send_failed()

    def login(self, phone: str, login_code: str, user_agent) -> dict:
        c = self._get_customer(phone)
        p = self._one_time_password_service.check_one_time_password(c, login_code)
        t = self._login_token_service.create_new_login_token(c, user_agent)
        p.delete()
        return {'token': t.token, 'date_joined': c.date_joined, 'phone': c.phone}

    def resend_one_time_password(self, phone):
        c = self._get_customer(phone)
        self._one_time_password_service.resend_one_time_password(c)

    def _get_customer(self, phone: str):
        try:
            return customer_service.get_customer_by_phone(phone)
        except ObjectDoesNotExist as e:
            logger.error(e)
            CustomerServiceException.for_customer_by_phone_does_not_exist()

    def get_customer_by_login_token(self, token: str, user_agent: str) -> Customer:
        return self._login_token_service.get_customer_by_token(token, user_agent)


customer_auth_service = CustomerAuthService()


class CustomerDataService:

    def get_all_businessmans(self, customer: Customer, business_name: str = None):
        query = customer.businessmans.order_by('-connected_customers__create_date')
        if business_name is not None and business_name.strip() != '':
            query = query.filter(business_name__icontains=business_name)
        return query.all()

    def get_businessman_of_customer_by_id(self, customer: Customer, businessman_id: int) -> Businessman:
        try:
            return customer.businessmans.get(id=businessman_id)
        except ObjectDoesNotExist:
            CustomerServiceException.for_businessman_not_found()

    def is_customer_jouned_to_businessman(self, customer: Customer, businessman_id) -> bool:
        return customer.businessmans.filter(id=businessman_id).exists()


customer_data_service = CustomerDataService()
