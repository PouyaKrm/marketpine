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
