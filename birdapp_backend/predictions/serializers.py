"""
Filename: serializers.py
Author: Oliver Lovatt
Date: 23-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 23-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
"""
from rest_framework import serializers
from .models import Prediction, DatasetVersion

# [STUDENT-WRITTEN] - skeleton made by [Claude AI 23-07-2026]

#used by the /export/ endpoint - one row per prediction, with the
#species name and grid cell coordinates flattened in directly so the
#frontend doesn't need to do its own joins on the cached data
class PredictionExportSerializer(serializers.ModelSerializer):
    species = serializers.CharField(source = "species.common_name")
    lat_centre = serializers.FloatField(source = "grid_cell.lat_centre")
    lon_centre = serializers.FloatField(source = "grid_cell.lon_centre")
    cell_radius_km = serializers.FloatField(source = "grid_cell.cell_radius_km")

    class Meta:
        model = Prediction
        fields = [
            "species",
            "lat_centre",
            "lon_centre",
            "cell_radius_km",
            "season",
            "likelihood_score",
            "sample_checklists",
            "detections",
        ]


#used by the /version/ endpoint - just enough for the frontend to decide
#whether it needs to re-download the full export
class DatasetVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetVersion
        fields = ["generated_at", "row_count"]
