from django.db import models

# Create your models here.
from users.models import Businessman


class PanelSetting(models.Model):

    welcome_message = models.CharField(max_length=200)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)

    class Meta:
        db_table = 'panel_setting'
