# Generated by Django 4.2.5 on 2025-04-11 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goodBuy_shop', '0014_alter_shop_end_time_alter_shop_start_time_shopimg'),
        ('goodBuy_want', '0005_wanttag_wantimg'),
    ]

    operations = [
        migrations.AddField(
            model_name='want',
            name='permission',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='goodBuy_shop.permission'),
            preserve_default=False,
        ),
    ]
