# Generated by Django 2.2 on 2020-04-15 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customerpurchase', '0008_auto_20200413_2114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerpurchase',
            name='loyalty_setting',
        ),
        migrations.AlterField(
            model_name='customerpurchase',
            name='create_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='customerpurchase',
            name='update_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
