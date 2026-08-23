"""
Bootstrap confidence intervals for AUC-ROC and Brier score, for the
baseline and Random Forest model, on the same spatial test set
used in train_evaluate_model.py.

Filename: bootstrap_ci.py
Author: Oliver Lovatt
Date: 20-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 20/07/2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""
import sys
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss

# [STUDENT-WRITTEN]
#reuse same data as train_evaluate_model
from train_evaluate_model import (
    SHORTLIST, RF_PARAMS, CALIBRATION_MIN_TRAIN_POSITIVES, CALIBRATION_CV_FOLDS,
    RANDOM_SEED, load_checklists, load_species_rows, make_spatial_split,
    build_features, BaselineModel,
)

N_BOOTSTRAP = 1000 #resamples to take
CI_LOW, CI_HIGH = 2.5, 97.5 #percentiles for a 95% confidence interval

#resample y_true with N_BOOTSTRAP times
#recalculate metric on each resample
#return mean and 95% confidence interval
def bootstrap_metric(y_true, preds, metric_fn, rng, n_boot = N_BOOTSTRAP):
    n = len(y_true)
    y_true = np.asarray(y_true)
    preds = np.asarray(preds)
    scores = []

    for _ in range(n_boot):
        idx = rng.integers(0, n, n) #sample checklists with replacement
        y_sample = y_true[idx]
        p_sample = preds[idx]

        #a resample with only one class present makes AUC undefined, skip
        if len(np.unique(y_sample)) < 2:
            continue
        scores.append(metric_fn(y_sample, p_sample))

    scores = np.array(scores)
    # [AI-GENERATED - Claude AI 27-07-2026]
    return {
        "mean": scores.mean(),
        "ci_low": np.percentile(scores, CI_LOW),
        "ci_high": np.percentile(scores, CI_HIGH),
        "n_valid_resamples": len(scores),
    }

# [STUDENT-WRITTEN]
def main(in_path):
    #same as train_evaluate_model
    checklists = load_checklists(in_path)
    species_df = load_species_rows(in_path)
    checklists = make_spatial_split(checklists)

    train = checklists[~checklists["IS_TEST_CELL"]].reset_index(drop = True)
    test = checklists[checklists["IS_TEST_CELL"]].reset_index(drop = True)

    #feature matrices
    X_train_full = build_features(train)
    X_test_full = build_features(test)

    rng = np.random.default_rng(RANDOM_SEED) #keeps results reproducable
    results = []

    for species in SHORTLIST:
        # [AI-GENERATED - Claude AI 27-07-2026]
        print(f"bootstrapping: {species}")
        # [STUDENT-WRITTEN]
        detected_ids = set(
            species_df.loc[species_df["COMMON NAME"] == species, "SAMPLING EVENT IDENTIFIER"]
        )
        y_train = train["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)
        y_test = test["SAMPLING EVENT IDENTIFIER"].isin(detected_ids)

        # [AI-GENERATED - Claude AI 27-07-2026]
        n_test_pos = int(y_test.sum())
        if n_test_pos < 5 or y_train.sum() < 5:
            print(f"  {species}: skipped, too few detections")
            continue

        # [STUDENT-WRITTEN]
        #same baseline + RF fit as train_evaluate_model so results match
        baseline = BaselineModel(train, y_train)
        baseline_preds = baseline.predict(test["LAT_IDX"], test["LON_IDX"], test["SEASON"])

        # [AI-GENERATED - Claude AI 27-07-2026]
        # only calibrate if there's enough positive data to do so reliably
        #(also same as train_evaluate)
        base_rf = RandomForestClassifier(**RF_PARAMS)
        if y_train.sum() >= CALIBRATION_MIN_TRAIN_POSITIVES:
            rf = CalibratedClassifierCV(base_rf, method = "sigmoid", cv = CALIBRATION_CV_FOLDS)
        else:
            rf = base_rf
        rf.fit(X_train_full, y_train)
        rf_preds = rf.predict_proba(X_test_full)[:, 1]

        y_test_arr = y_test.to_numpy()

        # [STUDENT-WRITTEN]
        #bootstrap all combinations (baseline/RF x AUC/brier)
        baseline_auc_ci = bootstrap_metric(y_test_arr, baseline_preds, roc_auc_score, rng)
        rf_auc_ci = bootstrap_metric(y_test_arr, rf_preds, roc_auc_score, rng)
        baseline_brier_ci = bootstrap_metric(y_test_arr, baseline_preds, brier_score_loss, rng)
        rf_brier_ci = bootstrap_metric(y_test_arr, rf_preds, brier_score_loss, rng)

        # [AI-GENERATED - Claude AI 27-07-2026]
        # store as formatted strings ("[low, high]") so the output CSV is
        # directly readable/citable without further processing
        results.append({
            "species": species,
            "n_test_positives": n_test_pos,
            "baseline_auc_mean": round(baseline_auc_ci["mean"], 4),
            "baseline_auc_ci": f"[{baseline_auc_ci['ci_low']:.4f}, {baseline_auc_ci['ci_high']:.4f}]",
            "rf_auc_mean": round(rf_auc_ci["mean"], 4),
            "rf_auc_ci": f"[{rf_auc_ci['ci_low']:.4f}, {rf_auc_ci['ci_high']:.4f}]",
            "baseline_brier_mean": round(baseline_brier_ci["mean"], 4),
            "baseline_brier_ci": f"[{baseline_brier_ci['ci_low']:.4f}, {baseline_brier_ci['ci_high']:.4f}]",
            "rf_brier_mean": round(rf_brier_ci["mean"], 4),
            "rf_brier_ci": f"[{rf_brier_ci['ci_low']:.4f}, {rf_brier_ci['ci_high']:.4f}]",
        })

    # [AI-GENERATED - Claude AI 27-07-2026]
    out_df = pd.DataFrame(results)
    out_df.to_csv("bootstrap_confidence_intervals.csv", index = False)
    print("\nDONE")
    print(out_df.to_string(index = False))

# [AI-GENERATED - Claude AI 27-07-2026]
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bootstrap_ci.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])
