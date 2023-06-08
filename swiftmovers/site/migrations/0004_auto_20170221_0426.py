# Generated by Django 1.10.5 on 2017-02-21 10:26
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("site", "0003_sitesettings_description")]

    operations = [
        migrations.CreateModel(
            name="AuthorizationKey",
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
                    "name",
                    models.CharField(
                        choices=[("facebook", "Facebook"), ("google-oauth2", "Google")],
                        max_length=20,
                        verbose_name="name",
                    ),
                ),
                ("key", models.TextField(verbose_name="key")),
                ("password", models.TextField(verbose_name="password")),
                (
                    "site_settings",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="site.SiteSettings",
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="authorizationkey", unique_together=set([("site_settings", "name")])
        ),
    ]
