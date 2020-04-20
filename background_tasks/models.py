from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

from users.models import BaseModel


class BackgroundTask(BaseModel):

    STATUS_RUNNING = '0'
    STATUS_KILL = '1'

    status_choices = [
        (STATUS_RUNNING, 'RUNNING'),
        (STATUS_KILL, 'KILL')
    ]

    local_id = models.PositiveIntegerField()
    pid = models.PositiveIntegerField()
    name = models.CharField(max_length=40)
    status = models.CharField(max_length=2, choices=status_choices, default=STATUS_KILL)


# @receiver(pre_save, sender=BackgroundTask)
# def kill_start_task(sender, instance: BackgroundTask, *args, **kwargs):
#     from .services import background_task_service
#     try:
#         b = BackgroundTask.objects.get(id=instance.id)
#     except ObjectDoesNotExist:
#         return
#     if b.status == instance.status:
#         return
#
#     if instance.status == BackgroundTask.STATUS_RUNNING:
#         background_task_service.start_process_by_local_id(b.local_id)
#     elif instance.status == BackgroundTask.STATUS_KILL:
#         background_task_service.kill_process_by_local_id(b.local_id)
#
