# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from wazimap.models import FieldTable
from django.contrib.postgres.fields import HStoreField, ArrayField

# Create your models here.


class Profile(models.Model):
    name = models.CharField(max_length=20)
    display_order = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class IndicatorProfile(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    table_name = models.ForeignKey(FieldTable, on_delete=models.CASCADE)
    universe = models.CharField(max_length=50, default="Population")
    field_name = models.CharField(max_length=50, null=True)
    title = models.CharField(max_length=30)
    summary = models.CharField(max_length=100)
    chart_title = models.CharField(max_length=100)
    chart_type = models.CharField(max_length=20, default="histogram")
    order_by = models.CharField(max_length=10, default="-total")
    exclude_zero = models.BooleanField(default=False)
    percent = models.BooleanField(default=True)
    recode = HStoreField(null=True, blank=True)
    key_order = ArrayField(models.CharField(max_length=20), null=True, blank=True)
    exclude = ArrayField(models.CharField(max_length=20), null=True, blank=True)
    display_order = models.IntegerField(default=1)
    parent_profile = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    group_remainder = models.IntegerField(default=20, null=True, blank=True)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
