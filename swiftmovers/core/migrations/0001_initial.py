# Generated by Django 3.2.19 on 2023-06-04 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('webhook', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('deleted', 'Deleted')], default='pending', max_length=50)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventDelivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=255)),
                ('event_type', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='EventPayload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payload', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventDeliveryAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task_id', models.CharField(max_length=255, null=True)),
                ('duration', models.FloatField(null=True)),
                ('response', models.TextField(null=True)),
                ('response_headers', models.TextField(null=True)),
                ('response_status_code', models.PositiveSmallIntegerField(null=True)),
                ('request_headers', models.TextField(null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=255)),
                ('delivery', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='core.eventdelivery')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='eventdelivery',
            name='payload',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='core.eventpayload'),
        ),
        migrations.AddField(
            model_name='eventdelivery',
            name='webhook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook.webhook'),
        ),
    ]