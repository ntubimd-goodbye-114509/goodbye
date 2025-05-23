# Generated by Django 4.2.5 on 2025-04-04 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goodBuy_web', '0002_payment_profile_payment_account'),
        ('goodBuy_shop', '0004_shop_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shop_payment',
            name='account',
        ),
        migrations.RemoveField(
            model_name='shop_payment',
            name='img',
        ),
        migrations.AlterField(
            model_name='shop_payment',
            name='payment',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='goodBuy_web.payment_account'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
    ]
