from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework import generics

from common.util.http_helpers import ok
from customer_return_plan.models import Discount
from customer_return_plan.serializers import ReadOnlyDiscountSerializer
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


