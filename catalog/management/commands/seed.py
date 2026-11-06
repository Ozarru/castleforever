from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Alias for seed_catalog.'
    def handle(self, *args, **options):
        call_command('seed_catalog', *args, **options)

