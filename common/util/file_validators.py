from django.conf import settings
from django.core.exceptions import ValidationError


def validate_upload_video (file):
    if file.size > int(settings.UPLOAD_VIDEO.get("max_size_video")):
        # raise ValidationError('اندازه لگو بیش از حد مجاز است(200kb)')
        raise ValidationError('({max_size_video} byte.اندازه ویدیو بیشتر از حد مجاز است.(حداکثر مجاز می باشد'.format(
        max_size_video =settings.UPLOAD_VIDEO.get("max_size_video")
        ))
    # return file
