from django.views.generic.base import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from users.models import AuthStatus


class AuthDocsNotUploaded(BasePermission):

    message = 'فقط افرادی که احراز هویت نشده اند می توانند مدارک خود را ارسال کنند'

    def has_permission(self, request: Request, view: View):

        return request.user.authorized == AuthStatus.UNAUTHORIZED


class IsAuthDocsUploaded(BasePermission):

    message = 'همه ی مدارک مورد نیاز ارسال نشده اند'

    def has_permission(self, request: Request, view: View):

        if not hasattr(request.user, 'businessmanauthdocs'):
            return False

        auth_doc = request.user.businessmanauthdocs

        return auth_doc.form.name and auth_doc.national_card.name and auth_doc.birth_certificate.name


class IsPhoneNotVerified(BasePermission):

    message = 'شماره تلفن قبلا تایید شده'

    def has_permission(self, request: Request, view: View) -> bool:

        return not request.user.is_phone_verified
