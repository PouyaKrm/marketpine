# Generated by Django 2.2 on 2021-05-02 11:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_verificationcodes_used_for'),
    ]

    operations = [
        migrations.RenameField(
            model_name='businessman',
            old_name='is_verified',
            new_name='is_phone_verified',
        ),
    ]
