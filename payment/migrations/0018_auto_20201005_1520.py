# Generated by Django 2.2 on 2020-10-05 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0017_payment_panel_plan_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='panel_plan_id',
            new_name='panel_plan',
        ),
    ]