# Generated by Django 3.2.17 on 2023-02-09 11:28

from django.db import migrations, models
import swiftmovers.core.utils.json_serializer
import swiftmovers.webhook.validators


class Migration(migrations.Migration):
    dependencies = [
        ("webhook", "0008_webhook_subscription_query"),
    ]

    operations = [
        migrations.AddField(
            model_name="webhook",
            name="custom_headers",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
                validators=[swiftmovers.webhook.validators.custom_headers_validator],
            ),
        ),
    ]
