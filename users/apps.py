
from django.apps import AppConfig

from users import tasks


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        tasks.delete_expired_codes(repeat_until=None)
