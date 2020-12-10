from datetime import timedelta, datetime
from django.db.models.expressions import F
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.views import APIView

from common.util.http_helpers import ok
from dashboard.serializers import DashboardSerializer


@api_view(['GET'])
def customers_total(request: Request):

    return Response({'customers_total': request.user.customers.count()}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_top_5_customers(request: Request):

    data = request.user.customerpurchase_set.annotate(phone=F('customer__phone')).values('phone').\
        annotate(purchase_sum=Sum('amount')).order_by('-purchase_sum')[:5]

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def total_amount_days_in_week(request: Request):

    """
    NEW
    Represent amount of purchases in each day of current week
    :param request:
    :return: Response with result and 200 status code
    """

    today = datetime.now().date()
    day_of_week = today - timedelta(days=today.weekday() + 2)  # beginning of the week in IR (saturday)
    result = []
    for _ in range(7):
        info = request.user.customerpurchase_set.filter(purchase_date__date=day_of_week).\
            aggregate(purchase_sum=Sum('amount'))
        info['date'] = day_of_week
        result.append(info)
        day_of_week += timedelta(days=1)
    return Response(result, status=status.HTTP_200_OK)


class DashboardAPIView(APIView):

    def get(self, request):

        sr = DashboardSerializer(request.user, request=request)
        return ok(sr.data)
