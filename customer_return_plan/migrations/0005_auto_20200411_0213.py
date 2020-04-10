# Generated by Django 2.2 on 2020-04-10 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_return_plan', '0004_auto_20200411_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='used_for',
            field=models.CharField(choices=[('0', 'None'), ('1', 'Festival'), ('2', 'Invitation'), ('3', 'Loyalty Amount'), ('4', 'Loyalty Number')], default='0', max_length=2),
        ),
    ]
