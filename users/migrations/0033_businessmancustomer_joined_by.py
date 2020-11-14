# Generated by Django 2.2 on 2020-11-14 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_businessman_page_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessmancustomer',
            name='joined_by',
            field=models.CharField(choices=[('0', 'By Panel'), ('1', 'Customer App')], default='0', max_length=2),
        ),
    ]