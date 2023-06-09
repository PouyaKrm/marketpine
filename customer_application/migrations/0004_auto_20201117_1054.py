# Generated by Django 2.2 on 2020-11-17 07:24

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_businessmancustomer_joined_by'),
        ('customer_application', '0003_auto_20200901_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerVerificationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_date', models.DateTimeField(auto_now=True, null=True)),
                ('expiration_time', models.DateTimeField()),
                ('code', models.CharField(max_length=20)),
                ('send_attempts', models.IntegerField(default=1)),
                ('last_send_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('used_for_choices', models.CharField(choices=[('0', 'Used for Login'), ('1', 'Used for phone update')], default='0', max_length=2)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='one_time_passwords', related_query_name='one_time_passwords', to='users.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='CustomerOneTimePasswords',
        ),
    ]
