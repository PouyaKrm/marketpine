# Generated by Django 2.2 on 2021-06-24 14:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0021_payment_call_back_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_date', models.DateTimeField(auto_now=True, null=True)),
                ('available_credit', models.BigIntegerField(default=0)),
                ('used_credit', models.BigIntegerField(default=0)),
                ('last_credit_increase_date', models.DateTimeField(blank=True, null=True)),
                ('businessman',
                 models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'wallet',
                'ordering': ('-create_date', '-update_date'),
            },
        ),
    ]
