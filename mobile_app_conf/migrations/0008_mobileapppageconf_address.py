# Generated by Django 2.2 on 2020-12-21 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_app_conf', '0007_auto_20200725_0825'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobileapppageconf',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
    ]
