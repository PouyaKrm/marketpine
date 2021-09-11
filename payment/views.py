import jdatetime
from django.conf import settings
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.views import APIView

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from base_app.views import BaseListAPIView
from common.util.date_helpers import get_end_day_of_jalali_month
from common.util.http_helpers import bad_request, created, ok
from smspanel.permissions import HasActiveSMSPanel
from users.permissions import IsBusinessmanAuthorized
from .models import Payment
from .permissions import ActivatePanelPermission
from .serializers import (SMSCreditPaymentCreationSerializer,
                          SubscriptionPaymentCreationSerializer,
                          PaymentListSerializer, SubscriptionPlansSerializer, BillingSummerySerializer,
                          WalletIncreaseCreditSerializer, PaymentResultSerializer
                          )
from .services import payment_service, wallet_billing_service

frontend_url = settings.FRONTEND_URL


class VerifyPayment(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request):
        pay_status = request.GET.get('Status')
        authority = request.GET.get('Authority')

        if (pay_status is None or (pay_status != 'OK' and pay_status != 'NOK')) or authority is None:
            raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_INFORMATION_INCORRECT)
        p = payment_service.verify_payment_by_authority(authority, pay_status)
        sr = PaymentResultSerializer(p)
        return ok(sr.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsBusinessmanAuthorized, HasActiveSMSPanel])
def create_payment_sms_credit(request):
    serializer = SMSCreditPaymentCreationSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return bad_request(serializer.errors)

    p = payment_service.create_payment_for_smspanel_credit(
        request.user,
        serializer.validated_data.get('amount')
    )
    serializer = SMSCreditPaymentCreationSerializer(p)
    return ok(serializer.data)


class WalletCreditPaymentCreation(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBusinessmanAuthorized]

    def post(self, request):
        sr = WalletIncreaseCreditSerializer(data=request.data, request=request)
        if not sr.is_valid():
            return bad_request(sr.errors)

        p = payment_service.create_payment_for_wallet_credit(
            request.user,
            sr.validated_data.get('amount')
        )

        sr = WalletIncreaseCreditSerializer(p)
        return ok(sr.data)


class SubscriptionPaymentCreate(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBusinessmanAuthorized]

    def post(self, request: Request):
        sr = SubscriptionPaymentCreationSerializer(data=request.data, request=request)

        if not sr.is_valid():
            return bad_request(sr.errors)

        p = payment_service.create_payment_for_subscription(request.user,
                                                            sr.validated_data.get('plan'))
        sr = SubscriptionPaymentCreationSerializer(p)
        return ok(sr.data)

    def get(self, request: Request):
        plans = payment_service.get_all_plans()
        sr = SubscriptionPlansSerializer(plans, many=True)
        return ok(sr.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsBusinessmanAuthorized, ActivatePanelPermission])
def panel_activation_payment(request):
    serializer = SubscriptionPaymentCreationSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
        return bad_request(serializer.errors)

    p = payment_service.create_panel_activation_payment(request,
                                                        serializer.validated_data.get('plan'),
                                                        serializer.validated_data.get('description'))
    serializer = SubscriptionPaymentCreationSerializer(p)
    return created(serializer.data)


class ListPayView(BaseListAPIView):
    serializer_class = PaymentListSerializer

    def get_queryset(self):
        queryset = Payment.objects.filter(businessman=self.request.user).filter(refid__isnull=False) \
            .order_by('-verification_date')
        return queryset


class BillingSummeryAPIView(APIView):

    def get(self, request: Request):
        m = self._get_month(request)
        day = None
        if m is not None:
            now = jdatetime.datetime.now().replace(month=m)
            day = self._get_day(request, now)
        result = wallet_billing_service.get_billing_summery(request.user, m, day)

        sr = BillingSummerySerializer(result, many=True)
        return ok(sr.data)

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

