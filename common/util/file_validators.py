from django.conf import settings
from django.core.exceptions import ValidationError
import os

def validate_upload_video_size (file):
    if file.size > int(settings.CONTENT_MARKETING.get("MAX_SIZE_VIDEO")):
        # raise ValidationError('اندازه لگو بیش از حد مجاز است(200kb)')
        raise ValidationError(
        '({MAX_SIZE_VIDEO} byte.اندازه ویدیو بیشتر از حد مجاز است.(حداکثر مجاز می باشد'.format(
        max_size_video =settings.CONTENT_MARKETING.get("MAX_SIZE_VIDEO")
        ))
    else:
        return file


def validate_video_file_extension(file):
    ext = os.path.splitext(file.name)[1]
    valid_extensions = settings.CONTENT_MARKETING.get("ALLOWED_TYPES_VIDEO")
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')
    else:
        return file
