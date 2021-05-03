import re
import secrets

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework.request import Request

from base_app.error_codes import ApplicationErrorCodes
from common.util import get_client_ip
from common.util.kavenegar_local import APIException
from common.util.sms_panel.message import system_sms_message
from users.models import Businessman, VerificationCodes, BusinessmanRefreshTokens, BusinessCategory, \
    PhoneChangeVerification

customer_frontend_paths = settings.CUSTOMER_APP_FRONTEND_PATHS


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

    def update_businessman_profile(self, user: Businessman, first_name: str, last_name: str,
                                   business_name: str,
                                   category: BusinessCategory, phone: str = None, email: str = None) -> Businessman:
        if user.authorized == Businessman.AUTHORIZATION_UNAUTHORIZED:
            user.first_name = first_name
            user.last_name = last_name
        user.business_name = business_name
        is_unique = self.is_phone_unique_for_update(user, phone)
        if phone is not None and not user.is_phone_verified and not is_unique:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)
        elif phone is not None and not user.is_phone_verified and is_unique:
            user.phone = phone

        if category is not None:
            user.business_category = category

        user.save()
        return user

    def verify_businessman_phone(self, user: Businessman, verification_code_id: int, code: str):
        verification_service.check_phone_confirm_code_is_valid_and_delete(user, verification_code_id, code)
        user.is_phone_verified = True
        user.save()

    def authenticate_user(self, username: str, password: str, request: Request) -> dict:

        user = authenticate(username=username, password=password)

        if user is None:
            return None

        expire_time = timezone.now() + settings.REFRESH_TOKEN_EXP_DELTA
        obj = BusinessmanRefreshTokens.objects.create(username=user.get_username(), expire_at=expire_time,
                                                      ip=get_client_ip(request))

        payload = {'exp': expire_time, "iss": user.get_username(), "iat": timezone.now(), 'id': obj.id}

        token = jwt.encode(payload, settings.REFRESH_KEY_PR, algorithm='RS256')

        data = {'refresh_token': token,
                'exp': expire_time,
                'id': user.id,
                'username': user.get_username(),
                'business_name': user.business_name,
                'exp_duration': settings.REFRESH_TOKEN_EXP_DELTA
                }

        return data

    def send_phone_change_verification(self, user: Businessman, new_phone: str) -> PhoneChangeVerification:

        is_unique = businessman_service.is_phone_unique_for_update(user, new_phone)
        if not is_unique:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)

        return verification_service.create_send_phone_change_verification_codes(user, new_phone)

    def change_phone_number(self, user: Businessman, phone_change_verification_id: int,
                            previous_phone_code: str,
                            new_phone_code: str) -> Businessman:

        vcode = verification_service.check_phone_change_verification_codes_and_delete(user,
                                                                                      phone_change_verification_id,
                                                                                      previous_phone_code,
                                                                                      new_phone_code)

        user.phone = vcode.new_phone
        user.save()
        return user


class VerificationService:

    def create_send_phone_confirm_verification_code(self, user: Businessman) -> VerificationCodes:
        exist = VerificationCodes.objects.filter(businessman=user, expiration_time__gt=timezone.now(),
                                                 used_for=VerificationCodes.USED_FOR_PHONE_VERIFICATION).exists()

        if exist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_CODE_ALREADY_SENT)

        vcode = self._create_verification_code_for_user(user, VerificationCodes.USED_FOR_PHONE_VERIFICATION)
        self._send_verification_code_phone(user.phone, vcode)
        return vcode

    def create_send_phone_change_verification_codes(self, user: Businessman, new_phone: str) -> PhoneChangeVerification:
        exist = PhoneChangeVerification.objects.filter(businessman=user,
                                                       previous_phone_verification__expiration_time__gt=timezone.now(),
                                                       new_phone_verification__expiration_time__gt=timezone.now()).exists()
        if exist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_CODE_ALREADY_SENT)
        with transaction.atomic():
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

    def resend_phone_confirm_code(self, user: Businessman, verification_code_id: int):

        try:
            vcode = VerificationCodes.objects.get(businessman=user, id=verification_code_id,
                                                  used_for=VerificationCodes.USED_FOR_PHONE_VERIFICATION)
        except ObjectDoesNotExist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)
        self._resend_verification_code(user.phone, vcode)

    def resend_phone_change_code(self, user: Businessman, phone_change_verification_id: int):
        try:
            vcode = PhoneChangeVerification.objects.get(businessman=user, id=phone_change_verification_id)

            self._resend_verification_code(user.phone, vcode.previous_phone_verification)
            self._resend_verification_code(vcode.new_phone, vcode.new_phone_verification)
        except ObjectDoesNotExist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)

    def check_phone_confirm_code_is_valid_and_delete(self, user: Businessman, verification_code_id: int, code: str):
        try:
            vcode = VerificationCodes.objects.get(id=verification_code_id, businessman=user, code=code,
                                                  expiration_time__gt=timezone.now(),
                                                  used_for=VerificationCodes.USED_FOR_PHONE_VERIFICATION)
            vcode.delete()
        except ObjectDoesNotExist as e:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED)

    def check_phone_change_verification_codes_and_delete(self, user: Businessman,
                                                         phone_change_verification_id: int,
                                                         previous_phone_code: str,
                                                         new_phone_code: str) -> PhoneChangeVerification:
        try:
            result = PhoneChangeVerification.objects.get(businessman=user,
                                                         id=phone_change_verification_id,
                                                         previous_phone_verification__code=previous_phone_code,
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
