# Generated by Django 2.2 on 2021-07-22 19:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0040_auto_20210620_1957'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loyalty', '0015_auto_20210722_2335'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerPoints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_date', models.DateTimeField(auto_now=True, null=True)),
                ('point', models.BigIntegerField(default=0)),
                ('businessman',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='points',
                                               related_query_name='points', to='users.Customer')),
            ],
            options={
                'db_table': 'customer_points',
                'unique_together': {('businessman', 'customer')},
            },
        ),
    ]
