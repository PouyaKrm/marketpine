# Generated by Django 2.2 on 2019-10-07 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panelprofile', '0002_auto_20191007_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smspanelinfo',
            name='api_key',
            field=models.TextField(),
        ),
    ]
