"""
trains one Random Forest classifier per shortlist species and compares it against the existing baseline

here I'm using a spatial split instead of a random split, eBird checklists are heavily clustered at popular hotspots,
and using a random split would mean the model memorises hotspot rates, rather than learning genuine location based patterns

the baseline has a k nearest neighbour fallback 

Filename: train_evaluate_model.py
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import roc_auc_score, brier_score_loss
from constants import (
    SHORTLIST, MAX_DURATION_MIN, MAX_DISTANCE_KM, MAX_OBSERVERS,
    CELL_KM, REFERENCE_LAT, KM_PER_DEG_LAT, KM_PER_DEG_LON,
    LAT_BIN_SIZE, LON_BIN_SIZE, MONTH_TO_SEASON, SEASONS,
)

from distance_features import add_distance_features

# [STUDENT-WRITTEN]
CHUNK_SIZE = 100_000
RANDOM_SEED = 42  #fixed so the train/test split and RF training are reproducible 

#moved to constants.py during refactoring

#separate 20% of data for testing
TEST_FRACTION = 0.2  

# [AI-GENERATED - Claude AI 18-07-2026]
# CalibratedClassifierCV needs enough positive examples in each training fold
# to work reliably - below this, cross-validated calibration gets unstable,
# so we fall back to the plain (uncalibrated) RF and note it in the output
CALIBRATION_MIN_TRAIN_POSITIVES = 30
CALIBRATION_CV_FOLDS = 3

# [STUDENT-WRITTEN]
#random forest settings
#minimum leaf size + shallow tree used as many species are sparse
RF_PARAMS = dict(
    n_estimators = 300,
    max_depth = 12,
    min_samples_leaf = 5,
    class_weight = "balanced",  #every species is rare relative to total checklists
    random_state = RANDOM_SEED,
    n_jobs = -1,
)

#moved to constants.py during refactoring

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


#same as build_predictions.py
def assign_grid_cell(lat, lon):
    #convert to integer needed as these numbers will be used as lookup keys later
    lat_idx = np.floor(lat / LAT_BIN_SIZE).astype(int)
    lon_idx = np.floor(lon / LON_BIN_SIZE).astype(int)
    return lat_idx, lon_idx

#same as build_predictions.py
def cell_centre(lat_idx, lon_idx):
    #0.5 puts it directly in the centre point 
    lat_centre = (lat_idx + 0.5) * LAT_BIN_SIZE
    lon_centre = (lon_idx + 0.5) * LON_BIN_SIZE
    return lat_centre, lon_centre


def load_checklists(path):
    #doesn't return all checklists 
    #filters to qualifying checklists before returning
    rows = []
    total_read = 0

    for chunk in pd.read_csv(
        path,
        sep = "\t",
        usecols = CHECKLIST_COLS,
        dtype = str,
        chunksize = CHUNK_SIZE,
    ):
        chunk = chunk.drop_duplicates(subset = "SAMPLING EVENT IDENTIFIER")
        rows.append(chunk)
        total_read += len(chunk)
        # [AI-GENERATED - Claude AI 18-07-2026]
        if total_read % 1_000_000 < CHUNK_SIZE:
            print(f"pass 1: processed {total_read:,} rows")

    # [STUDENT-WRITTEN]
    #if a checklist appears in more than one chunk boundary
    #dedup again across the full set
    #combines all chunks to one DF
    checklists = pd.concat(rows, ignore_index = True)
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
    #returns ONLY qualifying checklists 
    print(f"\n{len(checklists):,} unique checklists total, "
          f"{checklists['QUALIFIES'].sum():,} qualify after effort caps\n")
    return checklists[checklists["QUALIFIES"]].copy()

# [STUDENT-WRITTEN]
#same as build_predictions.py
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


#splits unique grid cells into train / test sets, so every checklist from a cell ends up on one side of the split
def make_spatial_split(qualifying):
    #select only LAT_IDX and LON_IDX columns
    #remove duplicates
    #remove old indexes and reset to 0, 1, 2, 3, 4....
    unique_cells = qualifying[["LAT_IDX", "LON_IDX"]].drop_duplicates().reset_index(drop = True)

    #create random number generator
    #shuffle list of random numbers 
    rng = np.random.default_rng(RANDOM_SEED)
    shuffled_idx = rng.permutation(len(unique_cells))
    #how many cells are in the testing data (20 percent)
    n_test = int(len(unique_cells) * TEST_FRACTION)
    
    # [AI-GENERATED - Claude AI 18-07-2026]
    test_cells = set(map(tuple, unique_cells.iloc[shuffled_idx[:n_test]].values))
    # (everything not in test_cells is train)
    #shuffled_idx[:n_test] -> take the first n_test entry (randomly chosen positions)
    #unique_cells.iloc -> select rows by numeric position, pull random rows from unique_cells
    #.values -> convert DF into numpy arrays [lat_idx, lon_idx]
    #map(tuple, ...) -> convert numpy arrays to tuples
    #set(...) -> collect tuples into a set
    #this set contains test_cells, (lax_idx, lon_idx) tuples held for testing

    # [STUDENT-WRITTEN]
    qualifying = qualifying.copy() #create independednt copy
    #build tuple column
    qualifying["IS_TEST_CELL"] = list(
        zip(qualifying["LAT_IDX"], qualifying["LON_IDX"])
    )
    #overwrite with true/false
    #chosen for testing = true, not chosen = false
    qualifying["IS_TEST_CELL"] = qualifying["IS_TEST_CELL"].isin(test_cells)

    # ~ flips the true/false values
    n_train_checklists = (~qualifying["IS_TEST_CELL"]).sum() #NOT test cells
    n_test_checklists = qualifying["IS_TEST_CELL"].sum()

    # [AI-GENERATED - Claude AI 18-07-2026]
    #summary print
    print(
        f"\nSpatial split: {len(unique_cells):,} unique cells -> "
        f"{len(unique_cells) - n_test:,} train cells / {n_test:,} test cells\n"
        f"({n_train_checklists:,} train checklists / {n_test_checklists:,} test checklists)\n",
        file = sys.stderr,
    )
    return qualifying

# [STUDENT-WRITTEN]
#builds the dataframe for random forest predictor values
def build_features(df):
    df = add_distance_features(df) #adds DIST_TO_COAT and DIST_TO_CITY
    features = pd.DataFrame({
        "LATITUDE": df["LATITUDE"],
        "LONGITUDE": df["LONGITUDE"],
        "DURATION MINUTES": df["DURATION MINUTES"],
        "EFFORT DISTANCE KM": df["EFFORT DISTANCE KM"],
        "NUMBER OBSERVERS": df["NUMBER OBSERVERS"],
        "DIST_TO_COAST_KM": df["DIST_TO_COAST_KM"],
        "DIST_TO_CITY_KM": df["DIST_TO_CITY_KM"],
    })
    #SEASONS variable from earlier use here
    #create one column per possible season
    #using this methods instead of .get_dummies() to avoid mismatches columns bugs
    for season in SEASONS:
        features[f"SEASON_{season}"] = (df["SEASON"] == season).astype(int)
    return features

#learn table
#remember table, BaselineModel object stores this
#predict using learned table
class BaselineModel:
    def __init__(self, train_checklists, species_detected_train):
        self.rates_by_season = {} #hold encounter rates for every training cell, per season
        self.neighbours_by_season = {}  #hold nearest neighbour, per season
        # [AI-GENERATED - Claude AI 18-07-2026]
        #last resort 
        #overall proportion of training checklists that detected species 
        self.overall_rate = species_detected_train.mean() if len(species_detected_train) else 0.0

        # [STUDENT-WRITTEN]
        #compute how many qualifying checklists exist per cell and season
        #(training only)
        totals = (
            train_checklists.groupby(["LAT_IDX", "LON_IDX", "SEASON"])["SAMPLING EVENT IDENTIFIER"]
            .nunique()
            .reset_index(name = "TOTAL")
        )

        #select rows where species_detected_train is True
        #pull IDs
        detected_ids = set(
            train_checklists.loc[species_detected_train, "SAMPLING EVENT IDENTIFIER"]
        )

        #add new DETECTED column
        #true if ID is detected, false otherwise 
        train_checklists = train_checklists.copy()
        train_checklists["DETECTED"] = train_checklists["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)
        
        #filter to only detected rows
        #group and count how many detected chechlists per cell + season
        det_counts = (
            train_checklists[train_checklists["DETECTED"]]
            .groupby(["LAT_IDX", "LON_IDX", "SEASON"])["SAMPLING EVENT IDENTIFIER"]
            .nunique()
            .reset_index(name = "DETECTIONS")
        )

        #keep every row from totals, attach matching data from det_counts
        merged = totals.merge(det_counts, on = ["LAT_IDX", "LON_IDX", "SEASON"], how = "left")
        #if results is NaN replace with 0
        merged["DETECTIONS"] = merged["DETECTIONS"].fillna(0)
        #rate calculation
        merged["RATE"] = merged["DETECTIONS"] / merged["TOTAL"]

    
        #for each season, filter to that seasons rows only, skip of empty
        #convert index into lat/lon coordinate
        for season in SEASONS:
            sub = merged[merged["SEASON"] == season]
            if sub.empty:
                continue
            lat_c, lon_c = cell_centre(sub["LAT_IDX"], sub["LON_IDX"])

            # [AI-GENERATED - Claude AI 18-07-2026]
            coords = np.column_stack([lat_c, lon_c])  #combine two arrays into one, each row is a lat/lon pair
            #with a new coordinate point, what known point is closest?
            nn = NearestNeighbors(n_neighbors = 1).fit(coords)
            #store nn and season rates into dictionaries
            self.neighbours_by_season[season] = nn
            self.rates_by_season[season] = sub["RATE"].values

    # [STUDENT-WRITTEN]
    #look up a rate for each test checklist (or look up nearest-neighbour)
    def predict(self, lat_idx, lon_idx, season):
        #convert to coordinate
        #stack lat/lon to 2D array 
        lat_c, lon_c = cell_centre(lat_idx, lon_idx)
        query = np.column_stack([lat_c, lon_c])
        #new array of lat_idx length
        #hold final predictions
        preds = np.full(len(lat_idx), self.overall_rate)

        # [AI-GENERATED - Claude AI 18-07-2026]
        #loop through each season
        #(nearest neightbour tool was fitted separately to each season)
        for s in SEASONS:
            #compare whole season column against season name
            #convert to numpy array
            mask = (season == s).values
            #check if there is a True value in the array, if not, skip to next season
            if not mask.any() or s not in self.neighbours_by_season:
                continue

            # [AI-GENERATED - Claude AI 18-07-2026]
            #get nearest neighbour that was fitted to this season
            nn = self.neighbours_by_season[s]
             #return distance to nearest training point and index
            _, idx = nn.kneighbors(query[mask])
            #don't need distance, forget this (_)
            #find rate that belonged to nearest training cel, save as this checklists prediction
            preds[mask] = self.rates_by_season[s][idx.ravel()]
        #return final array
        return preds

# [STUDENT-WRITTEN]
def main(in_path, out_path):
    #load both tables 
    #apply spatial split 
    checklists = load_checklists(in_path)
    species_df = load_species_rows(in_path)
    checklists = make_spatial_split(checklists)
    #attach IS_TEST_CELL to every row
    train = checklists[~checklists["IS_TEST_CELL"]].reset_index(drop = True)
    test = checklists[checklists["IS_TEST_CELL"]].reset_index(drop = True)

    #build feature tables with location, effot, season columns
    X_train_full = build_features(train)
    X_test_full = build_features(test)

    results = []

    #filter to just detection rows 
    #collect IDs
    for species in SHORTLIST:
        detected_ids = set(
            species_df.loc[species_df["COMMON NAME"] == species, "SAMPLING EVENT IDENTIFIER"]
        )

        #lables
        #true if checklist detected species
        y_train = train["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)
        y_test = test["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)

        # [AI-GENERATED - Claude AI 18-07-2026]
        n_test_pos = int(y_test.sum())
        if n_test_pos < 5 or y_train.sum() < 5:
            # too few positive examples on one side of the split to get a
            # meaningful AUC/Brier score - flag rather than report a
            # misleading number
            print(f"{species}: skipped, too few detections in train or test split", file = sys.stderr)
            results.append({
                "species": species,
                "n_test_checklists": len(test),
                "n_test_positives": n_test_pos,
                "baseline_auc": None,
                "rf_auc": None,
                "baseline_brier": None,
                "rf_brier": None,
                "note": "insufficient detections for reliable evaluation",
            })
            continue


        # [STUDENT-WRITTEN]
        #create new basline model object
        #predicit for every test checklist
        baseline = BaselineModel(train, y_train)
        baseline_preds = baseline.predict(test["LAT_IDX"], test["LON_IDX"], test["SEASON"])

        # [AI-GENERATED - Claude AI 18-07-2026]
        #random forest, calibrated so its predicted probabilities line up
        #with true observed frequencies (raw RF probabilities run high here
        #because class_weight="balanced" deliberately boosts the rare
        #class during training - great for AUC/ranking, bad for Brier
        #unless corrected)
        base_rf = RandomForestClassifier(**RF_PARAMS)
        calibration_note = ""

        if y_train.sum() >= CALIBRATION_MIN_TRAIN_POSITIVES:
            rf = CalibratedClassifierCV(base_rf, method = "sigmoid", cv = CALIBRATION_CV_FOLDS)
        else:
            #too few positives to calibrate reliably - use the plain RF and
            #say so, rather than silently reporting an unstable Brier score
            rf = base_rf
            calibration_note = "uncalibrated (too few positives to calibrate reliably)"

         # [STUDENT-WRITTEN]
        #learn relationship between features and label
        #return result -> probability of 'not detected' and 'detected'
        rf.fit(X_train_full, y_train)
        rf_preds = rf.predict_proba(X_test_full)[:, 1] #slice, only give column index 1

        # [AI-GENERATED - Claude AI 18-07-2026]
        results.append({
            "species": species,
            "n_test_checklists": len(test),
            "n_test_positives": n_test_pos,
            "baseline_auc": round(roc_auc_score(y_test, baseline_preds), 4),
            "rf_auc": round(roc_auc_score(y_test, rf_preds), 4),
            "baseline_brier": round(brier_score_loss(y_test, baseline_preds), 4),
            "rf_brier": round(brier_score_loss(y_test, rf_preds), 4),
            "note": calibration_note,
        })
        print(f"{species}: done", file = sys.stderr)


    #convert list of dictionaries to a table
    #write to csv
    #print comparison
    out_df = pd.DataFrame(results)
    out_df.to_csv(out_path, index = False)

    print(f"\nDONE")
    print(f"Comparison table written to {out_path}\n")
    print(out_df.to_string(index = False))

# [AI-GENERATED - Claude AI 18-07-2026]
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python train_evaluate_model.py path/to/ebd_GB-SCT_filtered.txt path/to/comparison_metrics.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
