# Generated by Django 2.2 on 2019-07-17 11:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0004_auto_20190717_1556'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendinvitation',
            old_name='is_confirmed',
            new_name='confirmed',
        ),
        migrations.RenameField(
            model_name='friendinvitation',
            old_name='is_discount_used',
            new_name='discount_used',
        ),
    ]
