# Generated by Django 3.2.19 on 2023-06-08 14:07

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0001_initial'),
        ('permission', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appinstallation',
            name='permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions which will be assigned to app.', related_name='app_installation_set', related_query_name='app_installation', to='permission.Permission'),
        ),
        migrations.AddField(
            model_name='appextension',
            name='app',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extensions', to='app.app'),
        ),
        migrations.AddField(
            model_name='appextension',
            name='permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this app extension.', to='permission.Permission'),
        ),
        migrations.AddField(
            model_name='app',
            name='permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this app.', related_name='app_set', related_query_name='app', to='permission.Permission'),
        ),
        migrations.AddIndex(
            model_name='app',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='app_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='app',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='app_meta_idx'),
        ),
    ]
