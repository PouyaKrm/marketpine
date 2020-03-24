# Generated by Django 2.2 on 2020-03-24 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0011_businessman_has_sms_panel'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now=True, null=True)),
                ('update_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('discount_type', models.CharField(choices=[('0', 'Percent'), ('1', 'Flat rate')], default='0', max_length=2, null=True)),
                ('percent_off', models.FloatField(default=0)),
                ('flat_rate_off', models.PositiveIntegerField(default=0)),
                ('discount_code', models.CharField(max_length=20)),
                ('expires', models.BooleanField(default=False)),
                ('expire_date', models.DateTimeField(blank=True, null=True)),
                ('businessman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('customers_used', models.ManyToManyField(related_name='customers_used', to='users.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
