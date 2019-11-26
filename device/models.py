from django.db import models
from users.models import Businessman


class Device(models.Model):
    register_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    imei = models.CharField(max_length=25)
    businessman=models.OneToOneField(Businessman,on_delete=models.CASCADE)
