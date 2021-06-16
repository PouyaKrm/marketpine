import logging
import secrets

import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from common.util.kavenegar_local import APIException, HTTPException
from common.util.sms_panel.message import SystemSMSMessage
from customer_application.exceptions import CustomerServiceException
from customer_return_plan.festivals.services import festival_service
from customer_return_plan.services import customer_discount_service
from customers.services import customer_service
from online_menu.services import online_menu_service
from smspanel.services import sms_message_service
from users.models import Customer, Businessman, BusinessmanCustomer
from users.services import businessman_service
from .error_codes import CustomerAppErrors
from .models import CustomerVerificationCode, CustomerLoginTokens, CustomerUpdatePhoneModel

logger = logging.getLogger(__name__)

customer_one_time_password_exp_delta = settings.CUSTOMER_ONE_TIME_PASSWORD_EXPIRE_DELTA
secret = settings.SECRET_KEY


class CustomerVerificationCodeService:

    def generate_new_login_verification_code(self, customer: Customer) -> CustomerVerificationCode:
        return self._generate_verification_code(customer, CustomerVerificationCode.USED_FOR_LOGIN)

    def check_login_verification_code(self, customer: Customer, code) -> CustomerVerificationCode:
        return self._get_last_unexpired_verify_code_by_code(customer, code,
                                                            CustomerVerificationCode.USED_FOR_LOGIN)

    def resend_login_verification_code(self, customer: Customer):
        self._resend_verification_code(customer, CustomerVerificationCode.USED_FOR_LOGIN)

    def generate_new_phone_update_code(self, customer: Customer, new_phone: str) -> CustomerVerificationCode:
        return self._generate_verification_code(customer, CustomerVerificationCode.USED_FOR_PHONE_UPDATE, new_phone)

    def resend_phone_update_code(self, customer: Customer):
        self._resend_verification_code(customer, CustomerVerificationCode.USED_FOR_PHONE_UPDATE)

    def check_phone_update_code(self, customer, code) -> CustomerVerificationCode:
        return self._get_last_unexpired_verify_code_by_code(customer, code, CustomerVerificationCode.USED_FOR_PHONE_UPDATE)

    def _generate_verification_code(self, customer: Customer, used_for, phone=None) -> CustomerVerificationCode:
        self._check_not_has_unexpired_verification_code(customer, used_for)
        r = secrets.randbelow(1000000)
        if r < 100000:
            r += 100000

        vc = CustomerVerificationCode.objects.create(customer=customer, code=r,
                                                     expiration_time=timezone.now() + customer_one_time_password_exp_delta,
                                                     last_send_time=timezone.now(),
                                                     used_for=used_for)
        try:
            if used_for == CustomerVerificationCode.USED_FOR_PHONE_UPDATE:
                self._send_vrification_code(phone, vc)
            else:
                self._send_vrification_code(customer.phone, vc)
            return vc
        except Exception as e:
            vc.delete()
            raise e

    def _resend_verification_code(self, customer: Customer, used_for: str):
        vc = self._get_valid_verification_code_for_resend(customer, used_for)
        vc.send_attempts += 1
        vc.save()
        if used_for == CustomerVerificationCode.USED_FOR_PHONE_UPDATE:
            self._send_vrification_code(vc.phone_update.new_phone, vc)
        else:
            self._send_vrification_code(customer.phone, vc)

    def _send_vrification_code(self, phone: str, vc: CustomerVerificationCode):
        sms = SystemSMSMessage()
        try:
            if vc.used_for == CustomerVerificationCode.USED_FOR_LOGIN:
                sms.send_customer_one_time_password(phone, vc.code)
            elif vc.used_for == CustomerVerificationCode.USED_FOR_PHONE_UPDATE:
                sms.send_customer_phone_change_code(phone, vc.code)
        except (APIException, HTTPException) as e:
            logger.error(e)
            raise e

    def _get_valid_verification_code_for_resend(self, customer: Customer, used_for: str) -> CustomerVerificationCode:
        try:
            v = CustomerVerificationCode.objects.get(
                customer=customer,
                expiration_time__gt=timezone.now(),
                used_for=used_for,
                send_attempts__lt=2,
                last_send_time__lt=timezone.now() - timezone.timedelta(minutes=1))
            return v
        except ObjectDoesNotExist:
            CustomerServiceException.for_invalid_verification_code()

    def _check_not_has_unexpired_verification_code(self, customer: Customer, used_for):
        exist = CustomerVerificationCode.objects.filter(used_for=used_for, customer=customer,
                                                        expiration_time__gt=timezone.now()).exists()
        if exist:
            CustomerServiceException.for_verification_code_already_sent()

    def _get_last_unexpired_verify_code_by_code(self, customer: Customer, code: str,
                                                used_for: str) -> CustomerVerificationCode:
        try:
            return CustomerVerificationCode.objects.get(customer=customer, code=code,
                                                        used_for=used_for,
                                                        expiration_time__gt=timezone.now())
        except ObjectDoesNotExist:
            raise CustomerServiceException.for_invalid_verification_code()


class CustomerLoginTokensService:

    def create_new_login_token(self, customer: Customer, user_agent: str) -> CustomerLoginTokens:
        t = jwt.encode({'customer_phone': customer.phone, 'customer_id': customer.id, 'iat': timezone.now().utcnow()},
                       secret, algorithm='HS256').decode('UTF-8')
        return CustomerLoginTokens.objects.create(customer=customer, user_agent=user_agent, token=t)

    def get_customer_by_token(self, token: str, user_agent: str) -> Customer:
        try:
            return CustomerLoginTokens.objects.get(token=token, user_agent=user_agent).customer
        except ObjectDoesNotExist:
            CustomerServiceException.for_login_token_does_not_exist()


class CustomerAuthService:

    def __init__(self):
        self._verification_code_service = CustomerVerificationCodeService()
        self._login_token_service = CustomerLoginTokensService()

    def send_login_code(self, phone: str):
        p = None
        c = customer_service.get_customer_by_phone_or_create(phone)
        try:
            p = self._verification_code_service.generate_new_login_verification_code(c)
        except (APIException, HTTPException) as e:
            p.delete()
            CustomerServiceException.for_password_send_failed()

    def login(self, phone: str, login_code: str, user_agent) -> dict:
        c = self._get_customer(phone)
        p = self._verification_code_service.check_login_verification_code(c, login_code)
        t = self._login_token_service.create_new_login_token(c, user_agent)
        self.set_phone_confirmed(c)
        p.delete()
        profile = customer_data_service.get_profile(c)
        return {'token': t.token, 'profile': profile}

    def resend_one_time_password(self, phone):
        c = self._get_customer(phone)
        try:
            self._verification_code_service.resend_login_verification_code(c)
        except (HTTPException, APIException) as e:
            logger.error(e)
            CustomerServiceException.for_password_send_failed()

    def _get_customer(self, phone: str):
        try:
            return customer_service.get_customer_by_phone(phone)
        except ObjectDoesNotExist as e:
            logger.error(e)
            CustomerServiceException.for_customer_by_phone_does_not_exist()

    def get_customer_by_login_token(self, token: str, user_agent: str) -> Customer:
        return self._login_token_service.get_customer_by_token(token, user_agent)

    def set_phone_confirmed(self, c: Customer) -> Customer:
        if not c.is_phone_confirmed:
            c.is_phone_confirmed = True
            c.save()
        return c

    def send_phone_update_code(self, customer: Customer, new_phone: str):

        is_unique = customer_service.is_phone_number_unique_for_update(customer, new_phone)
        is_same = new_phone == customer.phone
        if not is_unique or is_same:
            CustomerServiceException.for_phone_number_already_taken()
        p = None
        try:
            vc = self._verification_code_service.generate_new_phone_update_code(customer, new_phone)
            p = CustomerUpdatePhoneModel.objects.create(new_phone=new_phone, verify_code=vc)
        except (APIException, HTTPException) as e:
            p.delete()
            CustomerServiceException.for_password_send_failed()

    def resend_phone_update_code(self, customer: Customer):
        try:
            self._verification_code_service.resend_phone_update_code(customer)
        except (APIException, HTTPException) as e:
            logger.error(e)
            CustomerServiceException.for_password_send_failed()

    def update_phone(self, customer: Customer, code: str) -> dict:
        vc = self._verification_code_service.check_phone_update_code(customer, code)
        pu = vc.phone_update
        customer.phone = pu.new_phone
        customer.save()
        pu.delete()
        vc.delete()
        return customer_data_service.get_profile(customer)


customer_auth_service = CustomerAuthService()


class CustomerDataService:

    def get_all_businessmans(self, customer: Customer, business_name: str = None):
        query = customer.businessmans.filter(connected_customers__is_deleted=False).order_by(
            '-connected_customers__create_date')
        if business_name is not None and business_name.strip() != '':
            query = query.filter(business_name__icontains=business_name)
        return query.all()

    def is_customer_jouned_to_businessman(self, customer: Customer, businessman_id) -> bool:
        return customer.businessmans.filter(id=businessman_id).exists()

    def get_notifications(self, customer: Customer) -> dict:
        return {}
        f = festival_service.get_customer_latest_festival_for_notif(customer)
        return {'festival': f, 'post': p}

    def get_online_menus_by_businessman_id(self, businessman_id: int):
        b = self.get_businessman_by_id(businessman_id)
        return online_menu_service.get_all_menus(b)

    def add_customer_to_businessman(self, page_businessman_id: str, customer: Customer) -> Businessman:
        if customer.is_anonymous:
            CustomerServiceException.for_should_login()
        b = self.get_businessman_by_id_or_page_id(page_businessman_id)
        exist = BusinessmanCustomer.objects.filter(businessman=b, customer=customer, is_deleted=False).exists()
        if exist:
            return b

        self._check_customer_not_already_deleted(b, customer)

        BusinessmanCustomer.objects.create(businessman=b, customer=customer,
                                           joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        sms_message_service.send_welcome_message(b, customer)
        return b

    def get_businessman_by_id_or_page_id(self, page_businessman_id: str) -> Businessman:
        is_int = True
        try:
            parsed = int(page_businessman_id)
            if parsed <= 0:
                raise ValueError
        except ValueError:
            parsed = page_businessman_id
            is_int = False

        if is_int:
            return customer_data_service.get_businessman_by_id(parsed)
        else:
            return customer_data_service.get_businessman_by_page_id(parsed)

    def get_businessman_page_id(self, buisnessman: Businessman):
        return m

    def get_businessman_by_id(self, businessman_id: int) -> Businessman:
        try:
            return Businessman.objects.get(id=businessman_id)
        except ObjectDoesNotExist:
            CustomerServiceException.for_businessman_not_found()

    def get_businessman_by_page_id(self, page_id: str) -> Businessman:
        try:
            return businessman_service.get_businessman_by_page_id(page_id)
        except ObjectDoesNotExist:
            CustomerServiceException.for_businessman_not_found()

    def get_businessman_of_customer_by_id(self, customer: Customer, businessman_id: int) -> Businessman:
        try:
            return customer.businessmans.get(id=businessman_id, connected_customers__is_deleted=False)
        except ObjectDoesNotExist:
            CustomerServiceException.for_businessman_not_found()

    def get_profile(self, customer: Customer) -> dict:
        total_businessman = self.get_all_businessmans(customer).count()
        total_discounts = customer_discount_service.get_customer_available_discount(customer).count()
        return {
            'phone': customer.phone,
            'is_full_name_set': customer.is_full_name_set(),
            'full_name': customer.full_name,
            'date_joined': customer.date_joined,
            'total_subscribed': total_businessman,
            'total_unused_discounts': total_discounts,
        }

    def update_full_name(self, customer: Customer, full_name: str) -> Customer:
        customer.full_name = full_name
        customer.save()
        return customer

    def _check_customer_not_already_deleted(self, businessman: Businessman, customer: Customer):
        already_deleted = BusinessmanCustomer.objects.filter(businessman=businessman, customer=customer,
                                                             is_deleted=True).exists()

        if already_deleted:
            raise CustomerServiceException(CustomerAppErrors.CAN_NOT_JOIN_BUSINESSMAN_THAT_DELETED_CUSTOMER_BEFORE)

    def check_user_joined_businessman(self, businessman: Businessman, customer: Customer):
        exist = BusinessmanCustomer.objects.filter(businessman=businessman, customer=customer, is_deleted=False)
        if not exist:
            raise CustomerServiceException(CustomerAppErrors.USER_NOT_JOINED_BUSINESSMAN)


customer_data_service = CustomerDataService()
