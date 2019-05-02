from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Starts the bot'

    def handle(self, *args, **options):
        from bot.main import main
        main()
