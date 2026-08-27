"""
Filename: test_bootstrap.py
Author: Oliver Lovatt
Date: 27-08-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 18-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
"""

import numpy as np
from bootstrap_ci import bootstrap_metric
from sklearn.metrics import roc_auc_score

# [STUDENT-WRITTEN] - skeleton made by [Claude AI 27-08-2026]
def test_bootstrap_returns_valid_data_structure():
    #create fake dataset with mixed true/fase
    y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    preds = np.array([0.1, 0.8, 0.3, 0.6, 0.2, 0.9, 0.4, 0.7])
    rng = np.random.default_rng(42) #seed so results are reprooducable

    result = bootstrap_metric(y_true, preds, roc_auc_score, rng, n_boot = 100)

    # [AI-GENERATED - Claude AI 27-08-2026]
    #check reutrned dict has expected keys & shape
    assert "mean" in result
    assert "ci_low" in result 
    assert "ci_high" in result

    #genuine 95% CI should have ci_low <= mean <= ci_high
    assert result["ci_low"] <= result["mean"] <= result["ci_high"]


