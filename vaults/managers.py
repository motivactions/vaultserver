from django.db import models
from django.utils import timezone
from polymorphic.managers import PolymorphicManager


class ActiveAccountManager(PolymorphicManager):
    def get_queryset(self):
        now = timezone.now()
        qs = super().get_queryset()
        return qs.filter(
            models.Q(start_date__lte=now) | models.Q(start_date=None)
        ).filter(models.Q(end_date__gte=now) | models.Q(end_date=None))


class ExpiredAccountManager(PolymorphicManager):
    def get_queryset(self):
        now = timezone.now()
        qs = super().get_queryset()
        return qs.filter(end_date__lt=now)


class TransactionManager(PolymorphicManager):
    pass
