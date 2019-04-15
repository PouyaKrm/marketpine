from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Salesman(AbstractUser):

    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=500, blank=True, null=True)
    business_name = models.CharField(max_length=1000)
    bot_access = models.BooleanField(default=False)
    bot_access_expire = models.DateTimeField(blank=True, null=True)
    instagram_access = models.BooleanField(default=False)
    instagram_access_expire = models.DateTimeField(blank=True, null=True)

    
    def __str__(self):
        return self.username

