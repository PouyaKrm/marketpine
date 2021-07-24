# Generated by Django 2.2 on 2021-07-24 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0040_auto_20210620_1957'),
        ('loyalty', '0017_auto_20210724_1333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerexclusivediscount',
            name='customer',
        ),
        migrations.AddField(
            model_name='customerexclusivediscount',
            name='businessman_customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='exclusive_discounts', related_query_name='exclusive_discounts',
                                    to='users.BusinessmanCustomer'),
        ),
        migrations.AlterField(
            model_name='customerexclusivediscount',
            name='discount',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='exclusive_customers', related_query_name='exclusive_customers',
                                    to='customer_return_plan.Discount'),
        ),
        migrations.AlterModelTable(
            name='customerexclusivediscount',
            table='customer_exclusive_discounts',
        ),
    ]
