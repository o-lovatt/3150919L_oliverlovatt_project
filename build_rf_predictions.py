"""
generates RF predictions.csv

- take the RF approach (validated in train_model_evaluate.py)
- generate final RF predictions
- trained on the full dataset (no train/est split required this time)
- predict for every row that exists in current predictions.csv


Filename: build_rf_predictions.py
Author: Oliver Lovatt
Date: 04-08-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 04-08-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
"""

import sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV


# [STUDENT-WRITTEN]
#take data needed from train_evaluate_model
from train_evaluate_model import (
    SHORTLIST, RF_PARAMS, CALIBRATION_MIN_TRAIN_POSITIVES, CALIBRATION_CV_FOLDS,
    load_checklists, load_species_rows, build_features,
)

#standard values used for every prediction
STANDARD_DURATION_MIN = 60
STANDARD_DISTANCE_KM = 2
STANDARD_OBSERVERS = 1


def train_full_model(species, checklists, species_df, X_train_full):
    #build set of checklist ID's where species was detected
    detected_ids = set(
        species_df.loc[species_df["COMMON NAME"] == species, "SAMPLING EVENT IDENTIFIER"]
    )
    y = checklists["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)

    # [AI-GENERATED - Claude AI 04-08-2026]
    #if species has < 5 detections, don't train a model
    if y.sum() < 5:
        print(f"  {species}: too few detections in full data, skipping")
        return None

    base_rf = RandomForestClassifier(**RF_PARAMS)
    if y.sum() >= CALIBRATION_MIN_TRAIN_POSITIVES:
        model = CalibratedClassifierCV(base_rf, method="sigmoid", cv=CALIBRATION_CV_FOLDS)
    else:
        model = base_rf

    #train on full set and return trained model
    model.fit(X_train_full, y)
    return model


def main(ebd_path, baseline_csv_path, out_path):
    #load and prepare data
    print("loading checklists and species data...")
    checklists = load_checklists(ebd_path)
    species_df = load_species_rows(ebd_path)
    X_train_full = build_features(checklists)

    #rows we need predictions for, same (species, cell, season) combinations
    #make sure RF output has identical coverage to the baseline
    baseline = pd.read_csv(baseline_csv_path)

    output_rows = []

    #for each speces, train full data model
    for species in SHORTLIST:
        print(f"training on full data: {species}")
        model = train_full_model(species, checklists, species_df, X_train_full)
        if model is None:
            continue

        #filter down to only this species rows (cell/season combination)
        #created independant copy
        species_rows = baseline[baseline["species"] == species].copy()
        if len(species_rows) == 0:
            continue

        #build standardized feature row for each (cell, season) this species needs a prediction for
        predict_df = pd.DataFrame({
            "LATITUDE": species_rows["lat_centre"],
            "LONGITUDE": species_rows["lon_centre"],
            "SEASON": species_rows["season"],
            "DURATION MINUTES": STANDARD_DURATION_MIN,
            "EFFORT DISTANCE KM": STANDARD_DISTANCE_KM,
            "NUMBER OBSERVERS": STANDARD_OBSERVERS,
        })

        #run a table through build_features() so features are same shape as RF model was trained on
        X_predict = build_features(predict_df)
        rf_scores = model.predict_proba(X_predict)[:, 1]

        #overwrite likelihood_score only, round to 4 decimal places
        species_rows["likelihood_score"] = rf_scores.round(4)
        output_rows.append(species_rows)

    #combine all results into one table
    out_df = pd.concat(output_rows, ignore_index=True)
    out_df = out_df.sort_values(["species", "season", "lat_centre", "lon_centre"])
    out_df.to_csv(out_path, index=False)

    # [AI-GENERATED - Claude AI 04-08-2026]
    print(f"\nDONE")
    print(f"RF prediction rows written: {len(out_df):,}")
    print(f"Output: {out_path}")

# [AI-GENERATED - Claude AI 04-08-2026]
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python build_rf_predictions.py path/to/ebd_GB-SCT_filtered.txt path/to/predictions.csv path/to/predictions_rf.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
