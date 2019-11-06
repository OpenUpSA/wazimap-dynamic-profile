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
    chart_type = forms.ChoiceField(choices=CHART_CHOICES)
    chart_design = forms.ChoiceField(choices=DESIGN_CHOICES)
    display_order = forms.ChoiceField(choices=DISPLAY_CHOICES)


class IndicatorProfileAdmin(admin.ModelAdmin):
    form = IndicatorProfileForm
    list_display = ("title", "profile", "active", "display_order")
    list_filter = ("profile", "active")


admin.site.register(IndicatorProfile, IndicatorProfileAdmin)
