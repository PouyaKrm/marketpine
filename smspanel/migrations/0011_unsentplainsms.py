# Generated by Django 2.2 on 2019-12-07 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('smspanel', '0010_auto_20191207_0844'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnsentPlainSMS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=612)),
                ('resend_stop', models.PositiveIntegerField(default=0)),
                ('businessman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
