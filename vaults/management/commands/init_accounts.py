from django.core.management.base import BaseCommand

from ...setup import create_default_accounts


class Command(BaseCommand):
    help = "Initialize baristand accounts default structure"

    def handle(self, *args, **options):
        create_default_accounts()
