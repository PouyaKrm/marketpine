# Generated by Django 2.2 on 2019-10-06 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smspanel', '0002_auto_20190730_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentsms',
            name='content',
            field=models.CharField(max_length=612),
        ),
    ]
