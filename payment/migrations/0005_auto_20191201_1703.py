# Generated by Django 2.2 on 2019-12-01 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20191128_2355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default='PENDING', max_length=7),
        ),
    ]
