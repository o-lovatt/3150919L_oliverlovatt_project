"""
direct comparison of the current hand picked RF_PARAMS against RandomizedSearchCV result from tune_hyperparams.py.

- Trains BOTH parameter sets on the same train cells
- scores BOTH on the same held out test cells
- prints AUC + Brier side by side against the existing comparison_metrics.csv value for Barn Swallow
- this way i know if the tuned params are actually an improvement

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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss

# [STUDENT-WRITTEN]
from train_evaluate_model import (
    RANDOM_SEED, load_checklists, load_species_rows, make_spatial_split, build_features
)

TUNED_SPECIES = "Barn Swallow"

#current settings from train_evaluate_model RF_PARAMS
CURRENT_PARAMS = dict(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=RANDOM_SEED,
    n_jobs=-1,
)

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
def evaluate(label, params, X_train, y_train, X_test, y_test):
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    probs = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, probs)
    brier = brier_score_loss(y_test, probs)
    print(f"{label}:")
    print(f"  AUC   = {auc:.4f}")
    print(f"  Brier = {brier:.4f}\n")
    return auc, brier

# [STUDENT-WRITTEN]
def main(in_path):
    #same data loading and spatial split as train_evaluate_model & tune_hyperparams
    #but this time using BOTH sides of the split - train 
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

    # [AI-GENERATED - Claude AI 29-08-2026]
    print(f"Comparing RF params for {TUNED_SPECIES} on the held-out spatial test set")
    print(f"({len(train)} train checklists / {len(test)} test checklists)\n")

    evaluate("Current RF_PARAMS", CURRENT_PARAMS, X_train, y_train, X_test, y_test)
    evaluate("Tuned params (RandomizedSearchCV result)", TUNED_PARAMS, X_train, y_train, X_test, y_test)

    print("For reference, comparison_metrics.csv currently records:")
    print("  Current RF_PARAMS: AUC = 0.8013, Brier = 0.1067")
    print("  (this run's 'Current RF_PARAMS' number above should closely match that,")
    print("   since it's the same params/split/seed - if it doesn't, something's off)")

# [AI-GENERATED - Claude AI 29-08-2026]
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_tuned_params.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])