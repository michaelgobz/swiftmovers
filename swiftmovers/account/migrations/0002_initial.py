# Generated by Django 3.2.19 on 2023-06-08 14:07

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0001_initial'),
        ('permission', '0001_initial'),
        ('order', '0002_initial'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='permission.Permission', verbose_name='permissions'),
        ),
        migrations.AddField(
            model_name='customernote',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customernote',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customerevent',
            name='app',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='app.app'),
        ),
        migrations.AddField(
            model_name='customerevent',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.order'),
        ),
        migrations.AddField(
            model_name='customerevent',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='address',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='address_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='address',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='address_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='address',
            index=django.contrib.postgres.indexes.GinIndex(fields=['first_name', 'last_name', 'city', 'country'], name='address_search_gin', opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='address',
            index=django.contrib.postgres.indexes.GinIndex(fields=['company_name', 'street_address_1', 'street_address_2', 'city', 'postal_code', 'phone'], name='warehouse_address_search_gin', opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops']),
        ),
        migrations.AddField(
            model_name='user',
            name='addresses',
            field=models.ManyToManyField(blank=True, related_name='user_addresses', to='account.Address'),
        ),
        migrations.AddField(
            model_name='user',
            name='default_billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.address'),
        ),
        migrations.AddField(
            model_name='user',
            name='default_shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.address'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='account.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='permission.Permission', verbose_name='user permissions'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='user_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='user_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.GinIndex(fields=['email', 'first_name', 'last_name'], name='order_user_search_gin', opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_document'], name='user_search_gin', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='user_p_meta_jsonb_path_idx', opclasses=['jsonb_path_ops']),
        ),
    ]
