"""
- loads predictions.csv into the database for the endpoint to have something to compare against
- existing Prediction/GridCell/Species/DatasetVersion rows are cleared, then reloaded from the CSV. Fulll refresh
- matches build_predictions.py works so re-running this command after a new predictions.csv is always safe

Filename: load_predictions.py
Author: Oliver Lovatt
Date: 23-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 23-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""

import math
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from predictions.models import Species, GridCell, Prediction, DatasetVersion

# [STUDENT-WRITTEN]
#match build_predictions
CELL_KM = 15
REFERENCE_LAT = 56.5
KM_PER_DEG_LAT = 111.0
KM_PER_DEG_LON = 111.0 * math.cos(math.radians(REFERENCE_LAT)) # [AI-GENERATED - Claude AI 23-07-2026]
LAT_BIN_SIZE = CELL_KM / KM_PER_DEG_LAT
LON_BIN_SIZE = CELL_KM / KM_PER_DEG_LON

MIGRATORY_SPECIES = {
    "Osprey", "Common Cuckoo", "Barn Swallow", "Arctic Tern", "Atlantic Puffin",
}
RESIDENT_SPECIES = {
    "Crested Tit", "Rock Ptarmigan", "Red Kite", "Red Grouse", "White-tailed Eagle",
}

# [STUDENT-WRITTEN]
#scientific names verified directly against the EBD file SCIENTIFIC NAME column 
#Red Grouse differed from the common subspecies name
SCIENTIFIC_NAMES = {
    "Osprey": "Pandion haliaetus",
    "Common Cuckoo": "Cuculus canorus",
    "Barn Swallow": "Hirundo rustica",
    "Arctic Tern": "Sterna paradisaea",
    "Atlantic Puffin": "Fratercula arctica",
    "Crested Tit": "Lophophanes cristatus",
    "Rock Ptarmigan": "Lagopus muta",
    "Red Kite": "Milvus milvus",
    "Red Grouse": "Lagopus scotica",
    "White-tailed Eagle": "Haliaeetus albicilla",
}

# [STUDENT-WRITTEN]
class Command(BaseCommand):
    help = "Load predictions.csv into the database (full refresh)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        df = pd.read_csv(csv_path)
        self.stdout.write(f"read {len(df):,} rows from {csv_path}")

        with transaction.atomic():
            #full refresh, clears old data first
            Prediction.objects.all().delete()
            GridCell.objects.all().delete()
            Species.objects.all().delete()
            DatasetVersion.objects.all().delete()

            #species
            species_lookup = {}
            for name in df["species"].unique():
                status = "Migratory" if name in MIGRATORY_SPECIES else "Resident"
                species_obj = Species.objects.create(
                    common_name=name,
                    scientific_name=SCIENTIFIC_NAMES.get(name, ""),
                    migratory_status=status,
                )
                species_lookup[name] = species_obj
            self.stdout.write(f"created {len(species_lookup)} species")

            #grid cells
            unique_cells = df[["lat_centre", "lon_centre", "cell_radius_km"]].drop_duplicates()
            cell_lookup = {}
            for row in unique_cells.itertuples(index=False):
                #reverse the centre formula to recover the integer grid index
                lat_idx = round(row.lat_centre / LAT_BIN_SIZE - 0.5)
                lon_idx = round(row.lon_centre / LON_BIN_SIZE - 0.5)
                cell_obj = GridCell.objects.create(
                    lat_idx=lat_idx,
                    lon_idx=lon_idx,
                    lat_centre=row.lat_centre,
                    lon_centre=row.lon_centre,
                    cell_radius_km=row.cell_radius_km,
                )
                # [AI-GENERATED - Claude AI 23-07-2026]
                cell_lookup[(row.lat_centre, row.lon_centre)] = cell_obj
            self.stdout.write(f"created {len(cell_lookup)} grid cells")

            # [STUDENT-WRITTEN]
            #predictions 
            prediction_objs = []
            for row in df.itertuples(index=False):
                species_obj = species_lookup[row.species]
                cell_obj = cell_lookup[(row.lat_centre, row.lon_centre)]
                prediction_objs.append(Prediction(
                    species=species_obj,
                    grid_cell=cell_obj,
                    season=row.season,
                    likelihood_score=row.likelihood_score,
                    sample_checklists=row.sample_checklists,
                    detections=row.detections,
                ))
            # [AI-GENERATED - Claude AI 23-07-2026]
            Prediction.objects.bulk_create(prediction_objs)
            self.stdout.write(f"created {len(prediction_objs)} predictions")

            # [AI-GENERATED - Claude AI 23-07-2026]
            #dataset version, for the /version/ endpoint to check against
            DatasetVersion.objects.create(
                generated_at=timezone.now(),
                row_count=len(prediction_objs),
            )
            self.stdout.write("recorded new dataset version")

        self.stdout.write(self.style.SUCCESS("done"))
