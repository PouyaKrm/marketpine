# Generated by Django 2.2 on 2020-01-29 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_marketing', '0010_auto_20200129_0255'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video_url',
            field=models.URLField(null=True),
        ),
    ]
