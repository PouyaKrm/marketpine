# Generated by Django 2.2 on 2020-12-12 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panelprofile', '0018_auto_20201212_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smspanelinfo',
            name='username',
            field=models.CharField(max_length=100),
        ),
    ]
