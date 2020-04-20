from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from background_tasks.services import background_task_service


class Command(BaseCommand):

    def handle(self, *args, **options):
        r = background_task_service.kill_and_create_new_back_tasks()
        self.stdout.write('tasks run sucessfully')
        return r
