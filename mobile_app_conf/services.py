from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from mobile_app_conf.models import MobileAppPageConf, MobileAppHeader
from users.models import Businessman

max_allowed_headers = settings.MOBILE_APP_PAGE_CONF['MAX_ALLOWED_HEADERS']

class MobileAppPageConfService:

    def add_mobile_app_header(self, businessman: Businessman, image, show_order=None) -> MobileAppHeader:
        conf = self.get_businessman_conf_or_create(businessman)
        header = self.get_mobile_app_header_by_show_order_or_create(conf, show_order)
        header.header_image = image
        header.save()
        return header

    def get_businessman_conf_or_create(self, businessman: Businessman):
        try:
            return MobileAppPageConf.objects.get(businessman=businessman)
        except ObjectDoesNotExist:
            return MobileAppPageConf.objects.create(businessman=businessman)

    def headers_uploaded_count(self, businessman: Businessman) -> int:
        try:
            return MobileAppPageConf.objects.get(businessman=businessman).headers.count()
        except ObjectDoesNotExist:
            return 0

    def get_mobile_app_header_by_show_order_or_create(self, conf: MobileAppPageConf, show_order=None) -> MobileAppHeader:
        if show_order is None or not self.show_order_exists(conf, show_order):
            return MobileAppHeader.objects.create(mobile_app_page_conf=conf, show_order=show_order)
        return MobileAppHeader.objects.filter(show_order=show_order).first()

    def can_upload_new_header(self, businessman: Businessman, show_order=None) -> bool:
        count = self.get_businessman_all_app_headers(businessman).count()
        if count < max_allowed_headers:
            return True
        elif show_order is None:
            return False
        else:
            return self.show_order_exists(self.get_businessman_conf_or_create(businessman), show_order)

    def get_businessman_all_app_headers(self, businessman: Businessman):
        return self.get_businessman_conf_or_create(businessman=businessman).headers.all()

    def show_order_exists(self, conf: MobileAppPageConf, show_order: int) -> bool:
        return MobileAppHeader.objects.filter(mobile_app_page_conf=conf, show_order=show_order).exists()



mobile_page_conf_service = MobileAppPageConfService()
