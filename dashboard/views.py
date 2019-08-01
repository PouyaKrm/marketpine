from django.db.models.expressions import F
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Sum


@api_view(['GET'])
def customers_total(request: Request):

    return Response({'customers_total': request.user.customers.count()}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_top_5_customers(request: Request):

    data = request.user.customerpurchase_set.annotate(phone=F('customer__phone')).values('phone').\
        annotate(purchase_sum=Sum('amount')).order_by('-purchase_sum')[:5]

    return Response(data, status=status.HTTP_200_OK)

