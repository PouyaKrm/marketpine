import re
import secrets

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework.request import Request
from rest_framework_jwt.settings import api_settings

from base_app.error_codes import ApplicationErrorCodes, ApplicationErrorException
from common.util import get_client_ip
from common.util.kavenegar_local import APIException
from common.util.sms_panel.message import system_sms_message
from panelprofile.services import sms_panel_info_service, business_man_auth_doc_service
from payment.services import wallet_service
from users.models import Businessman, VerificationCodes, BusinessmanRefreshTokens, BusinessCategory, \
    PhoneChangeVerification

customer_frontend_paths = settings.CUSTOMER_APP_FRONTEND_PATHS

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class BusinessmanService:

    def is_page_id_unique(self, user: object, page_id: object) -> object:
        return not Businessman.objects.filter(page_id=page_id.lower()).exclude(id=user.id).exists()

    def get_businessman_by_page_id(self, page_id: str) -> Businessman:
        return Businessman.objects.get(mobileapppageconf__page_id=page_id.lower())

    def is_page_id_predefined(self, page_id: str) -> bool:
        return page_id in customer_frontend_paths

    def is_page_id_pattern_valid(self, page_id) -> bool:
        match = re.search(r'^\d*[a-zA-Z_-]+[a-zA-Z0-9_-]*$', page_id)
        return match is not None

    def is_phone_unique_for_update(self, user: Businessman, new_phone: str) -> bool:
        return not Businessman.objects.filter(phone=new_phone).exclude(id=user.id).exists()

    def register_user(self,
                      username: str,
                      password: str,
                      phone: str,
                      email: str,
                      first_name: str,
                      last_name: str) -> Businessman:

        self._check_username_is_unique(username)
        self._check_phone_is_unique(phone)
        self._check_email_is_unique(email)
        b = Businessman.objects.create(
            username=username,
            phone=phone,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True)
        b.set_password(password)
        b.save()
        wallet_service.get_businessman_wallet_or_create(b)
        return b

    def update_businessman_profile(self, user: Businessman, first_name: str, last_name: str,
                                   business_name: str,
                                   category: BusinessCategory, phone: str = None, email: str = None,
                                   viewed_intro: bool = None) -> Businessman:
        if first_name is not None and user.authorized == Businessman.AUTHORIZATION_UNAUTHORIZED:
            user.first_name = first_name
        if last_name is not None and user.authorized == Businessman.AUTHORIZATION_UNAUTHORIZED:
            user.last_name = last_name
        if business_name is not None:
            user.business_name = business_name
        is_unique = self.is_phone_unique_for_update(user, phone)
        if phone is not None and not user.is_phone_verified and not is_unique:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)
        elif phone is not None and not user.is_phone_verified and is_unique:
            user.phone = phone

        if category is not None:
            user.business_category = category

        if viewed_intro is not None:
            user.viewed_intro = viewed_intro

        user.save()
        return user

    def has_business_category(self, user: Businessman) -> bool:
        return BusinessCategory.objects.filter(businessman=user).exists()

    def send_businessman_phone_verification(self, user: Businessman, new_phone: str = None):
        if new_phone is not None:
            self._check_phone_is_unique_for_update(user, new_phone)
            user.phone = new_phone
            user.save()
            verification_service.delete_all_phone_confirm_code_for_user(user)
            verification_service.create_send_phone_confirm_verification_code(user)
        else:
            verification_service.create_send_phone_confirm_verification_code(user)

    def verify_businessman_phone(self, user: Businessman, code: str):
        verification_service.check_phone_confirm_code_is_valid_and_delete(user, code)
        user.is_phone_verified = True
        user.save()

    def is_password_correct(self, user: Businessman, password: str) -> bool:
        user = authenticate(username=user.username, password=password)
        return user is not None

    def login_user(self, username: str, password: str, request: Request) -> dict:

        user = authenticate(username=username, password=password)

        if user is None:
            return None

        expire_time = timezone.now() + settings.REFRESH_TOKEN_EXP_DELTA
        obj = BusinessmanRefreshTokens.objects.create(username=user.get_username(), expire_at=expire_time,
                                                      ip=get_client_ip(request))

        payload = {'exp': expire_time, "iss": user.get_username(), "iat": timezone.now(), 'id': obj.id}

        token = jwt.encode(payload, settings.REFRESH_KEY_PR, algorithm='RS256')

        refresh_token = {
            'token': token,
            'exp': expire_time,
            'id': user.id,
            'username': user.get_username(),
            'business_name': user.business_name,
            'exp_duration': settings.REFRESH_TOKEN_EXP_DELTA
        }

        access_token = self._create_access_token(user)
        data = {
            'refresh_token': refresh_token,
            'access_token': access_token
        }
        return data

    def get_access_token_by_username(self, username: str) -> dict:

        try:
            user = Businessman.objects.get(username=username)
            return self._create_access_token(user)
        except ObjectDoesNotExist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)

    def send_phone_change_verification(self, user: Businessman, new_phone: str) -> PhoneChangeVerification:

        is_unique = businessman_service.is_phone_unique_for_update(user, new_phone)
        if not is_unique or user.phone == new_phone:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)
        return verification_service.create_send_phone_change_verification_codes(user, new_phone)

    def change_phone_number(self, user: Businessman,
                            previous_phone_code: str,
                            new_phone_code: str) -> Businessman:

        vcode = verification_service.check_phone_change_verification_codes_and_delete(user,
                                                                                      previous_phone_code,
                                                                                      new_phone_code)

        user.phone = vcode.new_phone
        user.save()
        return user

    def authdocs_uploaded_and_pending(self, user: Businessman) -> Businessman:
        user.authorized = Businessman.AUTHORIZATION_PENDING
        user.has_sms_panel = True
        user.save()
        return user

    def authorize_user(self, user: Businessman) -> Businessman:

        if user.authorized != Businessman.AUTHORIZATION_PENDING:
            return user

        with transaction.atomic():
            sms_panel_info_service.activate_sms_panel(user)
            user.authorized = Businessman.AUTHORIZATION_AUTHORIZED
            user.has_sms_panel = True
            user.save()

        return user

    def un_authorize_user(self, user: Businessman) -> Businessman:
        if user.authorized == Businessman.AUTHORIZATION_UNAUTHORIZED:
            return user
        with transaction.atomic():
            sms_panel_info_service.deactivate_sms_panel(user)
            business_man_auth_doc_service.delete_businessman_docs(user)
            user.authorized = Businessman.AUTHORIZATION_UNAUTHORIZED
            user.save()
            return user

    def _check_phone_is_unique_for_update(self, user: Businessman, new_phone: str):
        is_unique = self.is_phone_unique_for_update(user, new_phone)
        if not is_unique:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)

    def _create_access_token(self, user: Businessman) -> dict:

        payload = jwt_payload_handler(user)

        token = jwt_encode_handler(payload)

        expirationTime = jwt.decode(token, verify=False)['exp']
        result = {
            'token': token,
            'exp': expirationTime,
            'exp_duration': api_settings.JWT_EXPIRATION_DELTA
        }
        return result

    def _check_username_is_unique(self, username: str):
        exist = Businessman.objects.filter(username=username).exists()
        if exist:
            raise ApplicationErrorException(ApplicationErrorCodes.USERNAME_IS_NOT_UNIQUE)

    def _check_email_is_unique(self, email: str):
        exist = Businessman.objects.filter(email=email).exists()
        if exist:
            raise ApplicationErrorException(ApplicationErrorCodes.EMAIL_IS_NOT_UNIQUE)

    def _check_phone_is_unique(self, phone: str):
        exist = Businessman.objects.filter(phone=phone).exists()
        if exist:
            raise ApplicationErrorException(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)


class VerificationService:

    def delete_all_phone_confirm_code_for_user(self, user: Businessman):
        VerificationCodes.objects.filter(businessman=user,
                                         used_for=VerificationCodes.USED_FOR_PHONE_VERIFICATION).delete()

    def delete_all_phone_change_codes(self, user: Businessman):
        VerificationCodes.objects.filter(businessman=user, used_for=VerificationCodes.USED_FOR_PHONE_CHANGE).delete()

    def create_send_phone_confirm_verification_code(self, user: Businessman) -> VerificationCodes:
        exist = VerificationCodes.objects.filter(businessman=user, expiration_time__gt=timezone.now(),
                                                 used_for=VerificationCodes.USED_FOR_PHONE_VERIFICATION).exists()

        if exist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_CODE_ALREADY_SENT)

        vcode = self._create_verification_code_for_user(user, VerificationCodes.USED_FOR_PHONE_VERIFICATION)
        self._send_verification_code_phone(user.phone, vcode)
        return vcode

    def create_send_phone_change_verification_codes(self, user: Businessman, new_phone: str) -> PhoneChangeVerification:
        exist = PhoneChangeVerification.objects.filter(
            businessman=user,
            new_phone=new_phone,
            previous_phone_verification__expiration_time__gt=timezone.now(),
            new_phone_verification__expiration_time__gt=timezone.now()).exists()

        if exist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_CODE_ALREADY_SENT)

        with transaction.atomic():
            verification_service.delete_all_phone_change_codes(user)
            PhoneChangeVerification.objects.filter(businessman=user).delete()
            previous_verification = self._create_verification_code_for_user(user,
                                                                            VerificationCodes.USED_FOR_PHONE_CHANGE)
            new_verification = self._create_verification_code_for_user(user, VerificationCodes.USED_FOR_PHONE_CHANGE)
            result = PhoneChangeVerification.objects.create(
                businessman=user,
                previous_phone_verification=previous_verification,
                new_phone_verification=new_verification,
                new_phone=new_phone)
            self._send_verification_code_phone(user.phone, previous_verification)
            self._send_verification_code_phone(new_phone, new_verification)
            return result

    def resend_phone_confirm_code(self, user: Businessman):

        vcode = VerificationCodes.objects.filter(
            businessman=user,
            used_for=VerificationCodes.USED_FOR_PHONE_VERIFICATION).order_by('-create_date').first()

        if vcode is None:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)

        self._resend_verification_code(user.phone, vcode)

    def resend_phone_change_code(self, user: Businessman):
        vcode = PhoneChangeVerification.objects.filter(businessman=user).order_by('-create_date').first()

        if vcode is None:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)

        self._resend_verification_code(user.phone, vcode.previous_phone_verification)
        self._resend_verification_code(vcode.new_phone, vcode.new_phone_verification)

    def check_phone_confirm_code_is_valid_and_delete(self, user: Businessman, code: str):
        try:
            vcode = VerificationCodes.objects.get(businessman=user, code=code,
                                                  expiration_time__gt=timezone.now(),
                                                  used_for=VerificationCodes.USED_FOR_PHONE_VERIFICATION)
            vcode.delete()
        except ObjectDoesNotExist as e:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)

    def check_phone_change_verification_codes_and_delete(self, user: Businessman,
                                                         previous_phone_code: str,
                                                         new_phone_code: str) -> PhoneChangeVerification:
        try:
            result = PhoneChangeVerification.objects.get(businessman=user,
                                                         previous_phone_verification__businessman=user,
                                                         previous_phone_verification__code=previous_phone_code,
                                                         new_phone_verification__businessman=user,
                                                         new_phone_verification__code=new_phone_code,
                                                         previous_phone_verification__expiration_time__gt=timezone.now(),
                                                         new_phone_verification__expiration_time__gt=timezone.now())
            result.delete()
            result.previous_phone_verification.delete()
            result.new_phone_verification.delete()
            return result
        except ObjectDoesNotExist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)

    def _resend_verification_code(self, phone: str, vcode: VerificationCodes):
        self._check_can_resend_verification_code(vcode)
        self._send_verification_code_phone(phone, vcode)
        vcode.num_requested += 1
        vcode.save()

    def _check_can_resend_verification_code(self, vcode: VerificationCodes):
        expired = vcode.expiration_time < timezone.now()
        max_request = vcode.num_requested >= 2
        last_send_delta_small = vcode.update_date > (timezone.now() - timezone.timedelta(minutes=1))

        if expired or max_request or last_send_delta_small:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)

    def _send_verification_code_phone(self, phone: str, vcode: VerificationCodes):
        try:
            if vcode.used_for == VerificationCodes.USED_FOR_PHONE_VERIFICATION:
                system_sms_message.send_verification_code(phone, vcode.code)
            if vcode.used_for == VerificationCodes.USED_FOR_PHONE_CHANGE:
                system_sms_message.send_businessman_phone_change_code(phone, vcode.code)
        except APIException as e:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_CODE_SEND_ERROR)

    def _create_verification_code_for_user(self, user: Businessman, used_for: str) -> VerificationCodes:
        code = self._create_unique_code_for_user(user)
        expire_time = timezone.now() + timezone.timedelta(minutes=10)
        vcode = VerificationCodes.objects.create(businessman=user, code=code, num_requested=1,
                                                 expiration_time=expire_time, used_for=used_for)
        return vcode

    def _create_unique_code_for_user(self, user: Businessman) -> str:

        def create_code() -> str:
            c = secrets.randbelow(10000)

            if c < 10000:
                c += 10000

            return c

        code = create_code()
        exist = VerificationCodes.objects.filter(businessman=user, code=code).exists()
        while exist:
            code = create_code()
            exist = VerificationCodes.objects.filter(code=code).exists()

        return code


verification_service = VerificationService()
businessman_service = BusinessmanService()
