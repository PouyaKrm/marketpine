# Generated by Django 2.2 on 2020-04-15 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_return_plan', '0008_auto_20200415_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='discount',
            name='update_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
