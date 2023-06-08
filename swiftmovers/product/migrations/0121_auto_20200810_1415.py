# Generated by Django 3.1 on 2020-08-10 14:15

from django.db import migrations, models

import swiftmovers.core.utils.json_serializer


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0120_auto_20200714_0539"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attribute",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="attribute",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="description_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="category",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="categorytranslation",
            name="description_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="collection",
            name="description_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="collection",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="collectiontranslation",
            name="description_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="digitalcontent",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="digitalcontent",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="productvariant",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="productvariant",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
    ]
