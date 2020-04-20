from django.contrib import admin
from .models import BackgroundTask

# Register your models here.
from django.http.request import HttpRequest


# class BackTaskAdminModel(admin.ModelAdmin):
#
#     def has_add_permission(self, request: HttpRequest, obj = ...):
#         return False
#
#     def has_delete_permission(self, request: HttpRequest, obj= ...):
#         return True
#
#     list_display = ['name', 'pid', 'status', 'create_date', 'update_date']
#
#
# admin.site.register(BackgroundTask, BackTaskAdminModel)
