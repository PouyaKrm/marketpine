# Generated by Django 2.2 on 2021-06-30 09:48

import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('payment', '0023_billing'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='jcreate_date',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True, null=True),
        ),
    ]