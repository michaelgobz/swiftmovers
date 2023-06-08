# Generated by Django 3.0.6 on 2020-06-09 08:45

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import swiftmovers.core.utils.json_serializer


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExportFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                            ("deleted", "Deleted"),
                        ],
                        default="pending",
                        max_length=50,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("content_file", models.FileField(null=True, upload_to="export_files")),
                (
                    "app",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="export_files",
                        to="app.App",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="export_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ExportEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("export_pending", "Data export was started."),
                            (
                                "export_success",
                                "Data export was completed successfully.",
                            ),
                            ("export_failed", "Data export failed."),
                            ("export_deleted", "Export file was deleted."),
                            (
                                "exported_file_sent",
                                "Email with link to download file was sent to the "
                                "customer.",
                            ),
                            (
                                "Export_failed_info_sent",
                                "Email with info that export failed was sent to the "
                                "customer.",
                            ),
                        ],
                        max_length=255,
                    ),
                ),
                (
                    "parameters",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        default=dict,
                        encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                    ),
                ),
                (
                    "app",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="export_csv_events",
                        to="app.App",
                    ),
                ),
                (
                    "export_file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="csv.ExportFile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="export_csv_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
