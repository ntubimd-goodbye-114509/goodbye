# Generated by Django 4.2.5 on 2025-04-20 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goodBuy_shop', '0018_alter_shopfootprints_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='deposit',
            field=models.BooleanField(default=False),
        ),
    ]
