# Generated by Django 4.2.5 on 2025-04-17 13:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goodBuy_web', '0005_blacklist_unique_blacklist_pair'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentaccount',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='paymentaccount',
            constraint=models.UniqueConstraint(fields=('user', 'payment'), name='unique_user_payment_account'),
        ),
    ]
