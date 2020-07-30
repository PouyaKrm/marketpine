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
        header.header_image_size = image.size
        header.save()
        return header

    def header_id_exists_by_user(self, user: Businessman, header_id: int) -> bool:
        conf = self.get_businessman_conf_or_create(user)
        return MobileAppHeader.objects.filter(mobile_app_page_conf=conf, id=header_id).exists()

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

    def get_mobile_app_header_by_show_order_or_create(self, conf: MobileAppPageConf,
                                                      show_order=None) -> MobileAppHeader:
        if show_order is None or not self.show_order_exists(conf, show_order):
            return MobileAppHeader.objects.create(mobile_app_page_conf=conf, show_order=show_order)
        return MobileAppHeader.objects.order_by('create_date').filter(show_order=show_order).first()

    def can_upload_new_header(self, businessman: Businessman, show_order=None) -> bool:
        count = self.get_businessman_all_app_headers(businessman).count()
        if count < max_allowed_headers:
            return True
        elif show_order is None:
            return False
        else:
            return self.show_order_exists(self.get_businessman_conf_or_create(businessman), show_order)

    def get_businessman_all_app_headers(self, businessman: Businessman):
        return self.get_businessman_conf_or_create(businessman=businessman).headers.order_by('show_order',
                                                                                             'create_date').all()

    def show_order_exists(self, conf: MobileAppPageConf, show_order: int) -> bool:
        return MobileAppHeader.objects.filter(mobile_app_page_conf=conf, show_order=show_order).exists()

    def are_show_orders_unique_for_update(self, user: Businessman, header_id_show_order: dict) -> bool:
        ids = [k for k, _ in header_id_show_order.items()]
        show_orders = [v for _, v in header_id_show_order.items()]
        return not self.get_businessman_all_app_headers(user).exclude(id__in=ids) \
            .filter(show_order__in=show_orders).exists()

    def update_show_orders_of_headers(self, user: Businessman, header_id_show_order: dict):
        for k, v in header_id_show_order.items():
            h = self.get_businessman_all_app_headers(user).get(id=k)
            h.show_order = v
            h.save()


mobile_page_conf_service = MobileAppPageConfService()
