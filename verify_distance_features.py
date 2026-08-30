"""
Bootstrap confidence intervals comparing the original feature set against
original features + DIST_TO_COAST_KM + DIST_TO_CITY_KM only for Barn Swallow.


Filename: verify_distance_features.py
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
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss

# [STUDENT WRITTEN]
from train_evaluate_model import (
    RF_PARAMS, SEASONS, CALIBRATION_MIN_TRAIN_POSITIVES, CALIBRATION_CV_FOLDS,
    RANDOM_SEED, load_checklists, load_species_rows, make_spatial_split,
)
from distance_features import add_distance_features
from bootstrap_ci import bootstrap_metric, N_BOOTSTRAP

TUNED_SPECIES = "Barn Swallow"


# [AI-GENERATED - Claude AI 29-08-2026]
def build_baseline_features(df):
    # same as the ORIGINAL build_features in train_evaluate_model.py,
    # reproduced here so this script works regardless of whether that
    # function has already been edited to include distance features
    features = pd.DataFrame({
        "LATITUDE": df["LATITUDE"],
        "LONGITUDE": df["LONGITUDE"],
        "DURATION MINUTES": df["DURATION MINUTES"],
        "EFFORT DISTANCE KM": df["EFFORT DISTANCE KM"],
        "NUMBER OBSERVERS": df["NUMBER OBSERVERS"],
    })
    for season in SEASONS:
        features[f"SEASON_{season}"] = (df["SEASON"] == season).astype(int)
    return features

# [STUDENT WRITTEN]
def build_distance_features(df):
    df = add_distance_features(df)
    features = build_baseline_features(df)
    features["DIST_TO_COAST_KM"] = df["DIST_TO_COAST_KM"]
    features["DIST_TO_CITY_KM"] = df["DIST_TO_CITY_KM"]
    return features

# [AI-GENERATED - Claude AI 29-08-2026]
def fit_and_predict(X_train, y_train, X_test):
    # same calibration logic as bootstrap_ci.py / train_evaluate_model.py -
    # only calibrate if there's enough positive training data to do so reliably
    base_rf = RandomForestClassifier(**RF_PARAMS)
    if y_train.sum() >= CALIBRATION_MIN_TRAIN_POSITIVES:
        model = CalibratedClassifierCV(base_rf, method="sigmoid", cv=CALIBRATION_CV_FOLDS)
    else:
        model = base_rf
    model.fit(X_train, y_train)
    return model.predict_proba(X_test)[:, 1]


def main(in_path):
    checklists = load_checklists(in_path)
    species_df = load_species_rows(in_path)
    checklists = make_spatial_split(checklists)

    train = checklists[~checklists["IS_TEST_CELL"]].reset_index(drop=True)
    test = checklists[checklists["IS_TEST_CELL"]].reset_index(drop=True)

    detected_ids = set(
        species_df.loc[species_df["COMMON NAME"] == TUNED_SPECIES, "SAMPLING EVENT IDENTIFIER"]
    )
    y_train = train["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)
    y_test = test["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)
    y_test_arr = y_test.to_numpy()

    rng = np.random.default_rng(RANDOM_SEED)

    # [AI-GENERATED - Claude AI 29-08-2026]
    print("Building baseline feature set...")
    X_train_base = build_baseline_features(train)
    X_test_base = build_baseline_features(test)

    print("Building baseline + distance feature set...")
    X_train_dist = build_distance_features(train)
    X_test_dist = build_distance_features(test)

    print(f"\nFitting baseline model for {TUNED_SPECIES}...")
    base_preds = fit_and_predict(X_train_base, y_train, X_test_base)

    print(f"Fitting baseline + distance model for {TUNED_SPECIES}...")
    dist_preds = fit_and_predict(X_train_dist, y_train, X_test_dist)

    print(f"\nBootstrapping ({N_BOOTSTRAP} resamples)...")
    base_auc_ci = bootstrap_metric(y_test_arr, base_preds, roc_auc_score, rng)
    dist_auc_ci = bootstrap_metric(y_test_arr, dist_preds, roc_auc_score, rng)
    base_brier_ci = bootstrap_metric(y_test_arr, base_preds, brier_score_loss, rng)
    dist_brier_ci = bootstrap_metric(y_test_arr, dist_preds, brier_score_loss, rng)

    def fmt(ci):
        return f"{ci['mean']:.4f}  [{ci['ci_low']:.4f}, {ci['ci_high']:.4f}]"

    print(f"\n=== {TUNED_SPECIES}: baseline features vs + distance features (calibrated) ===")
    print(f"{'':26s}{'AUC (mean [95% CI])':30s}{'Brier (mean [95% CI])'}")
    print(f"{'Baseline features':26s}{fmt(base_auc_ci):30s}{fmt(base_brier_ci)}")
    print(f"{'+ distance features':26s}{fmt(dist_auc_ci):30s}{fmt(dist_brier_ci)}")

    auc_overlap = not (dist_auc_ci["ci_low"] > base_auc_ci["ci_high"]
                        or base_auc_ci["ci_low"] > dist_auc_ci["ci_high"])
    brier_overlap = not (dist_brier_ci["ci_low"] > base_brier_ci["ci_high"]
                          or base_brier_ci["ci_low"] > dist_brier_ci["ci_high"])
    print(f"\nAUC 95% CIs overlap:   {auc_overlap}")
    print(f"Brier 95% CIs overlap: {brier_overlap}")

    out_df = pd.DataFrame([
        {
            "features": "baseline",
            "auc_mean": round(base_auc_ci["mean"], 4),
            "auc_ci": f"[{base_auc_ci['ci_low']:.4f}, {base_auc_ci['ci_high']:.4f}]",
            "brier_mean": round(base_brier_ci["mean"], 4),
            "brier_ci": f"[{base_brier_ci['ci_low']:.4f}, {base_brier_ci['ci_high']:.4f}]",
        },
        {
            "features": "baseline + distance",
            "auc_mean": round(dist_auc_ci["mean"], 4),
            "auc_ci": f"[{dist_auc_ci['ci_low']:.4f}, {dist_auc_ci['ci_high']:.4f}]",
            "brier_mean": round(dist_brier_ci["mean"], 4),
            "brier_ci": f"[{dist_brier_ci['ci_low']:.4f}, {dist_brier_ci['ci_high']:.4f}]",
        },
    ])
    out_df.to_csv("bootstrap_distance_features_comparison.csv", index=False)
    print("\nSaved to bootstrap_distance_features_comparison.csv")

# [AI-GENERATED - Claude AI 29-08-2026]
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_distance_features.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])
