from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_jalali.db import models as jmodels
from zeep import Client

from base_app.models import PanelDurationBaseModel
from panelprofile.services import sms_panel_info_service
from payment.exceptions import PaymentCreationFailedException, PaymentVerificationFailedException, \
    PaymentAlreadyVerifiedException, PaymentOperationFailedException
from users.models import Businessman, BaseModel, BusinessmanOneToOneBaseModel, BusinessmanManyToOneBaseModel, \
    BusinessmanCustomer

url = settings.ZARINPAL.get('url')
setting_merchant = settings.ZARINPAL.get('MERCHANT')


class SubscriptionPlan(BaseModel):
    DURATION_1_MONTH = '1_MONTH'
    DURATION_3_MONTH = '2_MONTH'
    DURATION_6_MONTH = '6_MONTH'
    DURATION_1_YEAR = '1_YEAR'

    duration_choices = [
        (DURATION_1_MONTH, '1 ماهه'),
        (DURATION_3_MONTH, '3 ماهه'),
        (DURATION_6_MONTH, '6 ماهه'),
        (DURATION_1_YEAR, '1 ساله')
    ]

    duration = models.CharField(max_length=20, choices=duration_choices)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price_in_toman = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def is_duration_1_month(self) -> bool:
        return self.duration == SubscriptionPlan.DURATION_1_MONTH

    def is_duration_3_month(self) -> bool:
        return self.duration == SubscriptionPlan.DURATION_3_MONTH

    def is_duration_6_month(self) -> bool:
        return self.duration == SubscriptionPlan.DURATION_6_MONTH

    def is_duration_1_year(self) -> bool:
        return self.duration == SubscriptionPlan.DURATION_1_YEAR

    def get_timedelta(self):
        if self.is_duration_1_month():
            return relativedelta(months=1)
        if self.is_duration_3_month():
            return relativedelta(months=3)
        if self.is_duration_6_month():
            return relativedelta(months=6)
        if self.is_duration_1_year():
            return relativedelta(years=1)

    def __str__(self):
        return self.title


class PaymentTypes:
    SMS = '0'
    ACTIVATION = '1'


class Payment(models.Model):
    TYPE_SMS = 'SMS'
    TYPE_WALLET_INCREASE = 'WALLET'
    TYPE_SUBSCRIPTION = 'SUB'

    payment_choices = [
        ('SMS', TYPE_SMS),
        ('WALLET', TYPE_WALLET_INCREASE),
        ('SUBSCRIPTION', TYPE_SUBSCRIPTION)
    ]

    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    authority = models.CharField(max_length=255, null=True, blank=True)
    refid = models.CharField(max_length=255, null=True, blank=True)
    create_status = models.IntegerField(null=True)
    call_back_status = models.CharField(max_length=10, null=True, blank=True)
    verification_status = models.IntegerField(null=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    amount = models.IntegerField()
    verification_date = models.DateTimeField(null=True)
    payment_type = models.CharField(max_length=40, choices=payment_choices, default='0')
    panel_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return "{}:{} T,creation_date:{}".format(self.businessman, self.amount, self.creation_date)

    def is_verified_before(self) -> bool:
        return self.refid is not None

    def pay(self, request):
        # url = reverse('payment:verify', kwargs={'to': callback} if callback else None)
        CallbackURL = request.build_absolute_uri(reverse('payment:verify'))
        client = Client(url)
        merchant = setting_merchant
        result = client.service.PaymentRequest(merchant, self.amount, self.description, self.businessman.email,
                                               self.phone, CallbackURL)
        self.create_status = result.Status
        if self.create_status == 100:
            self.authority = result.Authority
            self.save()
            # return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority)+'/ZarinGate')
        else:
            self.save()
            raise PaymentCreationFailedException(self.create_status)

    def __verify(self):

        """
        do not user this method directly beacesuse some operations must be exceucted before payment verification
        Use verify method instead
        :return:
        """

        if self.is_verified_before():
            raise PaymentAlreadyVerifiedException()

        merchant = setting_merchant
        client = Client(url)
        result = client.service.PaymentVerification(merchant, self.authority, self.amount)
        self.verification_status = result.Status
        self.save()
        if result.Status == 100:
            self.refid = str(result.RefID)
            self.verification_date = timezone.now()
            self.save()
        elif result.Status != 100:
            raise PaymentVerificationFailedException(result.Status)

    def verify(self):

        """
        executes some operations before verifying the payment
        :raises APIException if sms panel credit increase failed
        :raises PaymentVerificationFailedException if payment verification fails.
        :return:
        """

        if self.is_verified_before():
            raise PaymentAlreadyVerifiedException()

        try:
            self.do_operations()
        except Exception as e:
            FailedPaymentOperation.objects.create(businessman=self.businessman, payment=self,
                                                  payment_amount=self.amount, operation_type=self.payment_type)
            self.reverse_operations()

        try:
            self.__verify()
            sms_panel_info_service.set_wait_for_charge_to_pending()
        except Exception as e:
            self.reverse_operations()

    def reverse_operations(self):
        try:
            if self.payment_type == PaymentTypes.SMS:
                sms_panel_info_service.get_panel_decrease_credit_in_tomans(self.businessman.smspanelinfo, self.amount)
                self.save()
        except Exception as e:
            self.businessman.smspanelinfo.credit -= self.amount
            self.businessman.smspanelinfo.save()
            raise PaymentOperationFailedException(self.payment_type, e)
        if self.payment_type == PaymentTypes.ACTIVATION:
            self.businessman.panel_activation_date = timezone.now() - timezone.timedelta(days=1)
            self.businessman.panel_expiration_date = timezone.now()
            self.save()

    def do_operations(self):
        if self.payment_type == PaymentTypes.SMS:
            sms_panel_info_service.get_panel_increase_credit_in_tomans(self.businessman.smspanelinfo, self.amount)

        elif self.payment_type == PaymentTypes.ACTIVATION:
            self.__update_panel_activation_data()

    def __update_panel_activation_data(self):

        plan = self.panel_plan
        active_date = timezone.now()
        self.businessman.panel_activation_date = active_date
        self.businessman.duration_type = plan.duration_type

        if plan.is_duration_permanent():
            self.businessman.save()
            return

        if self.businessman.panel_expiration_date is not None:
            self.businessman.panel_expiration_date = self.businessman.panel_expiration_date + plan.duration
        else:
            self.businessman.panel_expiration_date = active_date + plan.duration

        self.businessman.save()
        self.businessman.smspanelinfo.activate()

    def is_payment_type_sms(self) -> bool:
        return self.payment_type == Payment.TYPE_SMS

    def is_payment_type_wallet(self) -> bool:
        return self.payment_type == Payment.TYPE_WALLET_INCREASE

    def is_payment_type_subscription(self) -> bool:
        return self.payment_type == Payment.TYPE_SUBSCRIPTION


class FailedPaymentOperation(models.Model):
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT)
    payment_amount = models.IntegerField()
    operation_type = models.CharField(max_length=2, choices=Payment.payment_choices, default='0')
    create_date = models.DateTimeField(auto_now_add=True)
    is_fixed = models.BooleanField(default=False)


class Wallet(BusinessmanOneToOneBaseModel):
    available_credit = models.BigIntegerField(default=0)
    used_credit = models.BigIntegerField(default=0)
    last_credit_increase_date = models.DateTimeField(null=True, blank=True)
    has_subscription = models.BooleanField(default=False)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "wallet"
        ordering = ('-create_date', '-update_date')


class Billing(BusinessmanManyToOneBaseModel):
    objects = jmodels.jManager()
    amount = models.BigIntegerField()
    customer_added = models.ForeignKey(BusinessmanCustomer, null=True, blank=True, on_delete=models.PROTECT)
    jcreate_date = jmodels.jDateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'billing'
        ordering = ('-create_date', '-update_date')
