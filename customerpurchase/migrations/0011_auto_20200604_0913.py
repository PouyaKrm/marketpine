# Generated by Django 2.2 on 2020-06-04 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customerpurchase', '0010_auto_20200415_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerpurchase',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchases', related_query_name='purchases', to='users.Customer'),
        ),
    ]
