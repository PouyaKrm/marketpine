from django.db import models
from django.conf import settings

# Create your models here.
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver

from base_app.models import PublicFileStorage
from common.util import generate_url_safe_base64_file_name
from users.models import BaseModel

sub_dir = settings.EDUCATIONS['SUB_DIR']
base_url = settings.EDUCATIONS['BASE_URL']

st = PublicFileStorage(subdir=sub_dir, base_url=base_url)


class EducationType(BaseModel):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Education(BaseModel):

    def get_upload_path(self, filename):
        return f'{self.id}/{generate_url_safe_base64_file_name(filename)}'

    video = models.FileField(storage=st, upload_to=get_upload_path)
    image = models.ImageField(storage=st, upload_to=get_upload_path)
    title = models.CharField(max_length=100)
    education_type = models.ForeignKey(EducationType, on_delete=models.PROTECT)

    def __str__(self):
        return self.title



_UNSAVED_IMAGE_FILEFIELD = 'unsaved_image_filefield'
_UNSAVED_VIDEO_FILEFIELD = 'unsaved_video_filefield'


@receiver(pre_save, sender=Education)
def skip_saving_file(sender, instance: Education, **kwargs):

    if instance.id:
        return

    if not hasattr(instance, _UNSAVED_IMAGE_FILEFIELD):
        setattr(instance, _UNSAVED_IMAGE_FILEFIELD, instance.image)
        instance.image = None

    if not hasattr(instance, _UNSAVED_VIDEO_FILEFIELD):
        setattr(instance, _UNSAVED_VIDEO_FILEFIELD, instance.video)
        instance.video = None


@receiver(post_save, sender=Education)
def save_file(sender, instance, created, **kwargs):

    if not created:
        return

    if hasattr(instance, _UNSAVED_IMAGE_FILEFIELD):
        instance.image = getattr(instance, _UNSAVED_IMAGE_FILEFIELD)
        instance.save()
        instance.__dict__.pop(_UNSAVED_IMAGE_FILEFIELD)

    if hasattr(instance, _UNSAVED_VIDEO_FILEFIELD):
        instance.video = getattr(instance, _UNSAVED_VIDEO_FILEFIELD)
        instance.save()
        instance.__dict__.pop(_UNSAVED_VIDEO_FILEFIELD)
