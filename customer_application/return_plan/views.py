from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request

from common.util.http_helpers import bad_request, ok
from customer_application.base_views import CustomerAuthenticationSchema, BaseListAPIView
from customer_application.exceptions import CustomerServiceException
from customer_application.return_plan.serializers import FriendInvitationSerializer, CustomerReadonlyDiscountSerializer
from customer_application.return_plan.services import return_plan_service
from customer_return_plan.services import customer_discount_service


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



class CustomerDiscountListAPIView(BaseListAPIView):

    def get_queryset(self):
        ust = self.request.query_params.get('ust', 'available')
        if ust == 'used':
            query = customer_discount_service.get_customer_used_discounts(self.request.user)
        else:
            query = customer_discount_service.get_customer_available_discount(self.request.user)
        # return customer_discount_service.get_customer_available_discount(self.request.user)
        return query
    serializer_class = CustomerReadonlyDiscountSerializer
