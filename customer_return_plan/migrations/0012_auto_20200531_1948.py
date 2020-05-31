# Generated by Django 2.2 on 2020-05-31 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer_return_plan', '0011_auto_20200531_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasediscount',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discounts', related_query_name='discounts', to='customer_return_plan.Discount'),
        ),
    ]
