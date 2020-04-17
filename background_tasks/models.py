from django.db import models

# Create your models here.
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
