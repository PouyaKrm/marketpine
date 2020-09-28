from django.db.models import QuerySet

from online_menu.models import OnlineMenu
from users.models import Businessman

from django.conf import settings

max_allowed = settings.ONLINE_MENU['MAX_ALLOWED_IMAGES']

class OnlineMenuService:

    def add_image(self, businessman: Businessman, image) -> (bool, OnlineMenu):
        count = self.get_all_menus(businessman).count()
        if count == max_allowed:
            return False, None
        m = OnlineMenu.objects.create(businessman=businessman, image=image)
        return True, m


    def get_all_menus(self, businessman: Businessman) -> QuerySet:
        return OnlineMenu.objects.filter(businessman=businessman).all()