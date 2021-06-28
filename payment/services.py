import calendar
import datetime
from typing import Tuple, List

import pytz
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import QuerySet
from django.db.models.aggregates import Sum
from django.urls import reverse
from django.utils import timezone
from rest_framework.request import Request
from zeep import Client

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
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
        increased_sms_panel_credit = False
        try:
            self._check_payment_verified_before(p)
            self.verify_payment(p)
            if p.is_payment_type_sms():
                sms_panel_info_service.get_panel_increase_credit_in_tomans(p.businessman, p.amount)
                increased_sms_panel_credit = True
            return p, sms_panel_info_service.get_buinessman_sms_panel(p.businessman)
        except Exception as ex:
            if increased_sms_panel_credit:
                sms_panel_info_service.get_panel_decrease_credit_in_tomans(p.businessman, p.amount)
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

    def __init__(self, query: QuerySet, added_by_panel_cost: int, added_by_app_cost: int, invitation_cost: int):
        self.query = query
        self.added_by_app_cost = added_by_app_cost
        self.added_by_panel_cost = added_by_panel_cost
        self.invitation_cost = invitation_cost


class MonthlyBillingSummery:
    def __init__(self, create_date, amount):
        self.create_date = create_date
        self.amount = amount


class DailyBillSummery:

    def __init__(self, create_date, joined_by: str, amount: int):
        self.create_date = create_date
        self.joined_by = joined_by
        self.amount = amount


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
        self._decrease_wallet_available_credit(w, invited_customer_after_purchase_cost)
        b = Billing.objects.create(amount=invited_customer_after_purchase_cost, customer_added=bc,
                                   businessman=bc.businessman)
        return b

    def _customer_add_by_panel_payment(self, bc: BusinessmanCustomer, error_code: dict = None) -> Billing:
        w = self.check_has_minimum_credit(bc.businessman, error_code)
        self._decrease_wallet_available_credit(w, customer_joined_by_panel_cost)
        b = Billing.objects.create(amount=customer_joined_by_panel_cost, customer_added=bc, businessman=bc.businessman)
        return b

    def _customer_add_by_app_payment(self, bc: BusinessmanCustomer, error_code: dict = None) -> Billing:
        w = self.check_has_minimum_credit(bc.businessman, error_code)
        self._decrease_wallet_available_credit(w, customer_joined_by_app_cost)
        b = Billing.objects.create(amount=customer_joined_by_app_cost, customer_added=bc, businessman=bc.businessman)
        return b

    def has_minimum_credit(self, user: Businessman) -> bool:
        w = self.get_businessman_wallet_or_create(user)
        return w.available_credit > wallet_minimum_allowed_credit

    def check_has_minimum_credit(self, user: Businessman, error_code: dict = None) -> Wallet:
        wallet = self.get_businessman_wallet_or_create(user)
        has_min = wallet.available_credit > wallet_minimum_allowed_credit
        if has_min:
            return wallet
        if error_code is None:
            raise ApplicationErrorException(ApplicationErrorCodes.NOT_ENOUGH_WALLET_CREDIT)
        else:
            raise ApplicationErrorException(error_code)

    def get_today_billings_until_now(self, user: Businessman) -> BillingSummery:
        tz = pytz.timezone('Asia/Tehran')
        local_now = datetime.datetime.now(tz)
        local_start_of_day = tz.normalize(local_now.replace(hour=0, minute=0, second=0, microsecond=0))
        query = Billing.objects.filter(businessman=user).filter(
            create_date__gte=local_start_of_day,
            create_date__lte=local_now
        )

        added_by_panel = self._aggregate_added_by_panel_amount(user, local_start_of_day, local_now)
        added_by_app = self._aggregate_added_by_app_amount(user, local_start_of_day, local_now)
        added_by_invitation = self._aggregate_added_by_invitation_amount(user, local_start_of_day, local_now)

        return BillingSummery(query, added_by_panel, added_by_app, added_by_invitation)

    def get_month_billings_group_by_day(self, user: Businessman, date_of_month: datetime.date) -> List[
        MonthlyBillingSummery]:
        q = self._group_by_billing_in_month(user, date_of_month.year, date_of_month.month)
        q = list(q)
        mapped = map(lambda x: MonthlyBillingSummery(x['create_date__date'], x['amount_sum']), q)
        return list(mapped)

    def get_day_billings_group_by_day_and_customer_joined_by_type(self, user: Businessman,
                                                                  date_of_date: datetime.date) -> List[
        DailyBillSummery]:
        tz = pytz.timezone('Asia/Tehran')
        local_now = datetime.datetime.now(tz)
        local_start_of_day = tz.normalize(
            local_now.replace(
                year=date_of_date.year,
                month=date_of_date.month,
                day=date_of_date.day,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
        )

        local_end_of_day = tz.normalize(
            local_now.replace(
                year=date_of_date.year,
                month=date_of_date.month,
                day=date_of_date.day,
                hour=23,
                minute=59,
                second=59
            )
        )
        q = Billing.objects.filter(businessman=user).filter(
            create_date__gte=local_start_of_day,
            create_date__lte=local_end_of_day
        ).values(
            'create_date__date', 'customer_added__joined_by'
        ).annotate(
            amount_sum=Sum('amount')
        ).order_by('create_date__date')

        q = list(q)
        mapped = map(
            lambda x: DailyBillSummery(x['create_date__date'], x['customer_added__joined_by'], x['amount_sum']),
            q
        )

        return list(mapped)

    def _group_by_billing_in_month(self, user: Businessman, year, month):
        tz = pytz.timezone('Asia/Tehran')
        local_now = datetime.datetime.now(tz)
        local_start_of_month = tz.normalize(
            local_now.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0))
        last_day = calendar.monthrange(year, month)[1]
        end_date = tz.normalize(
            local_now.replace(year=year, month=month, day=last_day, hour=23, minute=59,
                              second=59,
                              microsecond=0))

        q = Billing.objects.filter(
            businessman=user,
            create_date__gte=local_start_of_month,
            create_date__lte=end_date
        ).values(
            'create_date__date'
        ).annotate(
            amount_sum=Sum('amount')
        ).order_by('create_date__date')
        return q

    def get_month_billings_until_now(self, user: Businessman) -> BillingSummery:
        tz = pytz.timezone('Asia/Tehran')
        local_now = datetime.datetime.now(tz)
        local_start_of_month = tz.normalize(local_now.replace(day=1))
        query = Billing.objects.filter(
            businessman=user
        ).filter(
            create_date__gte=local_start_of_month,
            create_date__lte=local_now
        )

        added_by_panel = self._aggregate_added_by_panel_amount(user, local_start_of_month, local_now)
        added_by_app = self._aggregate_added_by_app_amount(user, local_start_of_month, local_now)
        added_by_invitation = self._aggregate_added_by_invitation_amount(user, local_start_of_month, local_now)

        return BillingSummery(query, added_by_panel, added_by_app, added_by_invitation)

    def _aggregate_added_by_panel_amount(self, user: Businessman, dt_from, dt_to):
        q = Billing.objects.filter(
            businessman=user
        ).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_PANEL
        )
        return self._aggregate_amount_from_to(q, dt_from, dt_to)

    def _aggregate_added_by_app_amount(self, user: Businessman, dt_from, dt_to):
        q = Billing.objects.filter(
            businessman=user
        ).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP
        )
        return self._aggregate_amount_from_to(q, dt_from, dt_to)

    def _aggregate_added_by_invitation_amount(self, user: Businessman, dt_from, dt_to):
        q = Billing.objects.filter(
            businessman=user
        ).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_INVITATION
        )

        return self._aggregate_amount_from_to(q, dt_from, dt_to)

    def _aggregate_amount_from_to(self, query: QuerySet, dt_from, dt_to) -> int:
        result = query.filter(
            create_date__gte=dt_from,
            create_date__lte=dt_to
        ).aggregate(
            Sum('amount')
        ).get('amount__sum', 0)
        if result is None:
            return 0
        return result

    def _decrease_wallet_available_credit(self, wallet: Wallet, amount: int) -> Wallet:
        wallet.available_credit -= amount
        wallet.used_credit = wallet.used_credit + amount
        wallet.save()
        return wallet


payment_service = PaymentService()
wallet_billing_service = WalletAndBillingService()
