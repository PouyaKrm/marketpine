# Generated by Django 2.2 on 2020-04-10 16:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomerPurchaseNumberDiscountSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now=True, null=True)),
                ('update_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('discount_type', models.CharField(choices=[('0', 'Percent'), ('1', 'Flat rate')], default='0', max_length=2, null=True)),
                ('percent_off', models.FloatField(default=0)),
                ('flat_rate_off', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomerLoyaltyDiscountSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now=True, null=True)),
                ('update_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('create_discount_for', models.CharField(choices=[('0', 'Purchase Amount'), ('1', 'Purchase Number'), ('2', 'Both')], default='2', max_length=2)),
                ('disabled', models.BooleanField(default=False)),
                ('businessman', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('purchase_amount_settings', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='loyalty.CustomerPurchaseAmountDiscountSettings')),
                ('purchase_number_settings', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='loyalty.CustomerPurchaseNumberDiscountSettings')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]