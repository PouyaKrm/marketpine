# Generated by Django 2.2 on 2020-02-19 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smspanel', '0018_smsmessage_receptors'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsmessage',
            name='send_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='smsmessage',
            name='sent_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
