from datetime import datetime

import jdatetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.views import APIView

from base_app.error_codes import ApplicationErrorException
from base_app.views import BaseListAPIView
from common.util.date_helpers import get_end_day_of_jalali_month
from common.util.http_helpers import bad_request, created, ok
from common.util.kavenegar_local import APIException
from payment.exceptions import PaymentVerificationFailedException, \
    PaymentAlreadyVerifiedException, PaymentOperationFailedException
from smspanel.permissions import HasActiveSMSPanel
from users.permissions import IsBusinessmanAuthorized
from .models import Payment
from .models import PaymentTypes
from .permissions import ActivatePanelPermission
from .serializers import (SMSCreditPaymentCreationSerializer,
                          PanelActivationPaymentCreationSerializer,
                          PaymentListSerializer, PanelActivationPlansSerializer, BillingSummerySerializer,
                          WalletIncreaseCreditSerializer, PaymentResultSerializer
                          )
from .services import payment_service, wallet_billing_service

frontend_url = settings.FRONTEND_URL


class VerifyPayment(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request):
        pay_status = request.GET.get('Status')
        authority = request.GET.get('Authority')
        if pay_status is None or authority is None:
            return redirect(frontend_url)
        # if pay_status != 'OK':
        #     return render(request, "payment/payment-failed.html", {
        #         'current_time': current_time,
        #         'frontend_url': frontend_url
        #     })

        try:
            result = payment_service.verify_payment_by_authority(authority, pay_status)
            p = result[0]
            sr = PaymentResultSerializer(p)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)
            # if ex.http_message == ApplicationErrorCodes.RECORD_NOT_FOUND:
            #     message = 'پرداخت موردنظر پیدا نشد'
            # else:
            #     message = ex.http_message['message']
            # return render(request, "payment/payment-failed.html", {'current_time': current_time,
            #                                                        'frontend_url': frontend_url,
            #                                                        'exception_message': message
            #                                                        })


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
        return bad_request(serializer.errors)

    try:
        p = payment_service.create_payment_for_smspanel_credit(
            request,
            request.user,
            serializer.validated_data.get('amount')
        )
        serializer = SMSCreditPaymentCreationSerializer(p)
        return ok(serializer.data)
    except ApplicationErrorException as ex:
        return bad_request(ex.http_message)


class WalletCreditPaymentCreation(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBusinessmanAuthorized]

    def post(self, request):

        sr = WalletIncreaseCreditSerializer(data=request.data, request=request)
        if not sr.is_valid():
            return bad_request(sr.errors)
        try:
            p = payment_service.create_payment_for_wallet_credit(request,
                                                                 request.user,
                                                                 sr.validated_data.get('amount')
                                                                 )

            sr = WalletIncreaseCreditSerializer(p)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)


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


class BillingSummeryAPIView(APIView):

    def get(self, request: Request):
        try:
            m = self._get_month(request)
            day = None
            if m is not None:
                now = jdatetime.datetime.now().replace(month=m)
                day = self._get_day(request, now)
            result = wallet_billing_service.get_billing_summery(request.user, m, day)

            sr = BillingSummerySerializer(result, many=True)
            return ok(sr.data)

        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)

    def _get_month(self, request: Request) -> int:
        err_message = 'مقدار ماه غیر مجاز است'
        m = request.query_params.get('month')
        if m is None:
            return None
        try:
            m = int(m)
            if m <= 0 or m > 12:
                raise ApplicationErrorException(err_message)
            return m
        except ValueError as ex:
            raise ApplicationErrorException(err_message, ex)

    def _get_day(self, request: Request, month_date: jdatetime.datetime) -> int:
        err_message = 'مقدار روز غیر مجاز است'
        day = request.query_params.get('day')
        if day is None:
            return None

        try:
            day = int(day)
            end_day = get_end_day_of_jalali_month(month_date)
            if day <= 0 or day > end_day:
                raise ApplicationErrorException(err_message)

            return day
        except ValueError as ex:
            raise ApplicationErrorException(err_message, ex)

    def _get_year_result_dict(self, result) -> dict:
        print(type(result))
        return None
