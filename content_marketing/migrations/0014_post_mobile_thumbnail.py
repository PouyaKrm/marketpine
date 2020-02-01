# Generated by Django 2.2 on 2020-02-01 17:00

import content_marketing.models
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_marketing', '0013_remove_post_video_message_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='mobile_thumbnail',
            field=models.ImageField(max_length=254, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/content/video/', location='C:\\Users\\Pouya\\Desktop\\programs\\python\\marketpine-backend\\..\\videos/'), upload_to=content_marketing.models.Post.get_upload_path),
        ),
    ]
