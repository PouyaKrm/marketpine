# Generated by Django 2.2 on 2020-03-01 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20200125_0749'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessman',
            name='has_sms_panel',
            field=models.BooleanField(default=False),
        ),
    ]
