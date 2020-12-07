from rest_framework import permissions
from rest_framework.request import Request
from django.conf import settings

from customers.services import customer_service

count = settings.ALLOWED_CUSTOMER_REGISTER_FREE


class CanAddCustomer(permissions.BasePermission):

    message = 'تا فعال سازی پنل امکان ثبت مشتری جدید نیست'

    def has_permission(self, request: Request, view) -> bool:

        if request.method != 'POST':
            return True

        if not request.user.is_panel_active():
            registered_count = customer_service.get_businessman_customers(request.user).count()
            return registered_count < count

        return True
