# Generated by Django 3.2.12 on 2022-04-12 09:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("warehouse", "0020_merge_20220217_1316"),
    ]

    operations = [
        migrations.AddField(
            model_name="allocation",
            name="order_line_token",
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name="preorderallocation",
            name="order_line_token",
            field=models.UUIDField(null=True),
        ),
    ]