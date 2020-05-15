from django.core.management.base import BaseCommand

from users.models import BusinessCategory


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        BusinessCategory.create_default_categories()
