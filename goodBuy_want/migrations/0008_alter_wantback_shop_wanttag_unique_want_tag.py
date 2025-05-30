# Generated by Django 4.2.5 on 2025-04-17 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goodBuy_shop', '0018_alter_shopfootprints_unique_together_and_more'),
        ('goodBuy_want', '0007_alter_wanttag_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wantback',
            name='shop',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='goodBuy_shop.shop'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='wanttag',
            constraint=models.UniqueConstraint(fields=('want', 'tag'), name='unique_want_tag'),
        ),
    ]
