# Generated by Django 2.2 on 2021-02-14 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content_marketing', '0014_auto_20210214_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comments', related_query_name='post_comments', to='users.Customer'),
        ),
    ]
