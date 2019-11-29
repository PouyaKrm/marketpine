from django.db import models
from users.models import Businessman
from django.http import HttpResponse
from django.shortcuts import redirect
from zeep import Client
from django.conf import settings
from django.urls import reverse


class Payment(models.Model):
    PAYMENT_STATUS= [
        ("PAID", 'paid'),
        ("PENDING", 'pending'),
        ("UNPAID", 'unpaid'),
    ]
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    authority = models.CharField(max_length=255, null=True,blank=True)
    refid = models.CharField(max_length=255, null=True,blank=True)
    status = models.CharField(max_length=7,
                              choices=PAYMENT_STATUS,
                              default="PENDING",)
    description = models.CharField(max_length=255, null=True,blank=True)
    phone=models.IntegerField(null=True,blank=True)
    amount = models.IntegerField()


    def __str__(self):
        return "{}:{} T,creation_date:{}".format(self.businessman,self.amount,self.creation_date)


    def pay(self, request):
        # url = reverse('payment:verify', kwargs={'to': callback} if callback else None)
        CallbackURL =  request.build_absolute_uri(reverse('payment:verify'))
        client=Client(settings.ZARINPAL.get('url'))
        merchant=settings.ZARINPAL.get("MERCHANT")
        result = client.service.PaymentRequest(merchant, self.amount, self.description, self.businessman.email, self.phone, CallbackURL)
        if result.Status == 100:
            self.authority = result.Authority
            self.save()
            return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority)+'/ZarinGate')
        else:
            ##TODO
            self.status = result.Status
            self.save()
            return HttpResponse('Error code: ' + str(result.Status))

    def verify(self, request):
        merchant=settings.ZARINPAL.get("MERCHANT")
        client=Client(settings.ZARINPAL.get('url'))
        result = client.service.PaymentVerification(merchant, self.authority, self.amount)
        if result.Status == 100:
            self.refid = str(result.RefID)
            self.status = "done"
            self.save()
            return HttpResponse('Transaction success.\nRefID: ' + str(result.RefID))
        elif result.Status == 101:
            self.status = str(result.Status)
            self.save()
            return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            self.status = str(result.Status)
            self.save()
            return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
