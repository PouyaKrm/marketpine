from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from zeep import Client
from django.utils.translation import ugettext as _
from .models import Payment
from .serializers import (PaymentCreationSerializer,
                         PaymentConstantAmountCreationSerializer,
                         PaymentResultSerializer,
                         PaymentListSerializer,
                         PaymentDetailSerializer,
                         )

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
        return redirect(settings.ZARINPAL.get("FORWARD_URL"))

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
    def get(self, request):
        authority = self.request.data['authority']
        queryset = get_object_or_404(Payment,authority =authority)
        serializer=PaymentResultSerializer(queryset)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ListPayView(generics.ListAPIView):
    serializer_class = PaymentListSerializer
    def get_queryset(self):
        queryset = Payment.objects.filter(businessman=self.request.user)
        return queryset


class DetailPayView(generics.RetrieveAPIView):
    serializer_class = PaymentDetailSerializer
    queryset = Payment.objects.all()
