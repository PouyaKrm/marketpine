# Generated by Django 2.2 on 2019-07-17 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendinvitation',
            name='invitation_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
