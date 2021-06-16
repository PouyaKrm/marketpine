import logging

from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request

from common.util.http_helpers import bad_request, ok
from customer_application.base_views import CustomerAuthenticationSchema, BaseListAPIView
from customer_application.exceptions import CustomerServiceException
from customer_application.pagination import CustomerAppListPaginator
from customer_application.return_plan.serializers import FriendInvitationSerializer, CustomerReadonlyDiscountSerializer
from customer_application.return_plan.services import return_plan_service, InvitationInfo
from customer_application.services import customer_data_service
from customer_return_plan.services import customer_discount_service

logger = logging.getLogger(__name__)

@api_view(['POST'])
@authentication_classes([CustomerAuthenticationSchema])
def friend_invitation(request: Request):
    sr = FriendInvitationSerializer(data=request.data, request=request, context={'user': request.user})
    if not sr.is_valid():
        return bad_request(sr.errors)
    try:
        inf = InvitationInfo()
        inf.businessman = sr.validated_data.get('businessman')
        inf.customer = request.user
        inf.friend_phone = sr.validated_data.get('friend_phone')
        inf.full_name = sr.validated_data.get('full_name')
        inf.friend_full_name = sr.validated_data.get('friend_full_name')
        result = return_plan_service.add_friend_invitation(inf)
        return ok(result)
    except CustomerServiceException as e:
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


@api_view(['GET'])
@authentication_classes([CustomerAuthenticationSchema])
def customer_businessman_discounts_list_api_view(request: Request, businessman_id: int):

    customer = request.user
    p = CustomerAppListPaginator()
    ust = request.query_params.get('ust', 'available')
    try:
        businessman = customer_data_service.get_businessman_by_id_or_page_id(businessman_id)
        if ust == 'used':
            discounts = customer_discount_service.get_customer_used_discounts(request.user).filter(
                businessman=businessman)
            # discounts = discount_service.get_customer_used_discounts_for_businessman(businessman, customer)
        else:
            # discounts = discount_service.get_customer_available_discounts_for_businessman(businessman, customer)
            discounts = customer_discount_service.get_customer_available_discount(customer).filter(
                businessman=businessman)
        result_page = p.paginate_queryset(discounts, request)
        sr = CustomerReadonlyDiscountSerializer(result_page, request=request, many=True)
        return p.get_paginated_response(sr.data)
    except CustomerServiceException as e:
        logger.error(e)
        return bad_request(e.http_message)

