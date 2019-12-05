from django.db import models

# Create your models here.
from users.models import Businessman, Customer
from django.conf import settings





class SMSTemplate(models.Model):

    title = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=200)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)


    def __str__(self):
        return self.title


class SentSMS(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    message_id = models.IntegerField()
    is_sent_to_all = models.BooleanField(default=False)
