# Generated by Django 2.2 on 2020-04-15 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customerpurchase', '0009_auto_20200415_1038'),
        ('customer_return_plan', '0007_auto_20200412_1431'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discount',
            name='customers_used',
        ),
        migrations.AddField(
            model_name='discount',
            name='purchases',
            field=models.ManyToManyField(related_name='purchases', related_query_name='purchases', to='customerpurchase.CustomerPurchase'),
        ),
        migrations.AlterField(
            model_name='discount',
            name='create_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='discount',
            name='update_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='discount',
            name='used_for',
            field=models.CharField(choices=[('0', 'None'), ('1', 'Festival'), ('2', 'Invitation'), ('3', 'Loyalty Amount'), ('4', 'Loyalty Number')], default='0', max_length=2),
        ),
    ]
