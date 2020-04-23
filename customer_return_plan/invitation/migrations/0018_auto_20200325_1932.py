# Generated by Django 2.2 on 2020-03-25 15:02

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0011_businessman_has_sms_panel'),
        ('invitation', '0017_auto_20200325_1923'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendinvitation',
            unique_together={('businessman', 'invited')},
        ),
    ]