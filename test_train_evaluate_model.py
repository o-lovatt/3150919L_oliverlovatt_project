import pandas as pd
from train_evaluate_model import BaselineModel

"""test if baseline returns higher predicted score for cell where species was detected often vs where it wasn't"""
def test_baseline_model_favours_more_detections():
    #create two fake grid cels in summer
    #cell one high rate of detection
    #cell two no detection
    train_checklists = pd.DataFrame({
        "SAMPLING EVENT IDENTIFIER": ["a", "b", "c", "d", "e", "f", "g", "h"],
        "LAT_IDX": [0, 0, 0, 0, 1, 1, 1, 1],
        "LON_IDX": [0, 0, 0, 0, 1, 1, 1, 1],
        "SEASON": ["Summer"] * 8,
    })

    #detected == TRUE on a, b, c, d
    species_detected_train = train_checklists["SAMPLING EVENT IDENTIFIER"].isin(["a", "b", "c", "d"])

    model = BaselineModel(train_checklists, species_detected_train)

    #what are predictions at both cell centres?
    lat_idx = pd.Series([0, 1])
    lon_idx = pd.Series([0, 1])
    season = pd.Series(["Summer", "Summer"])

    preds = model.predict(lat_idx, lon_idx, season)

    #cell 0,0 should have higher predicted rate than 1,1
    assert preds[0] > preds[1]
