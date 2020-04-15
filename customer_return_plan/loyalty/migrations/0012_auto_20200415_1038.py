# Generated by Django 2.2 on 2020-04-15 06:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0011_auto_20200413_2333'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerPurchaseAmountDiscountSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now=True, null=True)),
                ('update_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('discount_type', models.CharField(choices=[('0', 'Percent'), ('1', 'Flat rate')], default='0', max_length=2, null=True)),
                ('percent_off', models.FloatField(default=0)),
                ('flat_rate_off', models.PositiveIntegerField(default=0)),
                ('purchase_amount', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='customerloyaltydiscountsettings',
            name='one_time_purchase_amount_settings',
        ),
        migrations.RemoveField(
            model_name='customerloyaltydiscountsettings',
            name='sum_purchase_amount_settings',
        ),
        migrations.AlterField(
            model_name='customerloyaltydiscountsettings',
            name='businessman',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='customerloyaltydiscountsettings',
            name='create_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='customerloyaltydiscountsettings',
            name='purchase_number_settings',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='loyalty.CustomerPurchaseNumberDiscountSettings'),
        ),
        migrations.AlterField(
            model_name='customerloyaltydiscountsettings',
            name='update_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='customerpurchasenumberdiscountsettings',
            name='create_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='customerpurchasenumberdiscountsettings',
            name='update_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.DeleteModel(
            name='CustomerLoyalty',
        ),
        migrations.DeleteModel(
            name='CustomerOneTimePurchaseAmountDiscountSettings',
        ),
        migrations.DeleteModel(
            name='CustomerSumPurchaseAmountDiscountSettings',
        ),
        migrations.AddField(
            model_name='customerloyaltydiscountsettings',
            name='purchase_amount_settings',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='loyalty.CustomerPurchaseAmountDiscountSettings'),
        ),
    ]
