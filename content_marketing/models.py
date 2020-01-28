from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.dispatch import receiver

from common.util.kavenegar_local import APIException, HTTPException
from users.models import Businessman,Customer

from common.util.sms_panel.message import SystemSMSMessage

upload_path = settings.UPLOAD_VIDEO['BASE_PATH']
video_confirm_message = settings.UPLOAD_VIDEO['VIDEO_CONFIRM_MESSAGE']
video_reject_message = settings.UPLOAD_VIDEO['VIDEO_REJECT_MESSAGE']
video_base_url = settings.UPLOAD_VIDEO['BASE_URL']

video_storage = FileSystemStorage(location=upload_path, base_url=video_base_url)


class Post(models.Model):

    def get_upload_path(self, filename):
        now = timezone.now()
        return f"{self.businessman.id}/{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}/{filename}"

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    videofile = models.FileField(storage=video_storage, upload_to=get_upload_path, null=False, blank=False, max_length=254)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    is_confirmed = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=False)

    def __str__(self):
        return "id:{}, title:{} , businessman:{}".format(self.id, self.title, self.businessman)
    #
    # def is_active(self):
    #     self.is_active = True
    #     self.save()


@receiver(pre_save, sender=Post)
def send_message_video_is_confirmed(sender, instance: Post, *args, **kwargs):

    """
    Sends a text message if confirmation of post model is changed.
    If exception in message sends happen model will be saved and message won't be sent
    :param sender: Post class
    :param instance: the changed model that is being saved
    :param args:
    :param kwargs:
    :return: None
    """
    messenger = SystemSMSMessage()
    try:
        obj = Post.objects.get(id=instance.id)
        if obj.is_confirmed != instance.is_confirmed and instance.is_confirmed:
            messenger.send_message(instance.businessman.phone, video_confirm_message.format(title=instance.title))
        elif obj.is_confirmed != instance.is_confirmed and not instance.is_confirmed:
            messenger.send_message(instance.businessman.phone, video_reject_message.format(title=instance.title))
    except ObjectDoesNotExist:
        return
    except (APIException, HTTPException):
        return

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name='comments')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    body = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creation_date']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.customer)


class Like(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name='likes')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'post',)
        ordering = ['creation_date']

    def __str__(self):
        return 'like by {}'.format(self.customer)
