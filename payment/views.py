<<<<<<< HEAD
from datetime import datetime

import jdatetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from payment.exceptions import PaymentCreationFailedException, PaymentVerificationFailedException
from .models import Payment, PaymentTypes
=======
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from zeep import Client
from django.utils.translation import ugettext as _
from .models import Payment
>>>>>>> 966c21bb2f3eaaf1820cec3c460ff4545f6ac077
from .serializers import (PaymentCreationSerializer,
                         PaymentConstantAmountCreationSerializer,
                         PaymentResultSerializer,
                         PaymentListSerializer,
                         PaymentDetailSerializer,
                         )

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

def verify(request):
<<<<<<< HEAD


    current_time = datetime.now()
    if request.GET.get('Status') != 'OK':
        return render(request, "payment/payment-failed.html", {'current_time': current_time})

    try:
        p = Payment.objects.get(authority=request.GET['Authority'])
        p.verify()
        local_pay_date = jdatetime.date.fromgregorian(date=p.verification_date).strftime("%y/%m/%d %H:%M")

        if p.payment_type == PaymentTypes.SMS:
            credit = p.businessman.smspanelinfo.credit
            return render(request, "payment/sms-charge-sucess.html",
                          {'payment': p, 'credit': credit,
                           'verification_date': local_pay_date,
                           'current_time': current_time})

        return render(request, 'payment/activation-sucess.html',
                      {'payment': p,
                       'verification_date': local_pay_date,
                       'current_time': current_time})

    except ObjectDoesNotExist:
        return HttpResponse('پرداختی با این شناسه وجود ندارد')
    except PaymentVerificationFailedException as e:
        return render(request, "payment/payment-failed.html", {'current_time': datetime.now()})

=======
    if request.GET.get('Status') == 'OK':
        p = Payment.objects.get(authority=request.GET['Authority'])
        return p.verify(request)
    else:
        return redirect(settings.ZARINPAL.get("FORWARD_URL"))
>>>>>>> 966c21bb2f3eaaf1820cec3c460ff4545f6ac077


@api_view(['POST'])
def create_payment_sms_credit(request):
    serializer = PaymentCreationSerializer(data=request.data, context={'request': request, 'type': PaymentTypes.SMS})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer.save()
    except PaymentCreationFailedException as e:
        return Response({'status': e.returned_status}, status=status.HTTP_424_FAILED_DEPENDENCY)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_constant_payment(request):
    serializer = PaymentConstantAmountCreationSerializer(data=request.data,context={'request': request})

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

<<<<<<< HEAD
        serializer = PaymentResultSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
=======

class DetailPayView(generics.RetrieveAPIView):
    serializer_class = PaymentDetailSerializer
    queryset = Payment.objects.all()
>>>>>>> 966c21bb2f3eaaf1820cec3c460ff4545f6ac077
