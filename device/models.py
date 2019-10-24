from django.db import models
from users.models import Businessman


class Device(models.Model):
    register_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    imei=models.IntegerField()
    businessman=models.OneToOneField(Businessman,on_delete=models.CASCADE)
