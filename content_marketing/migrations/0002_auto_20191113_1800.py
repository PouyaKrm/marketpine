# Generated by Django 2.2 on 2019-11-13 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content_marketing', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='video',
            new_name='videofile',
        ),
    ]
