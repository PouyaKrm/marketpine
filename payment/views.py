from datetime import datetime

import jdatetime
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from base_app.views import BaseListAPIView
from common.util.http_helpers import bad_request, created
from common.util.kavenegar_local import APIException
from payment.exceptions import PaymentCreationFailedException, PaymentVerificationFailedException, \
    PaymentAlreadyVerifiedException, PaymentOperationFailedException
from smspanel.permissions import HasActiveSMSPanel
from users.permissions import IsBusinessmanAuthorized
from .models import PaymentTypes
from django.http import HttpResponse
from django.conf import settings

from .models import Payment
from .serializers import (SMSCreditPaymentCreationSerializer,
                          PanelActivationPaymentCreationSerializer,
                          PaymentListSerializer, PanelActivationPlansSerializer
                          )

from .permissions import ActivatePanelPermission

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics, permissions

from .services import payment_service

frontend_url = settings.FRONTEND_URL


def verify(request):
    current_time = datetime.now()
    pay_status = request.GET.get('Status')

    authority = request.GET.get('Authority')

    if pay_status is None or authority is None:
        return redirect(frontend_url)
    if pay_status != 'OK':
        return render(request, "payment/payment-failed.html", {'current_time': current_time,
                                                               'frontend_url': frontend_url})

    try:
        p = Payment.objects.get(authority=authority)
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
                       'current_time': current_time,
                       'frontend_url': frontend_url})

    except ObjectDoesNotExist:
        return HttpResponse('پرداختی با این شناسه وجود ندارد')
    except (PaymentVerificationFailedException, APIException) as e:
        return render(request, "payment/payment-failed.html", {'current_time': current_time,
                                                               'frontend_url': frontend_url})
    except PaymentAlreadyVerifiedException:
        return redirect(frontend_url)
    except PaymentOperationFailedException:
        return render(request, "payment/operation-failed.html", {'current_time': current_time,
                                                                 'frontend_url': frontend_url})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsBusinessmanAuthorized, HasActiveSMSPanel])
def create_payment_sms_credit(request):
    serializer = SMSCreditPaymentCreationSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer.save()
    except PaymentCreationFailedException as e:
        return Response({'status': e.returned_status}, status=status.HTTP_424_FAILED_DEPENDENCY)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsBusinessmanAuthorized, ActivatePanelPermission])
def panel_activation_payment(request):
    serializer = PanelActivationPaymentCreationSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
        return bad_request(serializer.errors)

    p = payment_service.create_panel_activation_payment(request,
                                                        serializer.validated_data.get('plan'),
                                                        serializer.validated_data.get('description'))
    serializer = PanelActivationPaymentCreationSerializer(p)
    return created(serializer.data)


class ListPayView(BaseListAPIView):
    serializer_class = PaymentListSerializer

    def get_queryset(self):
        queryset = Payment.objects.filter(businessman=self.request.user).filter(refid__isnull=False) \
            .order_by('-verification_date')
        return queryset


class PanelActivationPlansListAPIView(generics.ListAPIView):
    serializer_class = PanelActivationPlansSerializer
    queryset = payment_service.get_all_plans()
    pagination_class = None
