# Generated by Django 2.2 on 2019-12-07 18:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('smspanel', '0012_unsentplainsms_resend_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='unsentplainsms',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2019, 12, 7, 18, 9, 27, 542560, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
