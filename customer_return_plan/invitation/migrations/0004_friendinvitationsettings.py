# Generated by Django 2.2 on 2020-03-17 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0003_friendinvitationdiscount_used'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendInvitationSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_template', models.CharField(max_length=600)),
                ('discount_type', models.CharField(choices=[('Percent', '0'), ('Flat rate', '1')], default='0', max_length=2)),
                ('percent_off', models.FloatField(default=0)),
                ('flat_rate_off', models.PositiveIntegerField(default=0)),
                ('disabled', models.BooleanField(default=False)),
            ],
        ),
    ]