# Generated by Django 2.2 on 2020-03-25 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_businessman_has_sms_panel'),
        ('invitation', '0014_auto_20200325_0026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendinvitation',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='friendinvitation',
            name='invitation_type',
        ),
        migrations.AddField(
            model_name='friendinvitation',
            name='invited',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invited', to='users.Customer'),
        ),
        migrations.AddField(
            model_name='friendinvitation',
            name='inviter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inviter', to='users.Customer'),
        ),
    ]
