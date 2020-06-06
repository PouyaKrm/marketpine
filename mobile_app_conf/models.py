from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings

from users.models import BusinessmanOneToOneBaseModel, BaseModel, Businessman
from users.util import businessman_related_model_file_upload_path

mobile_app_base_path = settings.MOBILE_APP_PAGE_CONF['BASE_PATH']
mobile_app_base_url = settings.MOBILE_APP_PAGE_CONF['BASE_URL']

storage = FileSystemStorage(location=mobile_app_base_path, base_url=mobile_app_base_url)


class MobileAppPageConf(BusinessmanOneToOneBaseModel):

    store_location = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.businessman.username

    @staticmethod
    def add_mobile_app_header(businessman: Businessman, image):
        try:
            conf = MobileAppPageConf.objects.get(businessman=businessman)
        except ObjectDoesNotExist:
            conf = MobileAppPageConf.objects.create(businessman=businessman)
        return MobileAppHeader.create_mobile_app_header(conf, image)

    @staticmethod
    def headers_uploaded_count(businessman: Businessman) -> int:
        try:
            return MobileAppPageConf.objects.get(businessman=businessman).headers.count()
        except ObjectDoesNotExist:
            return 0


def mobile_app_header_upload_path(instance, filename):
    return businessman_related_model_file_upload_path(instance.mobile_app_page_conf, filename)


class MobileAppHeader(BaseModel):

    mobile_app_page_conf = models.ForeignKey(MobileAppPageConf, related_query_name='headers', related_name='headers',
                                             on_delete=models.CASCADE)
    header_image = models.ImageField(storage=storage, upload_to=mobile_app_header_upload_path)

    def __str__(self):
        return self.mobile_app_page_conf.businessman.username

    @staticmethod
    def create_mobile_app_header(mobile_app_conf: MobileAppPageConf, image):
        return MobileAppHeader.objects.create(mobile_app_page_conf=mobile_app_conf, header_image=image)