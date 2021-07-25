import logging

from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request

from base_app.error_codes import ApplicationErrorException
from common.util.http_helpers import bad_request, ok
from customer_application.base_views import CustomerAuthenticationSchema, BaseListAPIView, BaseAPIView
from customer_application.return_plan.serializers import FriendInvitationSerializer, CustomerReadonlyDiscountSerializer, \
    CreateLoyaltyDiscountSerializer
from customer_application.return_plan.services import return_plan_service, InvitationInfo
from customer_return_plan.services import customer_discount_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@authentication_classes([CustomerAuthenticationSchema])
def friend_invitation(request: Request):
    try:
        sr = FriendInvitationSerializer(data=request.data, request=request, context={'user': request.user})
        if not sr.is_valid():
            return bad_request(sr.errors)
        inf = InvitationInfo()
        inf.businessman = sr.validated_data.get('businessman')
        inf.customer = request.user
        inf.friend_phone = sr.validated_data.get('friend_phone')
        inf.full_name = sr.validated_data.get('full_name')
        inf.friend_full_name = sr.validated_data.get('friend_full_name')
        result = return_plan_service.add_friend_invitation(inf)
        return ok(result)
    except ApplicationErrorException as e:
        logger.error(e)
        return bad_request(e.http_message)


class CustomerDiscountListAPIView(BaseListAPIView):

    def get_queryset(self):
        ust = self.request.query_params.get('ust', 'available')
        businessman_id = self.request.query_params.get('businessman')
        if ust == 'used':
            query = customer_discount_service.get_customer_used_discounts(self.request.user)
        else:
            query = customer_discount_service.get_customer_available_discount(self.request.user)

        if businessman_id is not None and businessman_id.isnumeric() and int(businessman_id) > 0:
            query = query.filter(businessman__id=int(businessman_id))

        return query.order_by('-create_date')

    serializer_class = CustomerReadonlyDiscountSerializer


class CustomerLoyaltyDiscount(BaseAPIView):

    def post(self, request: Request):
        try:
            sr = CreateLoyaltyDiscountSerializer(data=request.data, request=request)
            if not sr.is_valid():
                return bad_request(sr.errors)
            discount = return_plan_service.create_loyalty_discount(
                request.user,
                sr.validated_data.get('businessman_id'),
                sr.validated_data.get('discount_settings_id')
            )

            sr = CreateLoyaltyDiscountSerializer(discount, request=request)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)
