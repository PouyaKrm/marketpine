# Generated by Django 2.2 on 2020-02-20 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smspanel', '0024_auto_20200220_0348'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsmessage',
            name='send_fail_attempts',
            field=models.IntegerField(default=0),
        ),
    ]
