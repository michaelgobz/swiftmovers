# Generated by Django 3.2.19 on 2023-06-04 17:14

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('is_active', models.BooleanField(default=False)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('currency_code', models.CharField(max_length=3)),
                ('default_country', django_countries.fields.CountryField(max_length=2)),
                ('allocation_strategy', models.CharField(choices=[('prioritize-sorting-order', 'Prioritize sorting order'), ('prioritize-high-stock', 'Prioritize high stock')], default='prioritize-sorting-order', max_length=255)),
                ('default_transaction_flow_strategy', models.CharField(choices=[('authorization', 'Authorize'), ('charge', 'Charge')], default='charge', max_length=255)),
                ('automatically_confirm_all_new_orders', models.BooleanField(default=True, null=True)),
                ('automatically_fulfill_non_shippable_gift_card', models.BooleanField(default=True, null=True)),
                ('expire_orders_after', models.IntegerField(blank=True, default=None, null=True)),
                ('order_mark_as_paid_strategy', models.CharField(choices=[('transaction_flow', 'Use transaction'), ('payment_flow', 'Use payment')], default='payment_flow', max_length=255)),
            ],
            options={
                'ordering': ('slug',),
                'permissions': (('manage_channels', 'Manage channels.'),),
            },
        ),
    ]
