# Generated by Django 2.2 on 2021-07-24 11:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('loyalty', '0019_auto_20210724_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerloyaltydiscountsettings',
            name='businessman',
        ),
        migrations.AddField(
            model_name='customerloyaltydiscountsettings',
            name='loyalty_settings',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='discount_settings', related_query_name='discount_settings',
                                    to='loyalty.CustomerLoyaltySettings'),
        ),
    ]
