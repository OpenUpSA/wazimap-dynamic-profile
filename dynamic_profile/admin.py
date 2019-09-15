# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django import forms
from .models import Profile, IndicatorProfile

# Register your models here.

admin.site.register(Profile)


class IndicatorProfileForm(forms.ModelForm):
    CHART_CHOICES = (("histogram", "Histogram"), ("pie", "Pie"))
    MAX_VALUE_CHOICES = (("Total", "Total"), ("Distribution", "Distribution"))
    DISPLAY_CHOICES = ((1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"))
    chart_type = forms.ChoiceField(choices=CHART_CHOICES)
    display_order = forms.ChoiceField(choices=DISPLAY_CHOICES)


class IndicatorProfileAdmin(admin.ModelAdmin):
    form = IndicatorProfileForm


admin.site.register(IndicatorProfile, IndicatorProfileAdmin)
