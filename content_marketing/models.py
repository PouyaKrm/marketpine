import uuid, base64

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.dispatch import receiver

from common.util import get_file_extension
from common.util.kavenegar_local import APIException, HTTPException
from users.models import Businessman,Customer

from common.util.sms_panel.message import SystemSMSMessage

content_upload_path = settings.CONTENT_MARKETING['BASE_PATH']
video_confirm_message = settings.CONTENT_MARKETING['VIDEO_CONFIRM_MESSAGE']
video_reject_message = settings.CONTENT_MARKETING['VIDEO_REJECT_MESSAGE']
video_base_url = settings.CONTENT_MARKETING['BASE_URL']

video_storage = FileSystemStorage(location=content_upload_path, base_url=video_base_url)


class PostConfirmationStatus:
    REJECTED = '0'
    ACCEPTED = '1'
    PENDING = '2'


class Post(models.Model):

    confirmation_choices = (
        (PostConfirmationStatus.REJECTED, "Rejected"),
        (PostConfirmationStatus.ACCEPTED, "Accepted"),
        (PostConfirmationStatus.PENDING, "Pending")
    )

    def get_upload_path(self, filename):
        now = timezone.now()
        extension = get_file_extension(filename)

        return f"{self.businessman.id}/{now.strftime('%Y')}/{now.strftime('%m')}/" \
            f"{ str(base64.urlsafe_b64encode(str(uuid.uuid4()).encode('utf8')), 'utf8')}{extension}"

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    videofile = models.FileField(storage=video_storage, upload_to=get_upload_path, null=False, blank=False, max_length=254)
    mobile_thumbnail = models.ImageField(storage=video_storage, upload_to=get_upload_path, null=True, max_length=254)
    video_url = models.URLField(null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    confirmation_status = models.CharField(max_length=1, choices=confirmation_choices, default=PostConfirmationStatus.PENDING)
    customer_notif_message_template = models.CharField(max_length=260, null=True)
    send_notif_sms = models.BooleanField(default=False)
    send_notif_pwa = models.BooleanField(default=False)

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

        if obj.confirmation_status != instance.confirmation_status:
            if instance.confirmation_status is PostConfirmationStatus.ACCEPTED:
                messenger.send_message(instance.businessman.phone, video_confirm_message)
            elif instance.confirmation_status is PostConfirmationStatus.REJECTED:
                messenger.send_message(instance.businessman.phone, video_reject_message)

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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'post',)
        ordering = ['creation_date']

    def __str__(self):
        return 'like by {}'.format(self.customer)


class ContentMarketingSettings(models.Model):

    businessman = models.OneToOneField(Businessman, on_delete=models.PROTECT, related_name="content_marketing_settings")
    message_template = models.CharField(max_length=260, default="")
    send_video_upload_message = models.BooleanField(default=False)


