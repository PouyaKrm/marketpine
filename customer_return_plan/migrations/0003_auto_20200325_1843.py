# Generated by Django 2.2 on 2020-03-25 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_return_plan', '0002_discount_used_for'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='used_for',
            field=models.CharField(choices=[('0', 'None'), ('1', 'Festival'), ('2', 'Invitation')], default='0', max_length=2),
        ),
    ]