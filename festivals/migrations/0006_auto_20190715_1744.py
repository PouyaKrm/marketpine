# Generated by Django 2.2 on 2019-07-15 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivals', '0005_auto_20190715_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='festival',
            name='flat_rate_off',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='festival',
            name='percent_off',
            field=models.PositiveIntegerField(default=0),
        ),
    ]