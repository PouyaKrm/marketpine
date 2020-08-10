# Generated by Django 2.2 on 2020-08-08 09:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_customeronetimepasswords_send_attempts'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='customer',
            unique_together=set(),
        ),
        migrations.CreateModel(
            name='BusinessmanCustomer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_date', models.DateTimeField(auto_now=True, null=True)),
                ('businessman', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='connected_customers', related_query_name='connected_customers', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='connected_businessmans', related_query_name='connected_businessmans', to='users.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='customer',
            name='businessman',
        ),
        migrations.AddField(
            model_name='customer',
            name='businessmans',
            field=models.ManyToManyField(related_name='customers', related_query_name='businessman', through='users.BusinessmanCustomer', to=settings.AUTH_USER_MODEL),
        ),
    ]