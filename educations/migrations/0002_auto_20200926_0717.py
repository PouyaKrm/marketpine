# Generated by Django 2.2 on 2020-09-26 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationtype',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
