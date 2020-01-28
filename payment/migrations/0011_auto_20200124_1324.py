# Generated by Django 2.2 on 2020-01-24 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0010_payment_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(choices=[('SMS', '0'), ('ACTIVATION', '1')], default='0', max_length=2),
        ),
    ]