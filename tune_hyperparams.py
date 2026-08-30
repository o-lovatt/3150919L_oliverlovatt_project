"""
checks if there are better RF hyperparameters than what i hand picked.
using GroupKFold by grid cell so informatin ins't leaked across cells.

Tune using ONE well sampled species like barn swallown rather than ever species separately
RF Params are golabal across species

Filename: verify_tuned_params.py
Author: Oliver Lovatt
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 29-08-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""

import sys 
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, GroupKFold

from train_evaluate_model import (
    RANDOM_SEED, load_checklists, load_species_rows, make_spatial_split, build_features
)

TUNED_SPECIES = "Barn Swallow"

def main (in_path):
    #same data loading and spatial split as train_evaluate_model
    #only using training side here
    #test set stays untouched
    checklists = load_checklists(in_path)
    species_df = load_species_rows(in_path)
    checklists = make_spatial_split(checklists)
    train = checklists[~checklists["IS_TEST_CELL"]].reset_index(drop = True)

    X_train = build_features(train)

    #check what training checklists detected the tuned species
    detected_ids = set(
        species_df.loc[species_df["COMMON NAME"] == TUNED_SPECIES, "SAMPLING EVENT IDENTIFIER"]
    )
    y_train = train["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)

    # [AI-GENERATED - Claude AI 29-08-2026]
    # GroupKFold needs one scalar label per row, not a (lat, lon) tuple —
    # factorize the cell coordinate pairs into single integer group IDs
    groups = (train["LAT_IDX"].astype(str) + "_" + train["LON_IDX"].astype(str)).values
 

    #range of values RandomizedSearchCV will take combinations from
    #(not exhaustive)
    param_distributions = {
        "n_estimators": [100, 200, 300, 400, 500],
        "max_depth": [8, 10, 12, 15, 20, None],
        "min_samples_leaf": [2, 5, 10, 20],
        "max_features": ["sqrt", "log2", 0.5],
    }

    # [STUDENT WRITTEN]
    #same class weight and random state as RF_PARAMS elsewhere
    base_rf = RandomForestClassifier(class_weight = "balanced", random_state = RANDOM_SEED, n_jobs = -1)

    search = RandomizedSearchCV(
        base_rf,
        param_distributions,
        n_iter = 25, #try 25 random combinations from param_distributions
        scoring="roc_auc", #matching metric i've already used for model comparison before
        cv=GroupKFold(n_splits = 5), #evaluate across 5 spatial folds
        random_state = RANDOM_SEED,
        n_jobs = -1,
    )
    search.fit(X_train, y_train, groups=groups)

    # [AI-GENERATED - Claude AI 29-08-2026]
    print(f"\nBest AUC found: {search.best_score_:.4f}")
    print(f"Best parameters: {search.best_params_}")

# [AI-GENERATED - Claude AI 29-08-2026]
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tune_hyperparameters.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])
