# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from wazimap.models import FieldTable
from django.contrib.postgres.fields import HStoreField, ArrayField

# Create your models here.


class Profile(models.Model):
    name = models.CharField(max_length=20)
    display_order = models.IntegerField(default=1)
    geo_level = ArrayField(
        models.CharField(max_length=20),
        default=[
            "country",
            "province",
            "district",
            "municipality",
            "ward",
            "subplace",
            "smallarea",
        ],
    )

    def __str__(self):
        return self.name


class IndicatorProfile(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    table_name = models.ForeignKey(FieldTable, on_delete=models.CASCADE)
    field_name = models.CharField(
        max_length=50, null=True, help_text="column names from the field table"
    )
    title = models.CharField(max_length=30, help_text="name of indicator")
    summary = models.CharField(
        max_length=100, help_text="description of the main value"
    )
    chart_title = models.CharField(max_length=100)
    chart_type = models.CharField(max_length=20, default="histogram")
    chart_design = models.CharField(max_length=25, default="half-width")
    order_by = models.CharField(max_length=10, default="-total", blank=True, null=True)
    exclude_zero = models.BooleanField(default=False, help_text="leave out 0 values")
    percent = models.BooleanField(default=True)
    recode = HStoreField(
        null=True,
        blank=True,
        help_text="group values according to cetain values eg: {'R1026 - R2499':'R1k - R2.5k}",
    )
    key_order = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    exclude = ArrayField(models.CharField(max_length=20), null=True, blank=True)
    display_order = models.IntegerField(default=1)
    parent_profile = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    group_remainder = models.IntegerField(
        default=20,
        null=True,
        blank=True,
        help_text="Eg: only show top 4 languages and group the rest as other",
    )
    info = models.TextField(
        null=True,
        blank=True,
        help_text="Any details thats must be know about the dataset such as how indicators were calculated",
    )
    dataset_context = models.IntegerField(
        blank=True,
        null=True,
        help_text="if the dataset is outside of the census and comminuty survey datasets addd a custom date for the dataset ",
    )
    distribution_total = models.BooleanField(
        default=False, help_text="Show the distribution total as part of the headers"
    )
    active = models.BooleanField(
        default=True, help_text="Should the this indicator be shown or not"
    )
    geo_level = ArrayField(
        models.CharField(max_length=20),
        default=[
            "country",
            "province",
            "district",
            "municipality",
            "ward",
            "subplace",
            "smallarea",
        ],
    )

    def __str__(self):
        return self.title
