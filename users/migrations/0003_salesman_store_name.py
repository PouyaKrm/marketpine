# Generated by Django 2.2 on 2019-04-13 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190413_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesman',
            name='store_name',
            field=models.CharField(default=None, max_length=1000),
            preserve_default=False,
        ),
    ]
