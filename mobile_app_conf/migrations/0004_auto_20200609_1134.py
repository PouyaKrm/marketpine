# Generated by Django 2.2 on 2020-06-09 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_app_conf', '0003_auto_20200606_2014'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mobileapppageconf',
            old_name='store_location',
            new_name='market_location',
        ),
        migrations.AddField(
            model_name='mobileappheader',
            name='show_order',
            field=models.IntegerField(null=True),
        ),
    ]
