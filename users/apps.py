
from django.apps import AppConfig
from django.contrib.auth import models

from common.util.sms_panel.client import ClientManagement


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        def un_authorize_user(self):
            if self.authorized != '2':
                return
            client = ClientManagement()
            client.deactivate_sms_panel(self.smspanelinfo.api_key)
            self.authorized = '0'
            self.save()

        models.User.add_to_class('un_authorize_user', un_authorize_user)



