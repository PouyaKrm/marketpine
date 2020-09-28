from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from online_menu.models import OnlineMenu
from users.models import Businessman

from django.conf import settings

max_allowed = settings.ONLINE_MENU['MAX_ALLOWED_IMAGES']


class OnlineMenuService:

    def add_image(self, businessman: Businessman, image, show_order: int, new_show_orders: dict) -> (bool, OnlineMenu):
        count = self.get_all_menus(businessman).count()
        if count == max_allowed:
            return False, None
        self.update_show_orders(businessman, new_show_orders)
        self.delete_menu_by_show_order(show_order)
        m = OnlineMenu.objects.create(businessman=businessman, image=image, show_order=show_order)
        return True, m

    def get_all_menus(self, businessman: Businessman) -> QuerySet:
        return OnlineMenu.objects.filter(businessman=businessman).all()

    def get_menu_by_id(self, businessman: Businessman, menu_id: int) -> OnlineMenu:
        try:
            return OnlineMenu.objects.filter(businessman=businessman).get(id=menu_id)
        except ObjectDoesNotExist:
            return None

    def are_new_show_orders_unique(self, show_order: int, new_show_orders: dict) -> bool:
        return not OnlineMenu.objects.filter(show_order__in=new_show_orders.values()).exclude(
            id__in=new_show_orders.keys()).exclude(show_order=show_order).exists()

    def delete_menu_by_show_order(self, show_order: int) -> OnlineMenu:
        try:
            o = OnlineMenu.objects.get(show_order=show_order)
            o.delete()
            return o
        except ObjectDoesNotExist:
            return None

    def delete_menu_by_id(self, user: Businessman, menu_id: int) -> OnlineMenu:
        try:
            m = OnlineMenu.objects.filter(businessman=user).get(id=menu_id)
            m.delete()
            return m
        except ObjectDoesNotExist:
            return None

    def update_show_orders(self, user: Businessman, new_show_orders: dict):
        for k, v in new_show_orders.items():
            try:
                m = OnlineMenu.objects.filter(businessman=user).get(id=k)
                m.show_order = v
                m.save()
            except ObjectDoesNotExist:
                pass


online_menu_service = OnlineMenuService()

