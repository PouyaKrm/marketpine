# Generated by Django 2.2 on 2020-05-31 21:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer_return_plan', '0012_auto_20200531_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasediscount',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_discount', related_query_name='purchase_discount', to='customer_return_plan.Discount'),
        ),
        migrations.AlterField(
            model_name='purchasediscount',
            name='purchase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_discount', related_query_name='purchases', to='customerpurchase.CustomerPurchase'),
        ),
    ]