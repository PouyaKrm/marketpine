from django.db import models
from django.conf import settings

# Create your models here.
from base_app.models import PublicFileStorage
from common.util import generate_url_safe_base64_file_name
from users.models import BaseModel

sub_dir = settings.EDUCATIONS['SUB_DIR']
base_url = settings.EDUCATIONS['BASE_URL']

st = PublicFileStorage(subdir=sub_dir, base_url=base_url)


class EducationType(BaseModel):

    name = models.CharField(max_length=100)


class Education(BaseModel):

    def get_path(self, filename):
        return '{}/{}'.format(self.id, generate_url_safe_base64_file_name(filename))

    video = models.FileField(storage=st, upload_to=get_path)
    image = models.ImageField(storage=st, upload_to=get_path)
    title = models.CharField(max_length=100)
    education_type = models.ForeignKey(EducationType, on_delete=models.PROTECT)

