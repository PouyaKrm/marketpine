# Generated by Django 2.2 on 2020-10-06 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20200817_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessman',
            name='panel_duration_type',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='businessman',
            name='panel_activation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='businessman',
            name='panel_expiration_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
