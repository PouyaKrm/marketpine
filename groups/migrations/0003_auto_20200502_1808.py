# Generated by Django 2.2 on 2020-05-02 18:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20190730_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessmangroups',
            name='type',
            field=models.CharField(choices=[('0', 'NORMAL'), ('1', 'SPECIAL')], default='0', max_length=2),
        ),
        migrations.AddField(
            model_name='businessmangroups',
            name='update_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='businessmangroups',
            name='businessman',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='businessmangroups',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]