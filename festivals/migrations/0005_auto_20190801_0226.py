# Generated by Django 2.2 on 2019-07-31 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivals', '0004_auto_20190731_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='festival',
            name='message',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
