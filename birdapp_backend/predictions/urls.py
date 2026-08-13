from django.urls import path
from .views import VersionView, PredictionExportView, RecentSightingsView

urlpatterns = [
    path("version/", VersionView.as_view(), name = "version"),
    path("predictions/export/", PredictionExportView.as_view(), name = "predictions-export"),
    path("recent-sightings/", RecentSightingsView.as_view(), name="recent-sightings"),
]
