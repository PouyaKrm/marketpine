# Generated by Django 2.2 on 2020-05-02 18:08

import common.util.custom_validators
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panelprofile', '0014_auto_20200421_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authdoc',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/pouya/projects/python/marketpine-backend/../uploaded_media/'), upload_to='auth-doc', validators=[common.util.custom_validators.pdf_file_validator]),
        ),
    ]
