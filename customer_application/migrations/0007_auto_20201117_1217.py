# Generated by Django 2.2 on 2020-11-17 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer_application', '0006_customerupdatephonemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerupdatephonemodel',
            name='verify_code',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='phone_update', related_query_name='phone_update', to='customer_application.CustomerVerificationCode'),
        ),
    ]