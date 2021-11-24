# Generated by Django 2.2 on 2021-11-03 14:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('smspanel', '0035_auto_20211008_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smsmessage',
            name='used_for',
            field=models.CharField(
                choices=[('0', 'NONE'), ('1', 'FESTIVAL'), ('2', 'CONTENT MARKETING'), ('3', 'INSTAGRAM MARKETING'),
                         ('4', 'WELCOME MESSAGE'), ('5', 'FRIEND INVITATION'), ('7', 'SEND TO GROUP'),
                         ('6', 'SEND TO ALL')], default='0', max_length=2),
        ),
    ]
