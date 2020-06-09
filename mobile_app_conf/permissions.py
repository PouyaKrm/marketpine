from rest_framework import permissions

from django.conf import settings

from mobile_app_conf.models import MobileAppPageConf

max_allowed_headers = settings.MOBILE_APP_PAGE_CONF['MAX_ALLOWED_HEADERS']


class HasAllowedToUploadMoreHeaderImage(permissions.BasePermission):

    def has_permission(self, request, view) -> bool:
        if request.method == 'GET':
            return True
        return MobileAppPageConf.headers_uploaded_count(request.user) < max_allowed_headers
