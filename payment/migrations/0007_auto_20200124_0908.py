# Generated by Django 2.2 on 2020-01-24 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_auto_20200124_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(null=True),
        ),
    ]
