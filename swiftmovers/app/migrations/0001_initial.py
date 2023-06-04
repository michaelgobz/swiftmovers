# Generated by Django 3.2.19 on 2023-06-04 17:14

from django.db import migrations, models
import django.db.models.deletion
import swiftmovers.core.utils.json_serializer


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('uuid', models.UUIDField(blank=True, null=True, unique=True)),
                ('name', models.CharField(max_length=60)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('type', models.CharField(choices=[('local', 'local'), ('thirdparty', 'thirdparty')], default='local', max_length=60)),
                ('identifier', models.CharField(blank=True, max_length=256, null=True)),
                ('about_app', models.TextField(blank=True, null=True)),
                ('data_privacy', models.TextField(blank=True, null=True)),
                ('data_privacy_url', models.URLField(blank=True, null=True)),
                ('homepage_url', models.URLField(blank=True, null=True)),
                ('support_url', models.URLField(blank=True, null=True)),
                ('configuration_url', models.URLField(blank=True, null=True)),
                ('app_url', models.URLField(blank=True, null=True)),
                ('manifest_url', models.URLField(blank=True, null=True)),
                ('version', models.CharField(blank=True, max_length=60, null=True)),
                ('audience', models.CharField(blank=True, max_length=256, null=True)),
                ('is_installed', models.BooleanField(default=True)),
                ('author', models.CharField(blank=True, max_length=60, null=True)),
            ],
            options={
                'ordering': ('name', 'pk'),
                'permissions': (('manage_apps', 'Manage apps'), ('manage_observability', 'Manage observability')),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AppExtension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=256)),
                ('url', models.URLField()),
                ('mount', models.CharField(choices=[('customer_overview_create', 'customer_overview_create'), ('customer_overview_more_actions', 'customer_overview_more_actions'), ('customer_details_more_actions', 'customer_details_more_actions'), ('product_overview_create', 'product_overview_create'), ('product_overview_more_actions', 'product_overview_more_actions'), ('product_details_more_actions', 'product_details_more_actions'), ('navigation_catalog', 'navigation_catalog'), ('navigation_orders', 'navigation_orders'), ('navigation_customers', 'navigation_customers'), ('navigation_discounts', 'navigation_discounts'), ('navigation_translations', 'navigation_translations'), ('navigation_pages', 'navigation_pages'), ('order_details_more_actions', 'order_details_more_actions'), ('order_overview_create', 'order_overview_create'), ('order_overview_more_actions', 'order_overview_more_actions')], max_length=256)),
                ('target', models.CharField(choices=[('popup', 'popup'), ('app_page', 'app_page')], default='popup', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='AppInstallation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('deleted', 'Deleted')], default='pending', max_length=50)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(blank=True, null=True, unique=True)),
                ('app_name', models.CharField(max_length=60)),
                ('manifest_url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AppToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=128)),
                ('auth_token', models.CharField(max_length=128, unique=True)),
                ('token_last_4', models.CharField(max_length=4)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='app.app')),
            ],
        ),
    ]
