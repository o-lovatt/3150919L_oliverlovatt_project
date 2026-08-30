"""
4-way ablation for Barn Swallow
Barn Swallows funnel along coastlines during migration

its earlier combined-feature gain (verify_distance_features.py: 0.8013 -> 0.8114 AUC)
could have come from DIST_TO_COAST_KM rather than DIST_TO_CITY_KM

This ablation shows which feature actually did the work,
the same test as for Atlantic Puffin.


Filename: verify_distance_features_swallow.py
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

from train_evaluate_model import (
    RF_PARAMS, SEASONS, CALIBRATION_MIN_TRAIN_POSITIVES, CALIBRATION_CV_FOLDS,
    RANDOM_SEED, load_checklists, load_species_rows, make_spatial_split,
)
from distance_features import add_distance_features
from bootstrap_ci import bootstrap_metric, N_BOOTSTRAP

TUNED_SPECIES = "Barn Swallow"


# [AI-GENERATED - Claude AI 29-08-2026]
def build_base_columns(df):
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


def build_feature_variants(df):
    # compute both distance columns once, then assemble four variants
    # so coastline/city KDTree lookups aren't repeated four times over
    df_with_dist = add_distance_features(df)
    base = build_base_columns(df)

    coast_only = base.copy()
    coast_only["DIST_TO_COAST_KM"] = df_with_dist["DIST_TO_COAST_KM"]

    city_only = base.copy()
    city_only["DIST_TO_CITY_KM"] = df_with_dist["DIST_TO_CITY_KM"]

    both = base.copy()
    both["DIST_TO_COAST_KM"] = df_with_dist["DIST_TO_COAST_KM"]
    both["DIST_TO_CITY_KM"] = df_with_dist["DIST_TO_CITY_KM"]

    return {
        "baseline": base,
        "+coast only": coast_only,
        "+city only": city_only,
        "+both": both,
    }


# [AI-GENERATED - Claude AI 29-08-2026]
def fit_and_predict(X_train, y_train, X_test):
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
    print(f"{TUNED_SPECIES}: {int(y_train.sum())} train positives / {int(y_test.sum())} test positives")

    rng = np.random.default_rng(RANDOM_SEED)

    print("\nBuilding feature variants...")
    train_variants = build_feature_variants(train)
    test_variants = build_feature_variants(test)

    results = {}
    for label in train_variants:
        print(f"Fitting: {label}...")
        preds = fit_and_predict(train_variants[label], y_train, test_variants[label])
        results[label] = preds

    print(f"\nBootstrapping ({N_BOOTSTRAP} resamples per variant)...")
    ci_results = {}
    for label, preds in results.items():
        auc_ci = bootstrap_metric(y_test_arr, preds, roc_auc_score, rng)
        brier_ci = bootstrap_metric(y_test_arr, preds, brier_score_loss, rng)
        ci_results[label] = (auc_ci, brier_ci)

    def fmt(ci):
        return f"{ci['mean']:.4f}  [{ci['ci_low']:.4f}, {ci['ci_high']:.4f}]"

    print(f"\n=== {TUNED_SPECIES}: feature ablation (calibrated, held-out test set) ===")
    print(f"{'':16s}{'AUC (mean [95% CI])':30s}{'Brier (mean [95% CI])'}")
    for label in train_variants:
        auc_ci, brier_ci = ci_results[label]
        print(f"{label:16s}{fmt(auc_ci):30s}{fmt(brier_ci)}")

    # check each variant against the baseline specifically -
    # that's the comparison that actually answers "does this feature earn its place"
    base_auc_ci, base_brier_ci = ci_results["baseline"]
    print("\nAUC 95% CI overlap vs baseline:")
    for label in ["+coast only", "+city only", "+both"]:
        auc_ci, _ = ci_results[label]
        overlap = not (auc_ci["ci_low"] > base_auc_ci["ci_high"]
                        or base_auc_ci["ci_low"] > auc_ci["ci_high"])
        print(f"  {label:16s} overlap = {overlap}")

    out_rows = []
    for label in train_variants:
        auc_ci, brier_ci = ci_results[label]
        out_rows.append({
            "features": label,
            "auc_mean": round(auc_ci["mean"], 4),
            "auc_ci": f"[{auc_ci['ci_low']:.4f}, {auc_ci['ci_high']:.4f}]",
            "brier_mean": round(brier_ci["mean"], 4),
            "brier_ci": f"[{brier_ci['ci_low']:.4f}, {brier_ci['ci_high']:.4f}]",
        })
    out_df = pd.DataFrame(out_rows)
    out_df.to_csv("bootstrap_distance_features_swallow_ablation.csv", index=False)
    print("\nSaved to bootstrap_distance_features_swallow_ablation.csv")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_distance_features_swallow.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])
