# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django import forms
from .models import Profile, IndicatorProfile

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order")


admin.site.register(Profile, ProfileAdmin)


class IndicatorProfileForm(forms.ModelForm):
    CHART_CHOICES = (("histogram", "Histogram"), ("pie", "Pie"))
    MAX_VALUE_CHOICES = (("Total", "Total"), ("Distribution", "Distribution"))
    DISPLAY_CHOICES = ((1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"))
    DESIGN_CHOICES = (("full-width", "Full-Width"), ("half-width", "Half-Width"))
    HEADER_CHOICES = (
        ("", "----------"),
        ("distribution_total", "Distribution Total"),
        ("highest_percent", "Highest Percent"),
        ("highest_category", "Highest Category"),
    )
    chart_type = forms.ChoiceField(choices=CHART_CHOICES)
    chart_design = forms.ChoiceField(choices=DESIGN_CHOICES)
    display_order = forms.ChoiceField(choices=DISPLAY_CHOICES)
    header_result = forms.ChoiceField(choices=HEADER_CHOICES, required=False)

    def clean(self):
        cleaned_data = super().clean()

        order_by = cleaned_data.get("order_by")
        key_order = cleaned_data.get("key_order")
        header_result = cleaned_data.get("header_result")
        header_field = cleaned_data.get("header_field")
        if order_by and key_order:
            raise forms.ValidationError("Cant set key_order with order_by")
        if header_result == "highest_percent" and not header_field:
            raise forms.ValidationError(
                "You have to enter the field name that should be displayed"
            )


class IndicatorProfileAdmin(admin.ModelAdmin):
    form = IndicatorProfileForm
    list_display = ("title", "profile", "active", "display_order")
    list_filter = ("profile", "active")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "profile",
                    "active",
                    "dataset_context",
                    "geo_level",
                    "display_order",
                    "parent_profile",
                )
            },
        ),
        ("DataSource", {"fields": ("table_name", "field_name")}),
        (
            "Header",
            {"fields": ("title", "summary", "info", "header_result", "header_field")},
        ),
        ("Charts", {"fields": ("chart_title", "chart_design", "chart_type")}),
        (
            "Calculation",
            {
                "fields": (
                    "order_by",
                    "exclude_zero",
                    "percent",
                    "recode",
                    "key_order",
                    "exclude",
                    "group_remainder",
                )
            },
        ),
    )


admin.site.register(IndicatorProfile, IndicatorProfileAdmin)
