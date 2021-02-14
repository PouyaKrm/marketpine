from django.views.generic.base import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class AllowAnyOnGet(BasePermission):

    def has_permission(self, request: Request, view: View) -> bool:
        if request.method == 'GET':
            return True
        return request.user.is_authenticated
