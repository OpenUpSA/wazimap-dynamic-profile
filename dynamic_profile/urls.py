from django.urls import path
from . import views

urlpatterns = [
    path("profiles", views.ProfileView.as_view(), name="api_profiles"),
    path("indicators", views.IndicatorProfileView.as_view(), name="api_indicators"),
    path("geography", views.GeographyView.as_view(), name="api_geography"),
    path(
        "geography/<geo_level>-<geo_code>",
        views.GeographyProfileView.as_view(),
        name="api_geography_profile",
    ),
]
