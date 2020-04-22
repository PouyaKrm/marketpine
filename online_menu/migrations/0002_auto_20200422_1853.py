# Generated by Django 2.2 on 2020-04-22 18:53

import django.core.files.storage
from django.db import migrations, models
import online_menu.models


class Migration(migrations.Migration):

    dependencies = [
        ('online_menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlinemenu',
            name='file',
            field=models.ImageField(max_length=200, storage=django.core.files.storage.FileSystemStorage(base_url='menu', location='/home/pouya795/Desktop/marketpine-backend/../resources/menus/'), upload_to=online_menu.models.OnlineMenu.get_upload_path),
        ),
    ]
