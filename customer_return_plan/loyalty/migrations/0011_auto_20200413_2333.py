# Generated by Django 2.2 on 2020-04-13 19:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0010_auto_20200413_2327'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerloyaltydiscountsettings',
            old_name='sum_purchase_amount_setting',
            new_name='sum_purchase_amount_settings',
        ),
    ]
