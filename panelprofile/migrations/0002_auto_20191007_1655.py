# Generated by Django 2.2 on 2019-10-07 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panelprofile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smspanelinfo',
            name='sms_english_cost',
            field=models.PositiveIntegerField(),
        ),
    ]
