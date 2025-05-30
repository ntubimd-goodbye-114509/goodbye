# Generated by Django 4.2.5 on 2025-05-21 15:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('goodBuy_web', '0010_useraddress_is_delete_alter_paymentaccount_account_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentaccount',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='goodBuy_web.payment'),
        ),
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=100)),
                ('searched_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fk_user_search_history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
