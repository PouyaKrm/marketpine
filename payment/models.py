from django.db import models
from django.utils import timezone

from payment.exceptions import PaymentCreationFailedException, PaymentVerificationFailedException, \
    PaymentAlreadyVerifiedException, PaymentOperationFailedException
from users.models import Businessman
from zeep import Client
from django.conf import settings
from django.urls import reverse


url = settings.ZARINPAL.get('url')
setting_merchant = settings.ZARINPAL.get('MERCHANT')
activation_expire_delta = settings.ACTIVATION_EXPIRE_DELTA

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

    def __str__(self):
        return "{}:{} T,creation_date:{}".format(self.businessman,self.amount,self.creation_date)

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

        if self.refid is not None:
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

        self.__verify()

        try:
            if self.payment_type == PaymentTypes.SMS:
                self.businessman.smspanelinfo.increase_credit_in_tomans(self.amount)

            elif self.payment_type == PaymentTypes.ACTIVATION:
                active_date = timezone.now()
                self.businessman.panel_activation_date = active_date

                if self.businessman.panel_expiration_date is not None:
                    self.businessman.panel_expiration_date = self.businessman.panel_expiration_date + activation_expire_delta
                else:
                    self.businessman.panel_expiration_date = active_date + activation_expire_delta

                self.businessman.save()

        except Exception as e:
            FailedPaymentOperation.objects.create(businessman=self.businessman, payment=self,
                                                  payment_amount=self.amount, operation_type=self.payment_type)
            raise PaymentOperationFailedException(self.payment_type, e)


class FailedPaymentOperation(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT)
    payment_amount = models.IntegerField()
    operation_type = models.CharField(max_length=2, choices=Payment.payment_choices, default='0')
    create_date = models.DateTimeField(auto_now_add=True)
    is_fixed = models.BooleanField(default=False)
