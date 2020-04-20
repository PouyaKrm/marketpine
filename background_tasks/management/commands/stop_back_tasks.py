from django.core.management import BaseCommand
from background_tasks.services import background_task_service


class Command(BaseCommand):

    def handle(self, *args, **options):
        background_task_service.kill_all_tasks_and_delete_from_db()
        self.stdout.write('tasks stop sucessfullty')
