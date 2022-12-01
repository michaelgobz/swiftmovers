# Generated by Django 4.1.3 on 2022-11-19 12:20

from decimal import Decimal
import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('checkouts', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gateway', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('to_confirm', models.BooleanField(default=False)),
                ('partial', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('charge_status', models.CharField(choices=[('not-charged', 'Not charged'), ('pending', 'Pending'), ('partially-charged', 'Partially charged'), ('fully-charged', 'Fully charged'), ('partially-refunded', 'Partially refunded'), ('fully-refunded', 'Fully refunded'), ('refused', 'Refused'), ('cancelled', 'Cancelled')], default='not-charged', max_length=20)),
                ('token', models.CharField(blank=True, default='', max_length=512)),
                ('total', models.DecimalField(decimal_places=3, default=Decimal('0.0'), max_digits=12)),
                ('captured_amount', models.DecimalField(decimal_places=3, default=Decimal('0.0'), max_digits=12)),
                ('currency', models.CharField(max_length=3)),
                ('store_payment_method', models.CharField(choices=[('on_session', 'On session'), ('off_session', 'Off session'), ('none', 'None')], default='none', max_length=11)),
                ('billing_email', models.EmailField(blank=True, max_length=254)),
                ('billing_first_name', models.CharField(blank=True, max_length=256)),
                ('billing_last_name', models.CharField(blank=True, max_length=256)),
                ('billing_company_name', models.CharField(blank=True, max_length=256)),
                ('billing_address_1', models.CharField(blank=True, max_length=256)),
                ('billing_address_2', models.CharField(blank=True, max_length=256)),
                ('billing_city', models.CharField(blank=True, max_length=256)),
                ('billing_city_area', models.CharField(blank=True, max_length=128)),
                ('billing_postal_code', models.CharField(blank=True, max_length=256)),
                ('billing_country_code', models.CharField(blank=True, max_length=2)),
                ('billing_country_area', models.CharField(blank=True, max_length=256)),
                ('cc_first_digits', models.CharField(blank=True, default='', max_length=6)),
                ('cc_last_digits', models.CharField(blank=True, default='', max_length=4)),
                ('cc_brand', models.CharField(blank=True, default='', max_length=40)),
                ('cc_exp_month', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('cc_exp_year', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000)])),
                ('payment_method_type', models.CharField(blank=True, max_length=256)),
                ('customer_ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('extra_data', models.TextField(blank=True, default='')),
                ('return_url', models.URLField(blank=True, null=True)),
                ('psp_reference', models.CharField(blank=True, db_index=True, max_length=512, null=True)),
                ('checkout', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='checkouts.deliverycheckout')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='orders.order')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, default='', max_length=512)),
                ('type', models.CharField(blank=True, default='', max_length=512)),
                ('reference', models.CharField(blank=True, default='', max_length=512)),
                ('available_actions', django_mysql.models.ListCharField(models.CharField(choices=[('charge', 'Charge payment'), ('refund', 'Refund payment'), ('void', 'Void payment')], default=list, max_length=256), max_length=256, size=None)),
                ('currency', models.CharField(max_length=3)),
                ('charged_value', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=12)),
                ('authorized_value', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=12)),
                ('refunded_value', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=12)),
                ('voided_value', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=12)),
                ('checkout', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_transactions', to='checkouts.deliverycheckout')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payment_transactions', to='orders.order')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failure', 'Failure')], default='success', max_length=128)),
                ('reference', models.CharField(blank=True, default='', max_length=512)),
                ('name', models.CharField(blank=True, default='', max_length=512)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='payments.transactionitem')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(blank=True, default='', max_length=512)),
                ('kind', models.CharField(choices=[('external', 'External reference'), ('auth', 'Authorization'), ('pending', 'Pending'), ('action_to_confirm', 'Action to confirm'), ('refund', 'Refund'), ('refund_ongoing', 'Refund in progress'), ('capture', 'Capture'), ('void', 'Void'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], max_length=25)),
                ('is_success', models.BooleanField(default=False)),
                ('action_required', models.BooleanField(default=False)),
                ('action_required_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('currency', models.CharField(max_length=3)),
                ('amount', models.DecimalField(decimal_places=3, default=Decimal('0.0'), max_digits=12)),
                ('error', models.TextField(null=True)),
                ('customer_id', models.CharField(max_length=256, null=True)),
                ('gateway_response', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('already_processed', models.BooleanField(default=False)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='payments.payment')),
            ],
        ),
    ]
