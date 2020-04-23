# Generated by Django 2.2 on 2019-07-30 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Festival',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('discount_code', models.CharField(max_length=12)),
                ('percent_off', models.PositiveIntegerField(default=0)),
                ('flat_rate_off', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]