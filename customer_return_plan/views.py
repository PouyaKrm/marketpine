from rest_framework.decorators import api_view
from rest_framework.request import Request

from base_app.views import BaseListAPIView
from common.util import create_detail_error
from common.util.http_helpers import ok, bad_request, not_found
from customer_return_plan.festivals.services import FestivalService
from customer_return_plan.models import Discount
from customer_return_plan.serializers import ReadOnlyDiscountSerializer, ApplyDiscountSerializer, \
    ReadOnlyDiscountWithUsedFieldSerializer
from customer_return_plan.services import DiscountService
from customers.serializers import CustomerListCreateSerializer
from customers.services import CustomerService
from .festivals.models import Festival
from .invitation.models import FriendInvitation

discount_service = DiscountService()
festival_service = FestivalService()
customer_service = CustomerService()

@api_view(['GET'])
def dashboard_data(request: Request):
    festivals = Festival.objects.count()
    friend_invitations = FriendInvitation.objects.count()
    return ok({'festivals_total': festivals, 'invitations_total': friend_invitations})


class DiscountListAPIView(BaseListAPIView):
    serializer_class = ReadOnlyDiscountSerializer

    def get_queryset(self):
        code = self.request.query_params.get('code')
        query = Discount.objects.filter(businessman=self.request.user).order_by('-create_date')
        if code:
            return query.filter(discount_code=code).all()
        return query.all()


@api_view(['POST'])
def apply_discount(request: Request):
    serializer = ApplyDiscountSerializer(data=request.data, context={'user': request.user})

    if not serializer.is_valid():
        return bad_request(serializer.errors)
    user = request.user
    code = serializer.validated_data.get('discount_code')
    phone = serializer.validated_data.get('phone')
    result = DiscountService().apply_discount(user, code, phone)
    if not result[0]:
        return bad_request(create_detail_error('مشتری مجاز به استفاده از کد تخفیف نیست'))
    return ok(ReadOnlyDiscountSerializer(result[1]).data)


class CustomerDiscountsListAPIView(BaseListAPIView):
    serializer_class = ReadOnlyDiscountWithUsedFieldSerializer

    def get_serializer_context(self):
        customer = customer_service.get_businessman_customer_by_id(self.request.user, self.kwargs.get('customer_id'))
        return {'customer': customer, 'user': self.request.user}

    def get_queryset(self):
        use_state = self.request.query_params.get('ust')
        customer = customer_service.get_businessman_customer_by_id(self.request.user, self.kwargs.get('customer_id'))
        default = discount_service.get_customer_discounts_for_businessman(self.request.user, customer)
        if use_state is None:
            return default

        use_state = use_state.lower()

        if use_state == 'used':
            return discount_service.get_customer_used_discounts_for_businessman(self.request.user, customer)
        elif use_state == 'unused':
            return discount_service.get_customer_unused_discounts_for_businessman(self.request.user, customer)

        elif use_state == 'available':
            return discount_service.get_customer_available_discounts_for_businessman(self.request.user, customer)
        else:
            return default


@api_view(['GET'])
def check_festival_name_or_discount_code_exists(request: Request):
    """
    NEW - use this method when user is registering a festival.
    To Check that festival name or discount code already exist Use This method.
    one of the parameters are optional. but if none of them are presented Response
    with 400 status code will be returned.
    parameter : name: name of the festival. - code: discount code of the festival
    :param request:
    :return:
    """
    code = request.query_params.get('code')
    name = request.query_params.get('fname')
    payload = {"fname": False, "code": False}

    if (name is None) and (code is None):
        return bad_request(create_detail_error('name and code parameters are required'))

    if (name is not None) and festival_service.festival_by_name_exists(request.user, name):
        payload['fname'] = True

    if (code is not None) and discount_service.discount_exists_by_discount_code(request.user, code):
        payload['code'] = True

    return ok(payload)


@api_view(['DELETE'])
def remove_customer_from_discount(request: Request, discount_id: int, customer_id: int):
    result = discount_service.delete_customer_from_discount(request.user, discount_id, customer_id)
    if not result[0]:
        return not_found(create_detail_error('آیدی کد تخفیف اشتباه است'))
    if result[0] and not result[1]:
        return bad_request(create_detail_error('مشتری از تخفیف استفاده نکرده است'))
    discount_serializer = ReadOnlyDiscountSerializer(result[2])
    customer_serializer = CustomerListCreateSerializer(result[3], context={'user': request.user})
    return ok({"discount": discount_serializer.data, "customer": customer_serializer.data})
