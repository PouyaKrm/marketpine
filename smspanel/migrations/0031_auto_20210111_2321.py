# Generated by Django 2.2 on 2021-01-11 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smspanel', '0030_welcomemessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentsms',
            name='cost',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='sentsms',
            name='date',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='sentsms',
            name='sender',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='sentsms',
            name='status',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sentsms',
            name='receptor',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
