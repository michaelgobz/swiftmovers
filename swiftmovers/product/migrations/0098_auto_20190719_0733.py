# Generated by Django 2.2.3 on 2019-07-19 12:33

import django.contrib.postgres.fields.jsonb
from django.db import migrations

import swiftmovers.core.utils.json_serializer


class Migration(migrations.Migration):
    dependencies = [("product", "0097_auto_20190719_0458")]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="meta",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="meta",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
    ]
