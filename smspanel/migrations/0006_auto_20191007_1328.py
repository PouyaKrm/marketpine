# Generated by Django 2.2 on 2019-10-07 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smspanel', '0005_auto_20191007_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smspanelinfo',
            name='api_key',
            field=models.CharField(max_length=150),
        ),
    ]