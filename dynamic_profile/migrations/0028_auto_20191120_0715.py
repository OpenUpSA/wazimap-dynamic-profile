# Generated by Django 2.2.6 on 2019-11-20 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_profile', '0027_indicatorprofile_header_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorprofile',
            name='header_result',
            field=models.CharField(default='', max_length=20),
        ),
    ]
