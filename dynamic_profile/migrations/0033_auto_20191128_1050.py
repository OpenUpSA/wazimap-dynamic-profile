# Generated by Django 2.2.6 on 2019-11-28 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_profile', '0032_auto_20191128_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorprofile',
            name='header_field',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='indicatorprofile',
            name='header_result',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]
