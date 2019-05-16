from django.db import models

# Create your models here.
from users.models import Businessman


class SMSTemplate(models.Model):

    title = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=200)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)


    def __str__(self):
        return self.title
