import importlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from wazimap.models import Geography
from .models import Profile, IndicatorProfile
from .serializer import (
    ProfileSerializer,
    IndicatorProfileSerializer,
    GeographySerializer,
)
from wazimap.data.utils import dataset_context
from wazimap.geo import geo_data
from wazimap.data.utils import get_session
from .utils import Section, BuildProfile, BuildIndicator


class GeographyView(APIView):
    """
    Show a list of all the geographies
    """

    def get(self, request):
        query = Geography.objects.all().distinct()
        serilize = GeographySerializer(query, many=True)
        return Response({"results": serilize.data}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    show all the avaliable dynamic profiles
    """

    def get(self, request):
        query = Profile.objects.all()
        serialize = ProfileSerializer(query, many=True)
        return Response({"results": serialize.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serialize = ProfileSerializer(data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)


class IndicatorProfileView(APIView):
    """
    show all the avaliable indicators
    """

    def get(self, request):
        query = IndicatorProfile.objects.all()
        serialize = IndicatorProfileSerializer(query, many=True)
        return Response({"results": serialize.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serialize = IndicatorProfileSerializer(data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)


class GeographyProfileView(APIView):
    """
    Get the profile for a particular geography
    """

    def get(self, request, geo_level, geo_code):
        results = {}
        version = self.request.GET.get(
            "geo_version", settings.WAZIMAP["default_geo_version"]
        )

        geography = Geography.objects.get(
            geo_level=geo_level, geo_code=geo_code, version=version
        )
        year = self.request.GET.get("release", geo_data.primary_release_year(geography))
        results["geograhy"] = geography.as_dict_deep()

        if settings.WAZIMAP["latest_release_year"] == year:
            year = "latest"

        build_indicator = settings.DYNAMIC_PROFILE_INDICATOR
        if build_indicator:
            module = importlib.import_module(build_indicator["path"])
            build_indicator = getattr(module, build_indicator["class"])
        else:
            build_indicator = BuildIndicator

        session = get_session()
        with dataset_context(year=year):
            section = Section(geography, session)
            section_results = section.build(BuildProfile, build_indicator)
            results["data"] = section_results

        return Response(results, status=status.HTTP_200_OK)
