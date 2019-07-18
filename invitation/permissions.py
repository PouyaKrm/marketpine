from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request


class HasInvitationAccess(permissions.BasePermission):

    def has_permission(self, request: Request, view: View):

        return request.user.friend_invitation_access
