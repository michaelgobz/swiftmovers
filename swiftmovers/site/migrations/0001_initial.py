# Generated by Django 3.2.19 on 2023-06-04 17:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_initial'),
        ('sites', '0002_alter_domain_unique'),
        ('menu', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header_text', models.CharField(blank=True, max_length=200)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('track_inventory_by_default', models.BooleanField(default=True)),
                ('default_weight_unit', models.CharField(choices=[('g', 'Gram'), ('lb', 'Pound'), ('oz', 'Ounce'), ('kg', 'kg'), ('tonne', 'Tonne')], default='kg', max_length=30)),
                ('automatic_fulfillment_digital_products', models.BooleanField(default=False)),
                ('default_digital_max_downloads', models.IntegerField(blank=True, null=True)),
                ('default_digital_url_valid_days', models.IntegerField(blank=True, null=True)),
                ('default_mail_sender_name', models.CharField(blank=True, default='', max_length=78, validators=[django.core.validators.RegexValidator('[\\n\\r]', code='forbidden_character', inverse_match=True, message='New lines are not allowed.'), django.core.validators.MaxLengthValidator(78)])),
                ('default_mail_sender_address', models.EmailField(blank=True, max_length=254, null=True)),
                ('customer_set_password_url', models.CharField(blank=True, max_length=255, null=True)),
                ('fulfillment_auto_approve', models.BooleanField(default=True)),
                ('fulfillment_allow_unpaid', models.BooleanField(default=True)),
                ('reserve_stock_duration_anonymous_user', models.IntegerField(blank=True, null=True)),
                ('reserve_stock_duration_authenticated_user', models.IntegerField(blank=True, null=True)),
                ('limit_quantity_per_checkout', models.IntegerField(blank=True, default=50, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('gift_card_expiry_type', models.CharField(choices=[('never_expire', 'Never expire'), ('expiry_period', 'Expiry period')], default='never_expire', max_length=32)),
                ('gift_card_expiry_period_type', models.CharField(blank=True, choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], max_length=32, null=True)),
                ('gift_card_expiry_period', models.PositiveIntegerField(blank=True, null=True)),
                ('charge_taxes_on_shipping', models.BooleanField(default=True)),
                ('include_taxes_in_prices', models.BooleanField(default=True)),
                ('display_gross_prices', models.BooleanField(default=True)),
                ('bottom_menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menu.menu')),
                ('company_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.address')),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='sites.site')),
                ('top_menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menu.menu')),
            ],
            options={
                'permissions': (('manage_settings', 'Manage settings.'), ('manage_translations', 'Manage translations.')),
            },
        ),
        migrations.CreateModel(
            name='SiteSettingsTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=35)),
                ('header_text', models.CharField(blank=True, max_length=200)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('site_settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='site.sitesettings')),
            ],
            options={
                'unique_together': {('language_code', 'site_settings')},
            },
        ),
    ]
