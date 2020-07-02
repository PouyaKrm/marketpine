from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings

from users.models import BusinessmanOneToOneBaseModel, BaseModel, Businessman
from users.util import businessman_related_model_file_upload_path
from base_app.models import PublicFileStorage

sub_dir = settings.MOBILE_APP_PAGE_CONF['SUB_DIR']
mobile_app_base_url = settings.MOBILE_APP_PAGE_CONF['BASE_URL']

storage = PublicFileStorage(subdir=sub_dir, base_url=mobile_app_base_url)


class MobileAppPageConf(BusinessmanOneToOneBaseModel):

    market_location = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.businessman.username


def mobile_app_header_upload_path(instance, filename):
    return businessman_related_model_file_upload_path(instance.mobile_app_page_conf, filename)


class MobileAppHeader(BaseModel):

    mobile_app_page_conf = models.ForeignKey(MobileAppPageConf, related_query_name='headers', related_name='headers',
                                             on_delete=models.CASCADE)
    show_order = models.IntegerField(null=True)
    header_image = models.ImageField(storage=storage, upload_to=mobile_app_header_upload_path)

    def __str__(self):
        return self.mobile_app_page_conf.businessman.username

