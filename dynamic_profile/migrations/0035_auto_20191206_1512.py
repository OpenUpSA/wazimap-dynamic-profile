# Generated by Django 2.2.6 on 2019-12-06 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_profile', '0034_auto_20191206_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='display_order',
            field=models.IntegerField(default=1, unique=True),
        ),
    ]