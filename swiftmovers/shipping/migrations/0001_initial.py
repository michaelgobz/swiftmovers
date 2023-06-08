# Generated by Django 3.2.19 on 2023-06-08 14:07

from decimal import Decimal
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import django_measurement.models
import measurement.measures.mass
import swiftmovers.core.db.fields
import swiftmovers.core.utils.editorjs
import swiftmovers.core.utils.json_serializer
import swiftmovers.core.weight


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tax', '0001_initial'),
        ('channel', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('price', 'Price based shipping'), ('weight', 'Weight based shipping')], max_length=30)),
                ('minimum_order_weight', django_measurement.models.MeasurementField(blank=True, default=swiftmovers.core.weight.zero_weight, measurement=measurement.measures.mass.Mass, null=True)),
                ('maximum_order_weight', django_measurement.models.MeasurementField(blank=True, measurement=measurement.measures.mass.Mass, null=True)),
                ('maximum_delivery_days', models.PositiveIntegerField(blank=True, null=True)),
                ('minimum_delivery_days', models.PositiveIntegerField(blank=True, null=True)),
                ('description', swiftmovers.core.db.fields.SanitizedJSONField(blank=True, null=True, sanitizer=swiftmovers.core.utils.editorjs.clean_editor_js)),
                ('excluded_products', models.ManyToManyField(blank=True, to='product.Product')),
            ],
            options={
                'ordering': ('pk',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShippingZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('name', models.CharField(max_length=100)),
                ('countries', django_countries.fields.CountryField(blank=True, default=[], max_length=749, multiple=True)),
                ('default', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('channels', models.ManyToManyField(related_name='shipping_zones', to='channel.Channel')),
            ],
            options={
                'permissions': (('manage_shipping', 'Manage shipping.'),),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShippingMethodTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=35)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', swiftmovers.core.db.fields.SanitizedJSONField(blank=True, null=True, sanitizer=swiftmovers.core.utils.editorjs.clean_editor_js)),
                ('shipping_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='shipping.shippingmethod')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingMethodPostalCodeRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.CharField(max_length=32)),
                ('end', models.CharField(blank=True, max_length=32, null=True)),
                ('inclusion_type', models.CharField(choices=[('include', 'Shipping method should include postal code rule'), ('exclude', 'Shipping method should exclude postal code rule')], default='exclude', max_length=32)),
                ('shipping_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postal_code_rules', to='shipping.shippingmethod')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingMethodChannelListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minimum_order_price_amount', models.DecimalField(blank=True, decimal_places=3, default=Decimal('0.0'), max_digits=12, null=True)),
                ('currency', models.CharField(max_length=3)),
                ('maximum_order_price_amount', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('price_amount', models.DecimalField(decimal_places=3, default=Decimal('0.0'), max_digits=12)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_method_listings', to='channel.channel')),
                ('shipping_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_listings', to='shipping.shippingmethod')),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='shipping_zone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_methods', to='shipping.shippingzone'),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='tax_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_methods', to='tax.taxclass'),
        ),
        migrations.AddIndex(
            model_name='shippingzone',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='shippingzone_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='shippingzone',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='shippingzone_meta_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='shippingmethodtranslation',
            unique_together={('language_code', 'shipping_method')},
        ),
        migrations.AlterUniqueTogether(
            name='shippingmethodpostalcoderule',
            unique_together={('shipping_method', 'start', 'end')},
        ),
        migrations.AlterUniqueTogether(
            name='shippingmethodchannellisting',
            unique_together={('shipping_method', 'channel')},
        ),
        migrations.AddIndex(
            model_name='shippingmethod',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='shippingmethod_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='shippingmethod',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='shippingmethod_meta_idx'),
        ),
    ]
