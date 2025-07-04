# Generated by Django 4.2.5 on 2025-06-09 12:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goodBuy_shop', '0025_rename_date_shopannouncement_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopfootprints',
            name='session_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='shopfootprints',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='shopfootprints',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='shopfootprints',
            constraint=models.UniqueConstraint(fields=('session_key', 'shop'), name='unique_session_shop_footprints'),
        ),
    ]
