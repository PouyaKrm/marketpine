# Generated by Django 2.2 on 2019-10-26 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='imei',
            field=models.CharField(max_length=25),
        ),
    ]
