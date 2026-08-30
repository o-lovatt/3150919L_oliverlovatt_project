"""
bootstrap confidence intervals comparing the current RF_PARAMS against the tuned hyperparameters
found by tune_hyperparams RandomizedSearchCV, for Barn Swallow.

- uses same methodology as bootstrap_ci, both models are fit once on thr train cells
- same CalibratedClassifierCV wrapping
- held out 132 cell test set is resampled with replacement 1,000 times
- this gets a 95% ci on auc and bruer for each parameter set

Filename: bootstrap_tuning_comparison.py
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
    RF_PARAMS, CALIBRATION_MIN_TRAIN_POSITIVES, CALIBRATION_CV_FOLDS,
    RANDOM_SEED, load_checklists, load_species_rows, make_spatial_split, build_features,
)
from bootstrap_ci import bootstrap_metric, N_BOOTSTRAP

TUNED_SPECIES = "Barn Swallow"

# [AI-GENERATED - Claude AI 29-08-2026]
# best result from tune_hyperparams.py's RandomizedSearchCV
TUNED_PARAMS = dict(
    n_estimators=500,
    max_depth=12,
    min_samples_leaf=20,
    max_features="sqrt",
    class_weight="balanced",
    random_state=RANDOM_SEED,
    n_jobs=-1,
)


# [AI-GENERATED - Claude AI 29-08-2026]
def fit_and_predict(params, X_train, y_train, X_test):
    # same calibration logic as bootstrap_ci.py / train_evaluate_model.py -
    # only calibrate if there's enough positive training data to do so reliably
    base_rf = RandomForestClassifier(**params)
    if y_train.sum() >= CALIBRATION_MIN_TRAIN_POSITIVES:
        model = CalibratedClassifierCV(base_rf, method="sigmoid", cv=CALIBRATION_CV_FOLDS)
    else:
        model = base_rf
    model.fit(X_train, y_train)
    return model.predict_proba(X_test)[:, 1]


def main(in_path):
    #same data loading and spatial split as train_evaluate_model
    checklists = load_checklists(in_path)
    species_df = load_species_rows(in_path)
    checklists = make_spatial_split(checklists)

    train = checklists[~checklists["IS_TEST_CELL"]].reset_index(drop=True)
    test = checklists[checklists["IS_TEST_CELL"]].reset_index(drop=True)

    X_train = build_features(train)
    X_test = build_features(test)

    detected_ids = set(
        species_df.loc[species_df["COMMON NAME"] == TUNED_SPECIES, "SAMPLING EVENT IDENTIFIER"]
    )
    y_train = train["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)
    y_test = test["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)
    y_test_arr = y_test.to_numpy()

    rng = np.random.default_rng(RANDOM_SEED)  #keeps results reproducible

    print(f"Fitting current RF_PARAMS for {TUNED_SPECIES}...")
    current_preds = fit_and_predict(RF_PARAMS, X_train, y_train, X_test)

    print(f"Fitting tuned params for {TUNED_SPECIES}...")
    tuned_preds = fit_and_predict(TUNED_PARAMS, X_train, y_train, X_test)

    print(f"\nBootstrapping ({N_BOOTSTRAP} resamples)...")
    current_auc_ci = bootstrap_metric(y_test_arr, current_preds, roc_auc_score, rng)
    tuned_auc_ci = bootstrap_metric(y_test_arr, tuned_preds, roc_auc_score, rng)
    current_brier_ci = bootstrap_metric(y_test_arr, current_preds, brier_score_loss, rng)
    tuned_brier_ci = bootstrap_metric(y_test_arr, tuned_preds, brier_score_loss, rng)

    # [AI-GENERATED - Claude AI 29-08-2026]
    def fmt(ci):
        return f"{ci['mean']:.4f}  [{ci['ci_low']:.4f}, {ci['ci_high']:.4f}]"

    print(f"\n=== {TUNED_SPECIES}: current vs tuned RF_PARAMS (calibrated, held-out test set) ===")
    print(f"{'':22s}{'AUC (mean [95% CI])':30s}{'Brier (mean [95% CI])'}")
    print(f"{'Current RF_PARAMS':22s}{fmt(current_auc_ci):30s}{fmt(current_brier_ci)}")
    print(f"{'Tuned params':22s}{fmt(tuned_auc_ci):30s}{fmt(tuned_brier_ci)}")

    #non-overlapping CIs is the same significance check used throughout
    #the rest of the dissertation's bootstrap results
    auc_overlap = not (tuned_auc_ci["ci_low"] > current_auc_ci["ci_high"]
                        or current_auc_ci["ci_low"] > tuned_auc_ci["ci_high"])
    brier_overlap = not (tuned_brier_ci["ci_low"] > current_brier_ci["ci_high"]
                          or current_brier_ci["ci_low"] > tuned_brier_ci["ci_high"])
    print(f"\nAUC 95% CIs overlap:   {auc_overlap}")
    print(f"Brier 95% CIs overlap: {brier_overlap}")

    out_df = pd.DataFrame([
        {
            "params": "current",
            "auc_mean": round(current_auc_ci["mean"], 4),
            "auc_ci": f"[{current_auc_ci['ci_low']:.4f}, {current_auc_ci['ci_high']:.4f}]",
            "brier_mean": round(current_brier_ci["mean"], 4),
            "brier_ci": f"[{current_brier_ci['ci_low']:.4f}, {current_brier_ci['ci_high']:.4f}]",
        },
        {
            "params": "tuned",
            "auc_mean": round(tuned_auc_ci["mean"], 4),
            "auc_ci": f"[{tuned_auc_ci['ci_low']:.4f}, {tuned_auc_ci['ci_high']:.4f}]",
            "brier_mean": round(tuned_brier_ci["mean"], 4),
            "brier_ci": f"[{tuned_brier_ci['ci_low']:.4f}, {tuned_brier_ci['ci_high']:.4f}]",
        },
    ])
    out_df.to_csv("bootstrap_tuning_comparison.csv", index=False)
    print("\nSaved to bootstrap_tuning_comparison.csv")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bootstrap_tuning_comparison.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])