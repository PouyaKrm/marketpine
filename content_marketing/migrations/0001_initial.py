# Generated by Django 2.2 on 2020-03-02 18:03

import content_marketing.models
from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('smspanel', '0027_smsmessage_reserved_credit'),
        ('users', '0011_businessman_has_sms_panel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('videofile', models.FileField(max_length=254, storage=django.core.files.storage.FileSystemStorage(base_url='/content/video/', location='C:\\Users\\Pouya\\Desktop\\programs\\python\\marketpine-backend\\..\\videos/'), upload_to=content_marketing.models.Post.get_upload_path)),
                ('mobile_thumbnail', models.ImageField(max_length=254, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/content/video/', location='C:\\Users\\Pouya\\Desktop\\programs\\python\\marketpine-backend\\..\\videos/'), upload_to=content_marketing.models.Post.get_upload_path)),
                ('video_url', models.URLField(null=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('confirmation_status', models.CharField(choices=[('0', 'Rejected'), ('1', 'Accepted'), ('2', 'Pending')], default='2', max_length=1)),
                ('send_sms', models.BooleanField(default=False)),
                ('send_pwa', models.BooleanField(default=False)),
                ('businessman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('notif_sms', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='smspanel.SMSMessage')),
            ],
        ),
        migrations.CreateModel(
            name='ContentMarketingSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_template', models.CharField(default='', max_length=260)),
                ('send_video_upload_message', models.BooleanField(default=False)),
                ('businessman', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='content_marketing_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Customer')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='content_marketing.Post')),
            ],
            options={
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Customer')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='content_marketing.Post')),
            ],
            options={
                'ordering': ['creation_date'],
                'unique_together': {('customer', 'post')},
            },
        ),
    ]
