# Generated by Django 2.2 on 2020-04-10 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0003_auto_20200410_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerpurchaseamountdiscountsettings',
            name='purchase_amount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='customerpurchasenumberdiscountsettings',
            name='purchase_number',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
