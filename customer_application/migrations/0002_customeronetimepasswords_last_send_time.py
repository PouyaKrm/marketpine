# Generated by Django 2.2 on 2020-08-08 12:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('customer_application', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeronetimepasswords',
            name='last_send_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]