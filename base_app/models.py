from django.db import models
from django.utils.deconstruct import deconstructible
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
# Create your models here.

public_path = settings.PUBLIC_FILE_BASE_PATH
private_path = settings.PRIVATE_FILE_BASE_PATH


@deconstructible
class PublicFileStorage(FileSystemStorage):

    def __init__(self, subdir, base_url):
        self.subdir = subdir
        super(PublicFileStorage, self).__init__(location=os.path.join(public_path, self.subdir), base_url=base_url)

    def __eq__(self, other):
        return self.subdir == other.subdir


@deconstructible
class PrivateFileStorage(FileSystemStorage):

   def __init__(self, subdir, base_url):
        self.subdir = subdir
        super(PrivateFileStorage, self).__init__(location=os.path.join(private_path, self.subdir), base_url=base_url)

   def __eq__(self, other):
        return self.subdir == other.subdir


class PanelDurationBaseModel(models.Model):
    DURATION_MONTHLY = 'M'
    DURATION_YEARLY = 'Y'
    DURATION_PERMANENT = 'PER'

    duration_choices = [
        (DURATION_MONTHLY, 'MONTHLY'),
        (DURATION_YEARLY, 'YEARLY'),
        (DURATION_PERMANENT, 'PERMANENT')
    ]

    duration_type = models.CharField(max_length=2, choices=duration_choices, default=DURATION_MONTHLY)

    class Meta:
        abstract = True

    def is_duration_monthly(self) -> bool:
        return self.duration_type == PanelDurationBaseModel.DURATION_MONTHLY

    def is_duration_yearly(self) -> bool:
        return self.duration_type == PanelDurationBaseModel.DURATION_YEARLY

    def is_duration_permanent(self) -> bool:
        return self.duration_type == PanelDurationBaseModel.DURATION_PERMANENT
