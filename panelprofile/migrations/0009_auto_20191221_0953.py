# Generated by Django 2.2 on 2019-12-21 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panelprofile', '0008_auto_20191209_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smspanelinfo',
            name='api_key',
            field=models.TextField(default=None, null=True),
        ),
    ]
