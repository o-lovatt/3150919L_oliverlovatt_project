"""
Filename: views.py
Author: Oliver Lovatt
Date: 23-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 23-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Prediction, DatasetVersion
from .serializers import PredictionExportSerializer, DatasetVersionSerializer
import requests
import os

# [AI-GENERATED - Claude AI 23-07-2026]
#GET /api/version/
#tiny endpoint - the frontend calls this on app open (at most once per
#24h) to check whether it needs to re-download the full export
class VersionView(APIView):
    def get(self, request):
        version = DatasetVersion.objects.order_by("-generated_at").first()
        if version is None:
            return Response({"generated_at": None, "row_count": 0})
        serializer = DatasetVersionSerializer(version)
        return Response(serializer.data)

# [AI-GENERATED - Claude AI 23-07-2026]
#GET /api/predictions/export/
#returns the full prediction table as JSON - this is what gets cached
#locally on the phone so the app can answer every prediction query
#offline, with no per-query network calls
class PredictionExportView(APIView):
    def get(self, request):
        predictions = Prediction.objects.select_related("species", "grid_cell").all()
        serializer = PredictionExportSerializer(predictions, many = True)
        return Response(serializer.data)

# [STUDENT WRITTEN]
#get lat/lon from incoming request 
#build parameter dict
#build headers dict
EBIRD_RECENT_URL = "https://api.ebird.org/v2/data/obs/geo/recent"
class RecentSightingsView(APIView):
    def get(self, request):
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        params_dict = {"lat": lat, "lng": lon, "back": 7} #(7 days to look back at)
        headers_dict = {"X-eBirdApiToken": os.getenv("EBIRD_API_KEY")}

        response = requests.get(EBIRD_RECENT_URL, params=params_dict, headers=headers_dict)

        if response.status_code != 200:
            return Response({"error": "Could not fetch recent sightings"}, status=502)
        return Response(response.json())

# [STUDENT WRITTEN]
class SpeciesRecentSightingsView(APIView):
    def get(self, request):
        species_code = request.GET.get("species_code")
        url = f"https://api.ebird.org/v2/data/obs/GB-SCT/recent/{species_code}"
        headers = {"X-eBirdApiToken": os.getenv("EBIRD_API_KEY")}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Could not fetch species sightings"}, status=502)

        return Response(response.json())