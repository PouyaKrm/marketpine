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
    address = models.TextField(null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    is_location_set = models.BooleanField(default=False)
    page_id = models.CharField(max_length=40, unique=True, blank=True, null=True)
    instagram_page_url = models.URLField(max_length=100, blank=True, null=True)
    working_time_from = models.TimeField(null=True, blank=True)
    working_time_to = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.businessman.username

    def is_address_set(self) -> bool:
        return self.address is not None and len(self.address.strip()) != 0



def mobile_app_header_upload_path(instance, filename):
    return businessman_related_model_file_upload_path(instance.mobile_app_page_conf, filename)


class MobileAppHeader(BaseModel):

    mobile_app_page_conf = models.ForeignKey(MobileAppPageConf, related_query_name='headers', related_name='headers',
                                             on_delete=models.CASCADE)
    show_order = models.IntegerField(null=True)
    header_image = models.ImageField(storage=storage, upload_to=mobile_app_header_upload_path)
    header_image_size = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.mobile_app_page_conf.businessman.username


class ContactInfo(BaseModel):

    mobile_app_page_conf = models.ForeignKey(MobileAppPageConf,
                                             related_name='contact_info',
                                             related_query_name='contact_info',
                                             on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

