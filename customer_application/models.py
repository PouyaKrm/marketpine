from django.db import models

# Create your models here.
from django.utils import timezone

from users.models import BaseModel, Customer


class CustomerVerificationCode(BaseModel):
    USED_FOR_LOGIN = '0'
    USED_FOR_PHONE_UPDATE = '1'
    used_for_choices = [
        (USED_FOR_LOGIN, 'Used for Login'),
        (USED_FOR_PHONE_UPDATE, 'Used for phone update')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_query_name='one_time_passwords',
                                 related_name='one_time_passwords')
    expiration_time = models.DateTimeField()
    code = models.CharField(max_length=20)
    send_attempts = models.IntegerField(default=1)
    last_send_time = models.DateTimeField(default=timezone.now)
    used_for = models.CharField(max_length=2, choices=used_for_choices, default=USED_FOR_LOGIN)


class CustomerLoginTokens(BaseModel):
    token = models.TextField(unique=True)
    user_agent = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_query_name='login_tokens',
                                 related_name='login_tokens')


class CustomerUpdatePhoneModel(BaseModel):
    verify_code = models.OneToOneField(CustomerVerificationCode, on_delete=models.CASCADE)
    new_phone = models.CharField(max_length=20)
