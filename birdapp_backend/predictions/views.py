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
