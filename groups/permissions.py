from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from django.conf import settings

from groups.models import BusinessmanGroups

max_allowed_defined_groups = settings.SMS_PANEL['MAX_ALLOWED_DEFINED_GROUPS']


class HasValidDefinedGroups(permissions.BasePermission):

    """
    Checks max allowed defined customer groups is not reached.
    """

    message = f"حداکثر تعداد مجاز گروه های تعریف شده {max_allowed_defined_groups} است، که شما به آن رسیده اید"

    def has_permission(self, request: Request, view: View):

        return BusinessmanGroups.get_all_businessman_normal_groups(request.user).count() < max_allowed_defined_groups


class CanDeleteGroup(permissions.BasePermission):

    message = 'امکان حذف گروه های خاص نیست'

    def has_object_permission(self, request: Request, view: View, obj: BusinessmanGroups) -> bool:

        if request.method == 'DELETE':
            return not obj.is_special_group()
        return True


