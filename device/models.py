from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver

from common.util import url_safe_secret

from users.models import Businessman, BusinessmanOneToOneBaseModel


class Device(BusinessmanOneToOneBaseModel):
    imei = models.CharField(max_length=25, null=True, unique=True)
    key = models.TextField(null=True, unique=True)
    disabled = models.BooleanField(default=True)


@receiver(post_save, sender=Device)
def generate_key_after_save(sender, instance: Device, created: bool, **kwargs):

    if created:
        instance.key = url_safe_secret()
        instance.save()
