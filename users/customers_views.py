from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request

from common.util.http_helpers import bad_request, no_content
from .exceptions import AuthenticationException
from .serializers import CustomerPhoneSerializer
from .services import customer_auth_service


@api_view(['POST'])
@permission_classes([])
def send_login_code(request: Request):
    sr = CustomerPhoneSerializer(data=request.data)
    if not sr.is_valid():
        return bad_request(sr.errors)
    try:
        customer_auth_service.send_login_code(sr.validated_data.get('phone'))
        return no_content()
    except AuthenticationException as e:
        return bad_request(e.http_message)
