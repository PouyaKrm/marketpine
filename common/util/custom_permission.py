from rest_framework import permissions
from users.models import AuthStatus

class IsAuthorized(permissions.BasePermission):

    message = 'شما هنوز احراز هویت نشده اید'

    def has_permission(self, request):

        return request.user.authorized == AuthStatus.AUTHORIZED