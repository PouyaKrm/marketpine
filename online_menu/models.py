from django.core.files.storage import FileSystemStorage
from django.db import models
from users.models import BusinessmanOneToOneBaseModel, Businessman
# Create your models here.
from django.conf import settings
from common.util import generate_url_safe_base64_file_name

base_path = settings.ONLINE_MENU['BASE_PATH']
base_url = settings.ONLINE_MENU['BASE_URL']

file_storage = FileSystemStorage(location=base_path, base_url=base_url)


class OnlineMenu(BusinessmanOneToOneBaseModel):
    def get_upload_path(self, filename: str):
        return f'{self.businessman.id}/{generate_url_safe_base64_file_name(filename)}'
    file = models.ImageField(max_length=200, storage=file_storage, upload_to=get_upload_path)

    @staticmethod
    def delete_menu_for_user_if_exists(businessman: Businessman) -> bool:
        if not OnlineMenu.objects.filter(businessman=businessman).exists():
            return False
        OnlineMenu.objects.filter(businessman=businessman).delete()
        return True

