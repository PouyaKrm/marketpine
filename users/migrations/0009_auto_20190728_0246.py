# Generated by Django 2.2 on 2019-07-27 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20190719_0102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessman',
            name='bot_access',
        ),
        migrations.RemoveField(
            model_name='businessman',
            name='instagram_access',
        ),
    ]
