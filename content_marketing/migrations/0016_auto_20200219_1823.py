# Generated by Django 2.2 on 2020-02-19 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content_marketing', '0015_auto_20200219_1820'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='customer_notif_message_template',
        ),
        migrations.RemoveField(
            model_name='post',
            name='send_notif_pwa',
        ),
        migrations.RemoveField(
            model_name='post',
            name='send_notif_sms',
        ),
    ]