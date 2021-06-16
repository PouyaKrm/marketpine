import logging

from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request

from base_app.error_codes import ApplicationErrorException
from common.util.http_helpers import bad_request, no_content, get_user_agent, ok
from customer_application.serializers import CustomerPhoneSerializer, CustomerLoginSerializer, \
    BaseBusinessmanSerializer, BusinessmanRetrieveSerializer, FestivalNotificationSerializer, \
    PostNotificationSerializer, CustomerProfileSerializer, CustomerCodeSerializer
from .base_views import BaseListAPIView, BaseAPIView
from .error_codes import CustomerAppErrors
from .pagination import CustomerAppListPaginator
from .services import customer_auth_service, customer_data_service

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([])
def send_login_code(request: Request):
    resend = request.query_params.get('resend')
    sr = CustomerPhoneSerializer(data=request.data)
    if not sr.is_valid():
        return bad_request(sr.errors)
    try:
        if resend is not None and resend.lower() == 'true':
            customer_auth_service.resend_one_time_password(sr.validated_data.get('phone'))
        else:
            customer_auth_service.send_login_code(sr.validated_data.get('phone'))
        return no_content()
    except ApplicationErrorException as e:
        logger.error(e)
        return bad_request(e.http_message)


@api_view(['POST'])
@permission_classes([])
def customer_login(request: Request):
    sr = CustomerLoginSerializer(data=request.data)
    if not sr.is_valid():
        return bad_request(sr.errors)

    ua = get_user_agent(request)
    phone = sr.validated_data.get('phone')
    code = sr.validated_data.get('code')
    try:
        t = customer_auth_service.login(phone, code, ua)
        return ok(t)
    except ApplicationErrorException as e:
        logger.error(e)
        return bad_request(e.http_message)


class ProfileAPIView(BaseAPIView):

    def get(self, request: Request):
        resp = customer_data_service.get_profile(request.user)
        return ok(resp)

    def put(self, request: Request):
        sr = CustomerProfileSerializer(data=request.data, request=request)
        if not sr.is_valid():
            return bad_request(sr.errors)
        fn = sr.validated_data.get('full_name')
        c = customer_data_service.update_full_name(request.user, fn)
        resp = customer_data_service.get_profile(c)
        return ok(resp)


class PhoneUpdateSendCode(BaseAPIView):

    def post(self, request: Request):

        sr = CustomerPhoneSerializer(data=request.data)
        resend_val = request.query_params.get('resend')
        resend = resend_val is not None and resend_val.lower() == 'true'
        if not sr.is_valid():
            return bad_request(sr.errors)
        try:
            if resend:
                customer_auth_service.resend_phone_update_code(request.user)
                return no_content()
            phone = sr.validated_data.get('phone')
            customer_auth_service.send_phone_update_code(request.user, phone)
            return no_content()
        except ApplicationErrorException as e:
            return bad_request(e.http_message)


class PhoneUpdate(BaseAPIView):

    def put(self, request: Request):
        sr = CustomerCodeSerializer(data=request.data)
        if not sr.is_valid():
            return bad_request(sr.errors)
        try:
            code = sr.validated_data.get('code')
            result = customer_auth_service.update_phone(request.user, code)
            return ok(result)
        except ApplicationErrorException as e:
            return bad_request(e.http_message)


class BusinessmansList(BaseListAPIView):

    serializer_class = BaseBusinessmanSerializer
    pagination_class = CustomerAppListPaginator

    def get_queryset(self):
        bn = self.request.query_params.get('bn', None)
        return customer_data_service.get_all_businessmans(self.request.user, bn)

    def get_object(self):
        return customer_data_service.get_all_businessmans(self.request.user)


class BusinessmanRetrieveAPIView(BaseAPIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, page_businessman_id: int):
        try:
            b = customer_data_service.get_businessman_by_id_or_page_id(page_businessman_id)
            sr = BusinessmanRetrieveSerializer(b, request=request)
            return ok(sr.data)
        except ApplicationErrorException as e:
            logger.error(e)
            return bad_request(e.http_message)

    def post(self, request: Request, page_businessman_id: int):
        if request.user.is_anonymous:
            err = CustomerAppErrors.error_dict(CustomerAppErrors.USER_SHOULD_LOGIN)
            return bad_request(err)
        try:
            b = customer_data_service.add_customer_to_businessman(page_businessman_id, request.user)
            sr = BusinessmanRetrieveSerializer(b, request=request)
            return ok(sr.data)
        except ApplicationErrorException as e:
            return bad_request(e.http_message)


class NotificationAPIView(BaseAPIView):

    def get(self, request):
        r = customer_data_service.get_notifications(self.request.user)
        f_sr = None
        p_sr = None
        if r['festival'] is not None:
            f_sr = FestivalNotificationSerializer(r['festival'], request=self.request).data

        if r['post'] is not None:
            p_sr = PostNotificationSerializer(r['post'], request=self.request).data
        return ok({'festival': f_sr, 'post': p_sr})
