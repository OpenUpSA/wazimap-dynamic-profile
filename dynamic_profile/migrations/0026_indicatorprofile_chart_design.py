# Generated by Django 2.2.6 on 2019-11-05 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_profile', '0025_profile_geo_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicatorprofile',
            name='chart_design',
            field=models.CharField(default='half-width', max_length=25),
        ),
    ]
