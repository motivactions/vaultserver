from django.core.management.base import BaseCommand

from ...models import Account


class Command(BaseCommand):
    help = "Update recalculate account balance"

    def handle(self, *args, **options):
        for acc in Account.objects.all():
            acc.save()
