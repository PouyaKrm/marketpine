# Generated by Django 2.2 on 2019-12-05 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smspanel', '0008_auto_20191013_2153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentsms',
            name='customers',
        ),
        migrations.AddField(
            model_name='sentsms',
            name='is_sent_to_all',
            field=models.BooleanField(default=False),
        ),
    ]
