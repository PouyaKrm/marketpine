from django.db import models

# Create your models here.
from users.models import BaseModel, Customer


class CustomerOneTimePasswords(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_query_name='one_time_passwords',
                                 related_name='one_time_passwords')
    expiration_time = models.DateTimeField()
    code = models.CharField(max_length=20)
    send_attempts = models.IntegerField(default=1)


class CustomerLoginTokens(BaseModel):
    token = models.TextField()
    user_agent = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_query_name='login_tokens',
                                 related_name='login_tokens')

