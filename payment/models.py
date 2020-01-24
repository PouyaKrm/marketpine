from django.db import models
from django.utils import timezone

from payment.exceptions import PaymentCreationFailedException, PaymentVerificationFailedException
from users.models import Businessman
from zeep import Client
from django.conf import settings
from django.urls import reverse


url = settings.ZARINPAL.get('url')
setting_merchant = settings.ZARINPAL.get('MERCHANT')

class PaymentTypes:
    SMS = '0'
    ACTIVATION = '1'

class Payment(models.Model):
<<<<<<< HEAD

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
=======
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    authority = models.CharField(max_length=255, null=True,blank=True)
    refid = models.CharField(max_length=255, null=True,blank=True)
    status = models.CharField(max_length=255,default="pending")
    description = models.CharField(max_length=255, null=True,blank=True)
    phone=models.IntegerField(null=True,blank=True)
>>>>>>> 966c21bb2f3eaaf1820cec3c460ff4545f6ac077
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
<<<<<<< HEAD
            self.save()
            raise PaymentCreationFailedException(self.create_status)
=======
            self.status = str(result.Status)
            self.save()
            # return HttpResponse('Error code: ' + str(result.Status))
            return redirect(settings.ZARINPAL.get("FORWARD_URL"))
>>>>>>> 966c21bb2f3eaaf1820cec3c460ff4545f6ac077

    def verify(self):
        merchant = setting_merchant
        client = Client(url)
        result = client.service.PaymentVerification(merchant, self.authority, self.amount)
        self.verification_status = result.Status
        self.save()
        if result.Status == 100:
            self.refid = str(result.RefID)
<<<<<<< HEAD
            self.verification_date = timezone.now()
            self.save()
        elif result.Status != 100 or result.Status != 101:
            raise PaymentVerificationFailedException(result.Status)
=======
            self.status = str(result.Status)
            self.save()
            # return HttpResponse('Transaction success.\nRefID: ' + str(result.RefID))
            return redirect(settings.ZARINPAL.get("FORWARD_URL"))

        elif result.Status == 101:
            self.status = str(result.Status)
            self.save()
            # return HttpResponse('Transaction submitted : ' + str(result.Status))
            return redirect(settings.ZARINPAL.get("FORWARD_URL"))

        else:
            self.status = str(result.Status)
            self.save()
            # return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
            return redirect(settings.ZARINPAL.get("FORWARD_URL"))
>>>>>>> 966c21bb2f3eaaf1820cec3c460ff4545f6ac077
