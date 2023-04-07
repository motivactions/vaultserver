from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class VaultsConfig(AppConfig):
    icon = "cash-100"
    default_auto_field = "django.db.models.BigAutoField"
    name = "vaults"
    app_label = "vaults"
    verbose_name = _("Vaults")

    def ready(self):
        from . import signals  # NOQA
        from . import handlers

        post_migrate.connect(init_app, sender=self)


def init_app(sender, **kwargs):
    """Called after migrations"""
    pass
