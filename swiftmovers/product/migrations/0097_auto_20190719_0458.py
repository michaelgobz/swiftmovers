# Generated by Django 2.2.3 on 2019-07-19 09:58

import django.contrib.postgres.fields.jsonb
from django.db import migrations

import swiftmovers.core.utils.json_serializer


class Migration(migrations.Migration):
    dependencies = [("product", "0096_auto_20190719_0339")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="private_meta",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="meta",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
            ),
        ),
    ]
