from rest_framework import serializers
from .models import Profile, IndicatorProfile
from wazimap.models import Geography


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class IndicatorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorProfile
        fields = "__all__"


class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geography
        fields = "__all__"
