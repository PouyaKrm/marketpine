# Generated by Django 2.2 on 2019-07-17 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0003_auto_20190717_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendinvitation',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='friendinvitation',
            name='is_discount_used',
            field=models.BooleanField(default=False),
        ),
    ]
