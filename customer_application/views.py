from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.request import Request

from common.util.http_helpers import bad_request, no_content, get_user_agent, ok
from customer_application.exceptions import CustomerServiceException
from customer_application.serializers import CustomerPhoneSerializer, CustomerLoginSerializer, \
    BaseBusinessmanSerializer, BusinessmanRetrieveSerializer
from .base_views import CustomerAuthenticationSchema, BaseListAPIView, BaseRetrieveAPIView, BaseAPIView
from .services import customer_auth_service, customer_data_service


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
    except CustomerServiceException as e:
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
        return ok({'token': t})
    except CustomerServiceException as e:
        return bad_request(e.http_message)


class BusinessmansList(BaseListAPIView):

    serializer_class = BaseBusinessmanSerializer

    def get_queryset(self):
        return customer_data_service.get_all_businessmans(self.request.user)

    def get_object(self):
        return customer_data_service.get_all_businessmans(self.request.user)


class BusinessmanRetrieveAPIView(BaseAPIView):

    serializer_class = BusinessmanRetrieveSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return customer_data_service.get_businessman_of_customer_by_id(self.request.user, self.kwargs.get('id'))

    def get(self, request: Request, businessman_id: int):
        try:
            b = customer_data_service.get_businessman_of_customer_by_id(request.user, businessman_id)
            sr = BusinessmanRetrieveSerializer(b, context={'request': request})
            return ok(sr.data)
        except CustomerServiceException as e:
            return bad_request(e.http_message)

