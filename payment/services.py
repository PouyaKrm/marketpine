import datetime
from typing import Tuple, List, Optional

import jdatetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.db.models.functions import TruncDay
from django.urls import reverse
from django.utils import timezone
from rest_framework.request import Request
from zeep import Client

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from common.util.date_helpers import get_end_day_of_jalali_month
from customer_return_plan.invitation.services import invitation_service
from panelprofile.models import SMSPanelInfo
from panelprofile.services import sms_panel_info_service
from payment.models import PanelActivationPlans, Payment, PaymentTypes, Wallet, Billing
from users.models import Businessman, BusinessmanCustomer

url = settings.ZARINPAL.get('url')
setting_merchant = settings.ZARINPAL.get('MERCHANT')
wallet_initial_available_credit = settings.WALLET['INITIAL_AVAILABLE_CREDIT']
wallet_minimum_allowed_credit = settings.WALLET['MINIMUM_ALLOWED_CREDIT']
customer_joined_by_panel_cost = settings.BILLING['CUSTOMER_JOINED_BY_PANEL_COST']
customer_joined_by_app_cost = settings.BILLING['CUSTOMER_JOINED_BY_APP_COST']
invited_customer_after_purchase_cost = settings.BILLING['INVITED_CUSTOMER_AFTER_PURCHASE_COST']


class PaymentService:

    def get_all_plans(self):
        return PanelActivationPlans.objects.filter(is_available=True).order_by('duration').all()

    def plan_exist_by_id(self, plan_id: int) -> bool:
        return PanelActivationPlans.objects.filter(id=plan_id).exists()

    def get_plan_by_id(self, plan_id) -> PanelActivationPlans:
        return PanelActivationPlans.objects.get(id=plan_id)

    def create_panel_activation_payment(self, request: Request, plan: PanelActivationPlans,
                                        description: str) -> Payment:
        p = Payment.objects.create(businessman=request.user, payment_type=PaymentTypes.ACTIVATION,
                                   amount=plan.price_in_toman, phone=request.user.phone,
                                   description=description, panel_plan=plan)
        p.pay(request)
        return p

    def create_payment_for_smspanel_credit(self,
                                           request: Request,
                                           user: Businessman,
                                           amount_tomal: float,
                                           ):

        return self._create_payment(request, user, amount_tomal, 'افزایش اعتبار پنل اسمس', Payment.TYPE_SMS)

    def verify_payment_by_authority(self, authority: str, callback_status: str) -> Tuple[Payment, SMSPanelInfo]:

        if callback_status != "OK" and callback_status != "NOK":
            raise ValueError('invalid callback status')

        p = self._get_payment_by_authority(authority)
        p.call_back_status = callback_status
        p.save()
        try:
            self._check_payment_verified_before(p)
            self.verify_payment(p)
            if p.is_payment_type_sms():
                sms_panel_info_service.get_panel_increase_credit_in_tomans(p.businessman, p.amount)
            return p, sms_panel_info_service.get_buinessman_sms_panel(p.businessman)
        except Exception as ex:
            if not isinstance(ex, ApplicationErrorException):
                raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_VERIFICATION_FAILED, ex)
            else:
                raise ex

    def verify_payment(self, p: Payment):
        try:
            self._check_payment_verified_before(p)
            merchant = setting_merchant
            client = Client(url)
            result = client.service.PaymentVerification(merchant, p.authority, p.amount)
            p.verification_status = result.Status
            p.save()

            if result.Status == 100:
                p.refid = str(result.RefID)
                p.verification_date = timezone.now()
                p.save()
            elif result.Status != 100:
                raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_WAS_NOT_SUCCESSFUL)
        except Exception as ex:
            if not isinstance(ex, ApplicationErrorException):
                raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_VERIFICATION_FAILED, ex)
            else:
                raise ex

    def _check_payment_verified_before(self, p: Payment):
        if p.is_verified_before():
            raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_ALREADY_VERIFIED)

    def _create_payment(self, request: Request, user: Businessman, amount_toman: float, description: str,
                        payment_type) -> Payment:
        try:
            with transaction.atomic():
                p = Payment.objects.create(
                    businessman=user,
                    amount=amount_toman,
                    description=description,
                    phone=user.phone,
                    payment_type=payment_type
                )
                call_back = request.build_absolute_uri(reverse('payment:verify'), )
                client = Client(url)
                merchant = setting_merchant
                result = client.service.PaymentRequest(merchant, p.amount, p.description, p.businessman.email,
                                                       p.phone, call_back)
                p.create_status = result.Status
                p.save()
            if p.create_status == 100:
                p.authority = result.Authority
                p.save()
            else:
                raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_CREATION_FAILED)

            return p

        except Exception as ex:
            raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_CREATION_FAILED, ex)

    def _get_payment_by_authority(self, authority: str) -> Payment:
        try:
            return Payment.objects.get(authority=authority)
        except ObjectDoesNotExist as ex:
            raise ApplicationErrorException(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)


class BillingSummery:

    def __init__(self, create_date, joined_by: str, amount: int):
        self.create_date = create_date
        self.joined_by = joined_by
        self.amount = amount

    def __str__(self):
        return self.__dict__.__str__()


class WalletAndBillingService:

    def get_businessman_wallet_or_create(self, user: Businessman) -> Wallet:

        try:
            return Wallet.objects.get(businessman=user)
        except ObjectDoesNotExist:
            return Wallet.objects.create(
                businessman=user,
                available_credit=wallet_initial_available_credit,
                used_credit=0
            )

    def payment_for_customer_added(self, bc: BusinessmanCustomer, low_credit_error_code: dict = None) -> Billing:

        if bc.joined_by != BusinessmanCustomer.JOINED_BY_PANEL and bc.joined_by != BusinessmanCustomer.JOINED_BY_INVITATION and bc.joined_by != BusinessmanCustomer.JOINED_BY_CUSTOMER_APP:
            raise ValueError("invalid joined by value in parameter")

        if bc.joined_by == BusinessmanCustomer.JOINED_BY_PANEL:
            return self._customer_add_by_panel_payment(bc, low_credit_error_code)

        if bc.joined_by == BusinessmanCustomer.JOINED_BY_CUSTOMER_APP:
            return self._customer_add_by_app_payment(bc, low_credit_error_code)

    def add_payment_if_customer_invited(self, bc: BusinessmanCustomer) -> Billing:
        invited = invitation_service.is_businessmancustomer_invited(bc)
        if not invited:
            return None
        exist = Billing.objects.filter(customer_added=bc).exists()
        if bc.joined_by == BusinessmanCustomer.JOINED_BY_INVITATION and exist:
            return None

        w = self.check_has_minimum_credit(bc.businessman)
        return self._create_billing_if_not_has_subscription(w, invited_customer_after_purchase_cost, bc)

    def _customer_add_by_panel_payment(self, bc: BusinessmanCustomer, error_code: dict = None) -> Billing:
        w = self.check_has_minimum_credit(bc.businessman, error_code)
        return self._create_billing_if_not_has_subscription(w, customer_joined_by_panel_cost, bc)

    def _customer_add_by_app_payment(self, bc: BusinessmanCustomer, error_code: dict = None) -> Billing:
        w = self.check_has_minimum_credit(bc.businessman, error_code)
        return self._create_billing_if_not_has_subscription(w, customer_joined_by_app_cost, bc)

    def has_minimum_credit(self, user: Businessman) -> bool:
        w = self.get_businessman_wallet_or_create(user)
        return w.available_credit > wallet_minimum_allowed_credit

    def check_has_minimum_credit(self, user: Businessman, error_code: dict = None) -> Wallet:
        wallet = self.get_businessman_wallet_or_create(user)
        has_sub = self._has_subscription(wallet)
        if has_sub:
            return wallet
        has_min = wallet.available_credit > wallet_minimum_allowed_credit
        if has_min:
            return wallet
        if error_code is None:
            raise ApplicationErrorException(ApplicationErrorCodes.NOT_ENOUGH_WALLET_CREDIT)

        else:
            raise ApplicationErrorException(error_code)

    def _has_subscription(self, wallet: Wallet) -> bool:
        has = wallet.has_subscription
        if not has:
            return False

        if has and wallet.subscription_end <= timezone.now():
            wallet.has_subscription = False
            wallet.save()
            return False
        else:
            return True

    def _create_billing_if_not_has_subscription(self, wallet: Wallet, amount: int, bc: BusinessmanCustomer) -> Optional[
        Billing
    ]:
        has_sub = self._has_subscription(wallet)
        if has_sub:
            return None
        self._decrease_wallet_available_credit(wallet, amount)
        b = Billing.objects.create(amount=amount, customer_added=bc, businessman=bc.businessman)
        return b

    def get_billing_summery(self, user: Businessman, month: int = None, day: int = None) -> List[BillingSummery]:
        now = jdatetime.datetime.now()
        if month is not None:
            now = now.replace(month=month)
        if day is not None:
            now = now.replace(day=day)

        if month is not None and day is not None:
            return self.get_day_billings_group_by_day_and_customer_joined_by_type(user, now)

        elif month is not None and day is None:
            return self.get_month_billings(user, now)

        else:
            return self.get_present_year_billings(user)

    def get_month_billings(self, user: Businessman, date_of_month: jdatetime) -> List[
        BillingSummery]:
        start = date_of_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_day = get_end_day_of_jalali_month(date_of_month)
        end = date_of_month.replace(day=end_day, hour=23, minute=59, second=59)

        q = Billing.objects.filter(
            businessman=user,
            jcreate_date__gte=start,
            jcreate_date__lte=end
        ).annotate(
            joined_by=F('customer_added__joined_by'),
            amount_f=F('amount'),
            day=TruncDay('jcreate_date')
        ).values(
            'joined_by',
            'day'
        ).annotate(
            amount_sum=Sum('amount_f')
        ).order_by(
            'joined_by',
            'day'
        )

        mapped = map(lambda x: BillingSummery(x['day'].date(), x['joined_by'], x['amount_sum']), q)
        return list(mapped)

    def get_day_billings_group_by_day_and_customer_joined_by_type(self, user: Businessman,
                                                                  date_of_day: jdatetime.datetime) -> List[
        BillingSummery]:
        start = date_of_day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_of_day.replace(hour=23, minute=59, second=59)

        q = Billing.objects.filter(
            businessman=user,
            jcreate_date__gte=start,
            jcreate_date__lte=end
        ).values(
            'customer_added__joined_by'
        ).annotate(
            amount_sum=Sum('amount')
        ).order_by(
            'customer_added__joined_by'
        )

        q = list(q)
        mapped = map(lambda x: BillingSummery(None, x['customer_added__joined_by'], x['amount_sum']), q)
        return list(mapped)

    def get_present_year_billings(self, user: Businessman) -> List[BillingSummery]:
        result = []

        month_ranges = self._get_jalali_month_ranges()
        for start, end in month_ranges:
            q = Billing.objects.filter(
                businessman=user,
                jcreate_date__gte=start,
                jcreate_date__lte=end
            ).values(
                'customer_added__joined_by',
            ).annotate(
                amount_sum=Sum('amount')
            ).order_by(
                'customer_added__joined_by',
            )

            q = list(q)
            mapped = map(
                lambda x: BillingSummery(start.date(), x['customer_added__joined_by'], x['amount_sum']),
                q
            )
            result = result + list(mapped)
        return result

    def _get_jalali_month_ranges(self) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        now = jdatetime.datetime.now()
        result = []
        for i in range(12):
            start = now.replace(month=i + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_day = get_end_day_of_jalali_month(start)
            end = now.replace(month=i + 1, day=end_day, hour=23, minute=59, second=59, microsecond=0)
            result.append((start, end))

        return result

    def _decrease_wallet_available_credit(self, wallet: Wallet, amount: int) -> Wallet:
        wallet.available_credit -= amount
        wallet.used_credit = wallet.used_credit + amount
        wallet.save()
        return wallet


payment_service = PaymentService()
wallet_billing_service = WalletAndBillingService()
