# Generated by Django 2.2 on 2021-07-18 09:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('payment', '0026_auto_20210718_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='failedpaymentoperation',
            name='operation_type',
            field=models.CharField(choices=[('SMS', 'SMS'), ('WALLET', 'WALLET'), ('SUBSCRIPTION', 'SUB')], default='0',
                                   max_length=2),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(choices=[('SMS', 'SMS'), ('WALLET', 'WALLET'), ('SUBSCRIPTION', 'SUB')], default='0',
                                   max_length=40),
        ),
    ]
