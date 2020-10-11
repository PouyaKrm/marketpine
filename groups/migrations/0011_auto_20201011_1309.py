# Generated by Django 2.2 on 2020-10-11 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0010_auto_20201011_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_query_name='membership', to='users.Customer'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_query_name='membership', to='groups.BusinessmanGroups'),
        ),
    ]