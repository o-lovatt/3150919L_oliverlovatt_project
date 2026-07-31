"""
Filename: models.py
Author: Oliver Lovatt
Date: 21-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 21-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
"""

from django.db import models

# Create your models here.
from django.db import models

# [STUDENT-WRITTEN]
#store species
class Species(models.Model):
    common_name = models.CharField(max_length = 100, unique = True)
    scientific_name = models.CharField(max_length = 100, blank = True) #blank so scientific name isn't needed
    migratory_status = models.CharField(max_length = 20, choices = [("Migratory", "Migratory"), ("Resident", "Resident/Partial Resident")])
    
    def __str__(self):
        return self.common_name

# [STUDENT-WRITTEN]
#store lat/lon coordinates
class GridCell(models.Model):
    lat_idx = models.IntegerField() #needs to be int for grid cell
    lon_idx = models.IntegerField() 
    lat_centre = models.FloatField()
    lon_centre = models.FloatField()
    cell_radius_km = models.FloatField()
    # [AI-GENERATED - Claude AI 21-07-2026]
    class Meta: 
        unique_together = ("lat_idx", "lon_idx") #no two rows can share this combination of values
    # [STUDENT-WRITTEN]
    def __str__(self):
        return (f"Grid cell: {self.lat_centre}, {self.lon_centre}")

# [STUDENT-WRITTEN]
#store prediction variables
class Prediction(models.Model):
    species = models.ForeignKey(Species, on_delete = models.CASCADE)
    grid_cell = models.ForeignKey(GridCell, on_delete = models.CASCADE)
    season = models.CharField(max_length = 10, choices = [
        #(stored value, displayed value)
        ("Spring", "Spring"), ("Summer", "Summer"), ("Autumn", "Autumn"), ("Winter", "Winter")
        ])
    likelihood_score = models.FloatField()
    sample_checklists = models.IntegerField()
    detections = models.IntegerField()
    # [AI-GENERATED - Claude AI 21-07-2026]
    class Meta: 
        unique_together = ("species", "grid_cell", "season")
    # [STUDENT-WRITTEN]
    def __str__(self):
        return (f"Species: {self.species.common_name} \nCell: {self.grid_cell} \nSeason: {self.season}")


# [STUDENT-WRITTEN]
#check when the prediction data get's updated
class DatasetVersion(models.Model): 
    generated_at = models.DateTimeField()
    row_count = models.IntegerField()
