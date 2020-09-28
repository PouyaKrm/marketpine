from base_app.models import PublicFileStorage
from django.db import models
from users.models import BusinessmanOneToOneBaseModel, Businessman, BusinessmanManyToOneBaseModel
# Create your models here.
from django.conf import settings
from common.util import generate_url_safe_base64_file_name

sub_dir = settings.ONLINE_MENU['SUB_DIR']
base_url = settings.ONLINE_MENU['BASE_URL']

file_storage = PublicFileStorage(sub_dir, base_url=base_url)


class OnlineMenu(BusinessmanManyToOneBaseModel):
    def get_upload_path(self, filename: str):
        return f'{self.businessman.id}/{generate_url_safe_base64_file_name(filename)}'
    image = models.ImageField(max_length=200, storage=file_storage, upload_to=get_upload_path)
    show_order = models.PositiveIntegerField(null=True)

    @staticmethod
    def delete_menu_for_user_if_exists(businessman: Businessman) -> bool:
        if not OnlineMenu.objects.filter(businessman=businessman).exists():
            return False
        OnlineMenu.objects.filter(businessman=businessman).delete()
        return True

