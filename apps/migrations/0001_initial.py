# Generated by Django 4.1 on 2023-04-01 21:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rest_framework_api_key", "0005_auto_20220110_1102"),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
            fields=[
                ("created", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="name"
                    ),
                ),
                (
                    "domain",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="domain"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ApplicationKey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_keys",
                        to="apps.application",
                    ),
                ),
                (
                    "key",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="rest_framework_api_key.apikey",
                    ),
                ),
            ],
            options={
                "verbose_name": "Aplication API Key",
                "verbose_name_plural": "Aplication API Keys",
                "unique_together": {("application", "key")},
            },
        ),
        migrations.AddField(
            model_name="application",
            name="apikeys",
            field=models.ManyToManyField(
                through="apps.ApplicationKey", to="rest_framework_api_key.apikey"
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="applications",
                to=settings.AUTH_USER_MODEL,
                verbose_name="owner",
            ),
        ),
    ]
