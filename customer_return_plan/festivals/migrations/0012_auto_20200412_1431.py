# Generated by Django 2.2 on 2020-04-12 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivals', '0011_auto_20200325_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='festival',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='festival',
            name='update_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
