# Generated by Django 3.2.19 on 2023-06-08 14:07

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceevent',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_events', to='order.order'),
        ),
        migrations.AddField(
            model_name='invoiceevent',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invoice',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='order.order'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='invoice_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='invoice_meta_idx'),
        ),
    ]
