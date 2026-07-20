"""
grid_resolution_check.py

checks how sparse the species x grid-cell x time-bucket combinations
are, across a few candidate grid resolutions AND a few candidate time
resolutions (week / month / season) 

Filename: grid_resolution_check.py
Author: Oliver Lovatt
Date: 20-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 14-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
"""

import pandas as pd
import numpy as np

# [STUDENT-WRITTEN]
#config
INPUT_FILE = "ebd_GB-SCT_filtered.txt"
CHUNK_SIZE = 250_000
MIN_CHECKLISTS = 5  #threshold for 'too sparse to be trustworthy'

CANDIDATE_RESOLUTIONS_KM = [10, 15, 20]
CANDIDATE_TIME_RESOLUTIONS = ["week", "month", "season"]

# [STUDENT-WRITTEN]
SHORTLIST_SPECIES = [
    "Osprey",
    "Common Cuckoo",
    "Barn Swallow",
    "Arctic Tern",
    "Atlantic Puffin",
    "Crested Tit",
    "Rock Ptarmigan",
    "Red Kite",
    "Red Grouse",
    "White-tailed Eagle",
]

USECOLS = [
    "COMMON NAME",
    "SAMPLING EVENT IDENTIFIER",
    "LATITUDE",
    "LONGITUDE",
    "OBSERVATION DATE",
]

# [STUDENT-WRITTEN]
#dictionary to map month numbers to season names
MONTH_TO_SEASON = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}
TIME_COLUMN_NAMES = {"week": "WEEK", "month": "MONTH", "season": "SEASON"}


# [STUDENT-WRITTEN]
#helpers
#takes dataframe in, added 3 new columns and returns
def add_time_columns(df):
    #convert to datetime
    dt = pd.to_datetime(df["OBSERVATION DATE"], errors = "coerce")
    df["WEEK"] = dt.dt.isocalendar().week.astype("Int64")#built in week number calculator (1 - 52)
    #good for if some dates fail to parse errors = "coerce"
    df["MONTH"] = dt.dt.month.astype("Int64")#extract month number 1 - 12
    df["SEASON"] = df["MONTH"].map(MONTH_TO_SEASON) #looks up value in month column and replaces with season name
    return df

# [AI-GENERATED - Claude AI 14-07-2026]
#converts lat/lon coords to grid cell ID
#1 degree of lat is roughly 111km, but 1 degree of lon shrinks the further away from the equator you get, as the lines move to one point towards the poles.
def assign_grid_cell(lat, lon, resolution_km):
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * np.cos(np.radians(56.5)) #mid-Scotland latitude, converts 56.5 degrees into radians

    #convert cell size into lat/lon degrees it corresponds too
    lat_bin_size = resolution_km / km_per_deg_lat
    lon_bin_size = resolution_km / km_per_deg_lon

    #divide lat by bin size "which bin am i in?"
    lat_idx = np.floor(lat / lat_bin_size).astype(int) #rounded down to a whole number
    lon_idx = np.floor(lon / lon_bin_size).astype(int)
    return lat_idx.astype(str) + "_" + lon_idx.astype(str)

# [STUDENT-WRITTEN]
#main
def main():
    print(f"Reading {INPUT_FILE} in chunks of {CHUNK_SIZE:,} rows...")

    rows = [] #collects filtered chunks
    total_read = 0

    for chunk in pd.read_csv(
        INPUT_FILE,
        sep = "\t",
        usecols = USECOLS,
        dtype = str,
        chunksize = CHUNK_SIZE,
    ):
        chunk = chunk[chunk["COMMON NAME"].isin(SHORTLIST_SPECIES)].copy()
        #.copy() used to make a fully independant copy

        #skip everything if chunk is empty
        #convert lat/lon to numbers
        #remove rows missing lat, lon or week
        if not chunk.empty:
            chunk["LATITUDE"] = pd.to_numeric(chunk["LATITUDE"], errors = "coerce")
            chunk["LONGITUDE"] = pd.to_numeric(chunk["LONGITUDE"], errors = "coerce")
            chunk = add_time_columns(chunk)
            chunk = chunk.dropna(subset=["LATITUDE", "LONGITUDE", "WEEK"])
            rows.append(chunk)

        total_read += len(chunk)
        if total_read % 1_000_000 < CHUNK_SIZE:
            print(f"processed {total_read:,} rows")
            #progress tracker

    #combine list of separate chunks back to one dataframe
    df = pd.concat(rows, ignore_index = True) #renumber rows 0 1 2....
    # [AI-GENERATED - Claude AI 14-07-2026]
    print(f"\nTotal shortlist-species rows kept: {len(df):,}\n")
    #safety check if no names match
    if df.empty:
        print("No rows matched SHORTLIST_SPECIES - check the COMMON NAME spellings against EBD file.")
        return


    # [STUDENT-WRITTEN]
    #main analysis loop
    #gives 9 combonations, 3 time resolutions x 3 spatial resolutions
    for time_res in CANDIDATE_TIME_RESOLUTIONS:
        time_col = TIME_COLUMN_NAMES[time_res]

        for res_km in CANDIDATE_RESOLUTIONS_KM:
            # [AI-GENERATED - Claude AI 14-07-2026]
            print(f"\nTime: {time_res:6s} | Space: {res_km}km cells")
            #call grid helper function to add a column
            df["CELL"] = assign_grid_cell(df["LATITUDE"], df["LONGITUDE"], res_km)

            # [STUDENT-WRITTEN]
            grouped = (
                #group rows by three columns (species, time, gird cell)
                df.groupby(["COMMON NAME", time_col, "CELL"])["SAMPLING EVENT IDENTIFIER"]
                .nunique() #count numbers of distinct checklist IDs
                .reset_index(name = "CHECKLIST_COUNT") #turn back to regular columns and name the new count column
            )

            #for each species, filter grouped results to that species rows
            for species in SHORTLIST_SPECIES:
                sub = grouped[grouped["COMMON NAME"] == species]
                #empty case handling
                # [AI-GENERATED - Claude AI 14-07-2026]
                if sub.empty:
                    print(f"  {species:24s}  NO DATA at this resolution")
                    continue
                # [STUDENT-WRITTEN]
                n_combos = len(sub) #distinct time bucket + cell combinations for this species
                n_sparse = (sub["CHECKLIST_COUNT"] < MIN_CHECKLISTS).sum()
                pct_sparse = 100 * n_sparse / n_combos
                # [AI-GENERATED - Claude AI 14-07-2026]
                print(
                    f"  {species:24s}  {n_combos:5d} cell-buckets populated, "
                    f"{pct_sparse:5.1f}% below {MIN_CHECKLISTS} checklists"
                )


if __name__ == "__main__":
    main()
