# Generated by Django 3.2.19 on 2023-06-08 14:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import swiftmovers.core.utils.json_serializer


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('deleted', 'Deleted')], default='pending', max_length=50)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('number', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(null=True)),
                ('external_url', models.URLField(max_length=2048, null=True)),
                ('invoice_file', models.FileField(upload_to='invoices')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvoiceEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('type', models.CharField(choices=[('requested', 'The invoice was requested'), ('requested_deletion', 'The invoice was requested for deletion'), ('created', 'The invoice was created'), ('deleted', 'The invoice was deleted'), ('sent', 'The invoice has been sent')], max_length=255)),
                ('parameters', models.JSONField(blank=True, default=dict, encoder=swiftmovers.core.utils.json_serializer.CustomJsonEncoder)),
                ('app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='app.app')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='invoice.invoice')),
            ],
            options={
                'ordering': ('date', 'pk'),
            },
        ),
    ]
