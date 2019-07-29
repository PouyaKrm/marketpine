# Generated by Django 2.2 on 2019-07-28 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FriendInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invitation_date', models.DateField(auto_now_add=True)),
                ('new', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'friend_invitation',
            },
        ),
        migrations.CreateModel(
            name='FriendInvitationDiscount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_code', models.CharField(max_length=9)),
                ('role', models.CharField(choices=[('IR', 'Inviter'), ('ID', 'Invited')], max_length=2)),
            ],
            options={
                'db_table': 'friend_invitation_discount',
            },
        ),
    ]
