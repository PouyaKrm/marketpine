from django.db import models

# Create your models here.
from users.models import Businessman, BusinessmanOneToOneBaseModel


class PanelSetting(BusinessmanOneToOneBaseModel):

    welcome_message = models.CharField(null=True, max_length=200)
    send_welcome_message = models.BooleanField(default=False)

    class Meta:
        db_table = 'panel_setting'

    @staticmethod
    def try_create_panel_setting_for_businessman(businessman: Businessman):
        if PanelSetting.objects.filter(businessman=businessman).exists():
            return False
        s = PanelSetting(businessman=businessman, welcome_message='به {} خوش آمدید'.format(businessman.business_name))
        s.save()
        return True
