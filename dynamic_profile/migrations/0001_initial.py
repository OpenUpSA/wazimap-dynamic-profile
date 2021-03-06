# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-08 07:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wazimap', '0012_auto_20190111_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column_name', models.CharField(max_length=50, null=True)),
                ('header', models.CharField(max_length=30)),
                ('summary', models.CharField(max_length=100)),
                ('chart_title', models.CharField(max_length=100)),
                ('chart_type', models.CharField(default='histogram', max_length=20)),
                ('order_by', models.BooleanField(default=False)),
                ('exclude_zero', models.BooleanField(default=False)),
                ('percent', models.BooleanField(default=False)),
                ('maximum_value', models.CharField(default='distribution', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Profiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='indicatorprofile',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dynamic_profile.Profiles'),
        ),
        migrations.AddField(
            model_name='indicatorprofile',
            name='table_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wazimap.FieldTable'),
        ),
    ]
