# Generated by Django 2.2 on 2019-07-31 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivals', '0003_festival_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='festival',
            name='message',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
