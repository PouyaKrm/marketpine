# Generated by Django 2.2 on 2019-08-04 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panelsetting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='panelsetting',
            name='welcome_message',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
