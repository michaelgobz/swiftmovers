# Generated by Django 3.2.19 on 2023-06-08 14:07

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('checkout', '0001_initial'),
        ('giftcard', '0001_initial'),
        ('product', '0001_initial'),
        ('warehouse', '0001_initial'),
        ('account', '0001_initial'),
        ('shipping', '0001_initial'),
        ('channel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='checkoutline',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='product.productvariant'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='billing_address',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.address'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='checkouts', to='channel.channel'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='collection_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checkouts', to='warehouse.warehouse'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='gift_cards',
            field=models.ManyToManyField(blank=True, related_name='checkouts', to='giftcard.GiftCard'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='shipping_address',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.address'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='shipping_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checkouts', to='shipping.shippingmethod'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkouts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='checkoutmetadata',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='checkoutmetadata_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='checkoutmetadata',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='checkoutmetadata_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='checkoutline',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='checkoutline_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='checkoutline',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='checkoutline_meta_idx'),
        ),
    ]
