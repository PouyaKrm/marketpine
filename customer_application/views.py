from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request

from common.util.http_helpers import bad_request, no_content, get_user_agent, ok
from customer_application.exceptions import AuthenticationException
from users.serializers import CustomerPhoneSerializer, CustomerLoginSerializer
from .services import customer_auth_service


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
    except AuthenticationException as e:
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
    except AuthenticationException as e:
        return bad_request(e.http_message)
