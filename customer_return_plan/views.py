from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework import generics

from common.util import create_detail_error
from common.util.http_helpers import ok, bad_request
from customer_return_plan.models import Discount
from customer_return_plan.serializers import ReadOnlyDiscountSerializer, ApplyDiscountSerializer, \
    ReadOnlyDiscountWithUsedFieldSerializer
from customer_return_plan.services import DiscountService
from .festivals.models import Festival
from .invitation.models import FriendInvitation


@api_view(['GET'])
def dashboard_data(request: Request):
    festivals = Festival.objects.count()
    friend_invitations = FriendInvitation.objects.count()
    return ok({'festivals_total': festivals, 'invitations_total': friend_invitations})


class DiscountListAPIView(generics.ListAPIView):
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


class CustomerDiscountsListAPIView(ListAPIView):
    serializer_class = ReadOnlyDiscountWithUsedFieldSerializer

    def get_serializer_context(self):
        return {'customer_id': self.kwargs.get('customer_id')}

    def get_queryset(self):
        return DiscountService().get_customer_discounts_by_customer_id(self.request.user,
                                                                       self.kwargs.get('customer_id'))
