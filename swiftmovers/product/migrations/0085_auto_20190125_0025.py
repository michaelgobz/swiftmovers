# Generated by Django 2.1.4 on 2019-01-25 06:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0084_auto_20190122_0113")]

    operations = [
        migrations.AlterField(
            model_name="producttype",
            name="is_shipping_required",
            field=models.BooleanField(default=True),
        )
    ]
