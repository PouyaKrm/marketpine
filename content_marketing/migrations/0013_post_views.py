# Generated by Django 2.2 on 2021-02-13 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_marketing', '0012_auto_20210213_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
