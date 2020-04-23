# Generated by Django 2.2 on 2020-04-12 08:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer_return_plan', '0006_auto_20200412_1321'),
        ('users', '0011_businessman_has_sms_panel'),
        ('loyalty', '0004_auto_20200410_2325'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerLoyalty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now=True, null=True)),
                ('update_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('loyalty_for', models.CharField(choices=[('0', 'Purchase number'), ('1', 'Purchase amount')], max_length=2)),
                ('businessman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.Customer')),
                ('discount', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='customer_return_plan.Discount')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]