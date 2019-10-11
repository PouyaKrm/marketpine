from django.http import HttpResponse
from django.shortcuts import redirect
from zeep import Client
from django.utils.translation import ugettext as _
from .models import Payment


def verify(request):

    if request.GET.get('Status') == 'OK':
        p = Payment.objects.get(authority=request.GET['Authority'])
        return p.verify(request)
    else:
        return HttpResponse(_('Transaction failed or canceled by user'))


def pay(request):
    p=Payment(amount=1000,user=request.user,description="for test")
    p.save()
    return p.pay(request)
