from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request

from common.util.http_helpers import bad_request, ok
from customer_application.base_views import CustomerAuthenticationSchema
from customer_application.exceptions import CustomerServiceException
from customer_application.return_plan.serializers import FriendInvitationSerializer
from customer_application.return_plan.services import return_plan_service


@api_view(['POST'])
@authentication_classes([CustomerAuthenticationSchema])
def friend_invitation(request: Request):
    sr = FriendInvitationSerializer(data=request.data, request=request, context={'user': request.user})
    if not sr.is_valid():
        return bad_request(sr.errors)
    try:
        result = return_plan_service.add_friend_invitation(request.user, sr.validated_data.get('businessman'),
                                                           sr.validated_data.get('friend_phone'))
        return ok(result)
    except CustomerServiceException as e:
        return bad_request(e.http_message)
