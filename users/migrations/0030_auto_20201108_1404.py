# Generated by Django 2.2 on 2020-11-08 10:34

import base_app.models
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_customer_is_phone_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessman',
            name='logo',
            field=models.ImageField(blank=True, max_length=254, null=True, storage=base_app.models.PublicFileStorage(base_url='logo', subdir='logo'), upload_to=users.models.Businessman.get_upload_path),
        ),
    ]
