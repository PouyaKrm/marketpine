# Generated by Django 2.2 on 2019-10-08 20:40

from django.db import migrations, models
import panelprofile.models


class Migration(migrations.Migration):

    dependencies = [
        ('panelprofile', '0004_authdoc_businessmanauthdocs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessmanauthdocs',
            name='birth_certificate',
            field=models.ImageField(max_length=40, null=True, upload_to=panelprofile.models.BusinessmanAuthDocs.get_upload_path),
        ),
        migrations.AlterField(
            model_name='businessmanauthdocs',
            name='national_card',
            field=models.ImageField(max_length=40, null=True, upload_to=panelprofile.models.BusinessmanAuthDocs.get_upload_path),
        ),
    ]