# Generated by Django 2.2 on 2019-04-18 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='salesmencustomer',
            unique_together={('customer', 'salesman')},
        ),
    ]