"""
eBird EBD prediction table aggregation script

builds effort-standardized encounter rates per (species, grid cell, season)

- deduplicate to checklist level 
- apply caps so only comparable checklists count (duration <= 300 min, distance <= 10 km, observers <= 10)
- assign each qualifying checklist to a 15km grid cell + season
- likelihood_score = detections / total qualifying checklists in that cell+season

Filename: build_predictions.py
Author: Oliver Lovatt
Date: 22-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 18-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""

import sys
import pandas as pd
import numpy as np

# [STUDENT-WRITTEN]
CHUNK_SIZE = 100_000

SHORTLIST = [
    "Osprey",
    "Common Cuckoo",
    "Barn Swallow",
    "Arctic Tern",
    "Atlantic Puffin",
    "Crested Tit",
    "Rock Ptarmigan",
    "Red Kite",
    "White-tailed Eagle",
    "Red Grouse",
]

#effort-standardization constants
MAX_DURATION_MIN = 300  #5 hours
MAX_DISTANCE_KM = 10
MAX_OBSERVERS = 10

#grid cell size
CELL_KM = 15
REFERENCE_LAT = 56.5  #mid-Scotland latitude same as grid_resolution_check
KM_PER_DEG_LAT = 111.0
KM_PER_DEG_LON = 111.0 * np.cos(np.radians(REFERENCE_LAT)) # [AI-GENERATED - Claude AI 18-07-2026]
LAT_BIN_SIZE = CELL_KM / KM_PER_DEG_LAT
LON_BIN_SIZE = CELL_KM / KM_PER_DEG_LON


MONTH_TO_SEASON = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}

#two separate lists needed
CHECKLIST_COLS = [
    "SAMPLING EVENT IDENTIFIER",
    "LATITUDE",
    "LONGITUDE",
    "OBSERVATION DATE",
    "DURATION MINUTES",
    "EFFORT DISTANCE KM",
    "NUMBER OBSERVERS",
]

SPECIES_COLS = ["SAMPLING EVENT IDENTIFIER", "COMMON NAME"]


#converts lat/lon coords to grid cell index 
def assign_grid_cell(lat, lon):
    #convert to integer needed as these numbers will be used as lookup keys later
    lat_idx = np.floor(lat / LAT_BIN_SIZE).astype(int)
    lon_idx = np.floor(lon / LON_BIN_SIZE).astype(int)
    return lat_idx, lon_idx

#converts grid cell index back to lat/lon centre point 
#reverse operation so prediction table can store a coordinate instead of an index
def cell_centre(lat_idx, lon_idx):
    #0.5 puts it directly in the centre point 
    lat_centre = (lat_idx + 0.5) * LAT_BIN_SIZE 
    lon_centre = (lon_idx + 0.5) * LON_BIN_SIZE
    return lat_centre, lon_centre


def load_checklists(path):
    #read only the checklist-level columns
    #dedup down to one row per checklist
    #effort/season/location 
    rows = []
    total_read = 0

    for chunk in pd.read_csv(
        path,
        sep = "\t",
        usecols = CHECKLIST_COLS,
        dtype = str,
        chunksize = CHUNK_SIZE,
    ):
        # [AI-GENERATED - Claude AI 18-07-2026]
        chunk = chunk.drop_duplicates(subset = "SAMPLING EVENT IDENTIFIER")
        rows.append(chunk)
        total_read += len(chunk)
        if total_read % 1_000_000 < CHUNK_SIZE:
            print(f"pass 1: processed {total_read:,} rows")

    # [STUDENT-WRITTEN]
    checklists = pd.concat(rows, ignore_index = True)
    #if a checklist appears in more than one chunk boundary
    #dedup again across the full set
    #combines all chunks to one DF
    checklists = checklists.drop_duplicates(subset = "SAMPLING EVENT IDENTIFIER")

    #convert types
    checklists["LATITUDE"] = pd.to_numeric(checklists["LATITUDE"], errors = "coerce")
    checklists["LONGITUDE"] = pd.to_numeric(checklists["LONGITUDE"], errors = "coerce")
    checklists["DURATION MINUTES"] = pd.to_numeric(checklists["DURATION MINUTES"], errors = "coerce")
    #stationary distance is always 0, interpret blank distance as 0
    checklists["EFFORT DISTANCE KM"] = pd.to_numeric(checklists["EFFORT DISTANCE KM"], errors = "coerce").fillna(0)
    checklists["NUMBER OBSERVERS"] = pd.to_numeric(checklists["NUMBER OBSERVERS"], errors = "coerce")

    #same date/season conversion like grid_resolution_check
    dt = pd.to_datetime(checklists["OBSERVATION DATE"], errors = "coerce")
    checklists["SEASON"] = dt.dt.month.map(MONTH_TO_SEASON)

    #store results as two nex columns
    lat_idx, lon_idx = assign_grid_cell(checklists["LATITUDE"], checklists["LONGITUDE"])
    checklists["LAT_IDX"] = lat_idx
    checklists["LON_IDX"] = lon_idx

    # [STUDENT-WRITTEN]
    #checklist will only qualify is it meets these conditions:
    #valid duration, distance, observer count, season & coordinates
    #don't dedup
    checklists["QUALIFIES"] = (
        checklists["DURATION MINUTES"].notna()
        & (checklists["DURATION MINUTES"] <= MAX_DURATION_MIN)
        & (checklists["EFFORT DISTANCE KM"] <= MAX_DISTANCE_KM)
        & checklists["NUMBER OBSERVERS"].notna()
        & (checklists["NUMBER OBSERVERS"] <= MAX_OBSERVERS)
        & checklists["SEASON"].notna()
        & checklists["LATITUDE"].notna()
        & checklists["LONGITUDE"].notna()
    )

    # [AI-GENERATED - Claude AI 18-07-2026]
    #returns all checklists valid or not
    print(f"\n{len(checklists):,} unique checklists total, "
          f"{checklists['QUALIFIES'].sum():,} qualify after effort caps\n")
    return checklists

# [STUDENT-WRITTEN]
def load_species_rows(path):
    #read only shortlist species rows
    #one row per species
    #second pass needs to read sampling ID and common name rows
    rows = []
    total_read = 0

    for chunk in pd.read_csv(
        path,
        sep = "\t",
        usecols = SPECIES_COLS,
        dtype = str,
        chunksize = CHUNK_SIZE,
    ):
        chunk = chunk[chunk["COMMON NAME"].isin(SHORTLIST)]
        rows.append(chunk)

        # [AI-GENERATED - Claude AI 18-07-2026]
        total_read += len(chunk)
        if total_read % 1_000_000 < CHUNK_SIZE:
            print(f"pass 2: processed ~{total_read:,} rows")

    # [STUDENT-WRITTEN]
    #combine all filtered chunks into one DF
    #deduplicate on both columns sampling id and common name here
    species_df = pd.concat(rows, ignore_index = True)
    #species should only appear once per checklist
    species_df = species_df.drop_duplicates(subset = ["SAMPLING EVENT IDENTIFIER", "COMMON NAME"])
    return species_df


def main(in_path, out_path):
    # [STUDENT-WRITTEN]
    #call both previous functions
    checklists = load_checklists(in_path)
    species_df = load_species_rows(in_path)

    #total qualifying checklists per cell & season 
    qualifying = checklists[checklists["QUALIFIES"]].copy() #.copy() make a fully indpendant table

    # [AI-GENERATED - Claude AI 18-07-2026]
    #this pairs values by position
    qualifying["CELL"] = list(zip(qualifying["LAT_IDX"], qualifying["LON_IDX"]))
    #list converts zip object to a tuple so it can be assigned to a column 

    # [STUDENT-WRITTEN]
    #total qualifying checklists (cell, season)
    #what likelihood score will be divided by 
    totals = (
        qualifying.groupby(["CELL", "SEASON"])["SAMPLING EVENT IDENTIFIER"]
        .nunique()
        .reset_index(name = "SAMPLE_CHECKLISTS")
    )

    #attach cell + season + qualifies onto each species row, keep qualifying only
    #reorganise qualifying checklists table, set index to be the sampling id
    #keep only cell + season columns
    lookup = qualifying.set_index("SAMPLING EVENT IDENTIFIER")[["CELL", "SEASON"]] 
    #find and join rows with sampling ID to cell and season columns 
    species_df = species_df.join(lookup, on = "SAMPLING EVENT IDENTIFIER")
    #drop species detection from nonqualifying checklists
    species_df = species_df.dropna(subset = ["CELL", "SEASON"])

    #species detections (species, cell, season)
    #what will divide likelihood score 
    detections = (
        species_df.groupby(["COMMON NAME", "CELL", "SEASON"])["SAMPLING EVENT IDENTIFIER"]
        .nunique()
        .reset_index(name = "DETECTIONS")
    )

    #merge totals and detection tables
    #keep every row from detections and attack matching totals 
    merged = detections.merge(totals, on = ["CELL", "SEASON"], how = "left")
    #encounter rate calc
    merged["likelihood_score"] = (merged["DETECTIONS"] / merged["SAMPLE_CHECKLISTS"]).round(4) #rounded to four decimal places

    # [AI-GENERATED - Claude AI 18-07-2026]
    # unpack cell tuple back into lat/lon centre
    #reverses earlier zip -> list step, need two numbers separate 
    lat_idx = merged["CELL"].apply(lambda c: c[0])
    lon_idx = merged["CELL"].apply(lambda c: c[1])
    #convert two numbers into lat/lon coordinate 
    lat_centre, lon_centre = cell_centre(lat_idx, lon_idx)

    # [STUDENT-WRITTEN]
    #final output table 
    out_df = pd.DataFrame({
        "species": merged["COMMON NAME"],
        "lat_centre": lat_centre.round(5),
        "lon_centre": lon_centre.round(5),
        "cell_radius_km": CELL_KM / 2,
        "season": merged["SEASON"],
        "likelihood_score": merged["likelihood_score"],
        "sample_checklists": merged["SAMPLE_CHECKLISTS"],
        "detections": merged["DETECTIONS"],
    })


    #sort final table 
    #write to csv
    out_df = out_df.sort_values(["species", "season", "lat_centre", "lon_centre"])
    out_df.to_csv(out_path, index = False)

    # [AI-GENERATED - Claude AI 18-07-2026]
    #final summary printing
    print(f"\nDONE")
    print(f"Prediction rows written: {len(out_df):,}")
    print(f"Output: {out_path}")
    print("\nROWS PER SPECIES")
    print(out_df["species"].value_counts().to_string())
    print("\nSAMPLE_CHECKLISTS DISTRIBUTION (per row)")
    print(out_df["sample_checklists"].describe().to_string())


# [AI-GENERATED - Claude AI 18-07-2026]
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python build_predictions.py path/to/ebd_GB-SCT_filtered.txt path/to/predictions.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
