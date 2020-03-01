# Generated by Django 2.2 on 2020-01-29 10:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content_marketing', '0005_auto_20200129_0159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentmarketingsettings',
            name='businessman',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='content_marketing_settings', to=settings.AUTH_USER_MODEL),
        ),
    ]