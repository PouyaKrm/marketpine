# Generated by Django 2.2 on 2020-08-06 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20200515_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerOneTimePasswords',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_date', models.DateTimeField(auto_now=True, null=True)),
                ('customer_phone', models.CharField(max_length=15)),
                ('expiration_time', models.DateTimeField()),
                ('code', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]