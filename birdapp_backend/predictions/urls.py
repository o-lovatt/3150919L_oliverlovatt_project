from django.urls import path
from .views import VersionView, PredictionExportView

urlpatterns = [
    path("version/", VersionView.as_view(), name = "version"),
    path("predictions/export/", PredictionExportView.as_view(), name = "predictions-export"),
]
