# Generated by Django 4.2.5 on 2025-04-20 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goodBuy_order', '0011_order_payment_account_info_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shop_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
