from rest_framework import permissions
from rest_framework.request import Request

from panelsetting.models import PanelSetting


class CreatePanelSettingIfDoesNotExist(permissions.BasePermission):

    def has_permission(self, request: Request, view):

        if not PanelSetting.objects.filter(businessman=request.user).exists():

            PanelSetting.objects.create(businessman=request.user)

        return True
