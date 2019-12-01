from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect
from zeep import Client
from django.utils.translation import ugettext as _
from .models import Payment
from .serializers import (PaymentCreationSerializer,
                         PaymentConstantAmountCreationSerializer,
                         PaymentResultSerializer,)

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView

def verify(request):

    if request.GET.get('Status') == 'OK':
        p = Payment.objects.get(authority=request.GET['Authority'])
        return p.verify(request)
    else:
        return HttpResponse(_('Transaction failed or canceled by user'))


# def pay(request):
#     p=Payment(amount=1000,businessman=request.user,description="for test")
#     p.save()
#     # return p.pay(request)
#     return HttpResponseRedirect('https://www.zarinpal.com/')


@api_view(['POST'])
def create_payment (request):
    serializer=PaymentCreationSerializer(data=request.data,context={'request': request})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def create_constant_payment (request):
    serializer=PaymentConstantAmountCreationSerializer(data=request.data,context={'request': request})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class ResultPay(APIView):

    def post(self, request):

        authority = request.POST['authority']
        # authority = request.query_params.get('authority')
        queryset = Payment.objects.get(authority=authority)

        serializer = PaymentResultSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def result_pay (request):
#     query =Payment.objects.get(authority= request.query_params.get('authority'))
#     serializer=PaymentResultSerializer(query,context={'request': request})
#
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     serializer.save()
#     return Response(serializer.data, status=status.HTTP_201_CREATED)



# class ResultPayView(generics.ListAPIView):
#     serializer_class = PaymentResultSerializer
#     # lookup_field = 'authority'
#     # queryset = Payment.objects.all()
#     def get_queryset(self):
#         authority=self.request.query_params.get('authority', None)
#         queryset = Payment.objects.get(authority=authority)
