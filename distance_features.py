"""
Two extra predictor features for the RF model distance to the nearest
coastline point, and distance to the nearest major Scottish settlement

- DIST_TO_COAST_KM is being added because several of the species are strongly coastal so proximity to the coast is a real ecological signal
- DIST_TO_CITY_KM is being added because eBird checklist density is higher near population centres regardless of true species occurrence
this gives the model a way to account for that bias 

The coastline data source is Natural Earth 10m coastline filtered
to a bounding box around Scotland and saved as scotland_coastline_points.csv

# [AI-GENERATED - Claude AI 29-08-2026]
Both use the SAME equirectangular projection already used in
constants.py / gridCell.js (fixed REFERENCE_LAT, KM_PER_DEG_LAT,
KM_PER_DEG_LON) rather than full haversine, so distances here are
directly consistent with the rest of the pipeline's spatial maths.


Filename: distance_features.py
Author: Oliver Lovatt
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 29-08-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
"""

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from constants import REFERENCE_LAT, KM_PER_DEG_LAT, KM_PER_DEG_LON

# [STUDENT-WRITTEN]
#hand-picked coordinates covering the central belt, highlands, and islands
SCOTTISH_SETTLEMENTS = {
    "Glasgow": (55.8642, -4.2518),
    "Edinburgh": (55.9533, -3.1883),
    "Aberdeen": (57.1497, -2.0943),
    "Dundee": (56.4620, -2.9707),
    "Inverness": (57.4778, -4.2247),
    "Perth": (56.3950, -3.4308),
    "Stirling": (56.1165, -3.9369),
    "Paisley": (55.8456, -4.4239),
    "East Kilbride": (55.7642, -4.1763),
    "Hamilton": (55.7778, -4.0392),
    "Kilmarnock": (55.6114, -4.4957),
    "Ayr": (55.4586, -4.6292),
    "Greenock": (55.9483, -4.7628),
    "Coatbridge": (55.8631, -4.0230),
    "Livingston": (55.8825, -3.5227),
    "Falkirk": (56.0019, -3.7839),
    "Kirkcaldy": (56.1165, -3.1590),
    "Glenrothes": (56.1997, -3.1740),
    "Dunfermline": (56.0719, -3.4520),
    "Motherwell": (55.7868, -3.9938),
    "Cumbernauld": (55.9450, -3.9930),
    "Dumfries": (55.0704, -3.6053),
    "Galashiels": (55.6183, -2.8062),
    "Elgin": (57.6493, -3.3155),
    "Fort William": (56.8198, -5.1052),
    "Oban": (56.4152, -5.4719),
    "Wick": (58.4392, -3.0930),
    "Thurso": (58.5975, -3.5254),
    "Stornoway": (58.2093, -6.3861),
    "Kirkwall": (58.9807, -2.9605),
    "Lerwick": (60.1547, -1.1494),
}


# [AI-GENERATED - Claude AI 29-08-2026]
def _project_to_km(lat, lon):
    # same equirectangular approximation as constants.py / gridCell.js:
    # fixed reference latitude, so this is only valid at Scotland's scale
    x_km = np.asarray(lon) * KM_PER_DEG_LON
    y_km = np.asarray(lat) * KM_PER_DEG_LAT
    return np.column_stack([x_km, y_km])


# [STUDENT-WRITTEN]
#build both KDTrees once 
_coastline_df = pd.read_csv("scotland_coastline_points.csv")
_coastline_xy = _project_to_km(_coastline_df["lat"].values, _coastline_df["lon"].values)
_coastline_tree = cKDTree(_coastline_xy)

_settlement_lats = [lat for lat, lon in SCOTTISH_SETTLEMENTS.values()]
_settlement_lons = [lon for lat, lon in SCOTTISH_SETTLEMENTS.values()]
_settlement_xy = _project_to_km(_settlement_lats, _settlement_lons)
_settlement_tree = cKDTree(_settlement_xy)


# [AI-GENERATED - Claude AI 29-08-2026]
def add_distance_features(df):
    """
    Takes a dataframe with LATITUDE/LONGITUDE columns and returns a copy
    with two new columns added: DIST_TO_COAST_KM and DIST_TO_CITY_KM.
    """
    points_xy = _project_to_km(df["LATITUDE"].values, df["LONGITUDE"].values)

    coast_dist, _ = _coastline_tree.query(points_xy)
    city_dist, _ = _settlement_tree.query(points_xy)

    out = df.copy()
    out["DIST_TO_COAST_KM"] = coast_dist
    out["DIST_TO_CITY_KM"] = city_dist
    return out
