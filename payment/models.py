from django.db import models
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from payment.exceptions import PaymentCreationFailedException, PaymentVerificationFailedException, \
    PaymentAlreadyVerifiedException, PaymentOperationFailedException
from users.models import Businessman, BaseModel
from zeep import Client
from django.conf import settings
from django.urls import reverse

from panelprofile.services import sms_panel_info_service


url = settings.ZARINPAL.get('url')
setting_merchant = settings.ZARINPAL.get('MERCHANT')
activation_expire_delta = settings.ACTIVATION_EXPIRE_DELTA


class PanelActivationPlans(BaseModel):

    DURATION_MONTHLY = 'M'
    DURATION_YEARLY = 'Y'
    DURATION_PERMANENT = 'PER'

    duration_choices = [
        (DURATION_MONTHLY, 'MONTHLY'),
        (DURATION_YEARLY, 'YEARLY'),
        (DURATION_PERMANENT, 'PERMANENT')
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price_in_toman = models.PositiveIntegerField()
    duration_type = models.CharField(max_length=2, choices=duration_choices, default=DURATION_MONTHLY)
    duration = models.DurationField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def is_duration_monthly(self) -> bool:
        return self.duration_type == PanelActivationPlans.DURATION_MONTHLY

    def is_duration_yearly(self) -> bool:
        return self.duration_type == PanelActivationPlans.DURATION_YEARLY

    def is_duration_permanent(self) -> bool:
        return self.duration_type == PanelActivationPlans.DURATION_PERMANENT

    def set_duration_by_duration_type(self):
        if self.is_duration_monthly():
            self.duration = timezone.timedelta(days=30)

        elif self.is_duration_yearly():
            self.duration = timezone.timedelta(days=365)

    def __str__(self):
        return self.title


@receiver(pre_save, sender=PanelActivationPlans)
def set_duration(sender, instance: PanelActivationPlans, *args, **kwargs):
    instance.set_duration_by_duration_type()


class PaymentTypes:
    SMS = '0'
    ACTIVATION = '1'

class Payment(models.Model):


    payment_choices = [
        ('SMS', '0'),
        ('ACTIVATION', '1')
    ]

    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    authority = models.CharField(max_length=255, null=True, blank=True)
    refid = models.CharField(max_length=255, null=True, blank=True)
    create_status = models.IntegerField(null=True)
    verification_status = models.IntegerField(null=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    amount = models.IntegerField()
    verification_date = models.DateTimeField(null=True)
    payment_type = models.CharField(max_length=2, choices=payment_choices, default='0')
    panel_plan = models.ForeignKey(PanelActivationPlans, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return "{}:{} T,creation_date:{}".format(self.businessman,self.amount,self.creation_date)

    def is_verified_before(self) -> bool:
        return self.refid is not None

    def pay(self, request):
        # url = reverse('payment:verify', kwargs={'to': callback} if callback else None)
        CallbackURL = request.build_absolute_uri(reverse('payment:verify'))
        client = Client(url)
        merchant = setting_merchant
        result = client.service.PaymentRequest(merchant, self.amount, self.description, self.businessman.email, self.phone, CallbackURL)
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
                sms_panel_info_service.decrease_credit_in_tomans(self.businessman.smspanelinfo, self.amount)
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
            sms_panel_info_service.increase_credit_in_tomans(self.businessman.smspanelinfo, self.amount)
            # self.businessman.smspanelinfo.increase_credit_in_tomans(self.amount)

        elif self.payment_type == PaymentTypes.ACTIVATION:
            active_date = timezone.now()
            self.businessman.panel_activation_date = active_date

            if self.businessman.panel_expiration_date is not None:
                self.businessman.panel_expiration_date = self.businessman.panel_expiration_date + activation_expire_delta
            else:
                self.businessman.panel_expiration_date = active_date + activation_expire_delta

            self.businessman.save()


class FailedPaymentOperation(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT)
    payment_amount = models.IntegerField()
    operation_type = models.CharField(max_length=2, choices=Payment.payment_choices, default='0')
    create_date = models.DateTimeField(auto_now_add=True)
    is_fixed = models.BooleanField(default=False)

