"""
filtering the bto dataset for cross validate eBirds

Filename: filter_bto.py
Author: Oliver Lovatt
Date: 19-08-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 19/08/2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""
from  bto_grid_centres import grid_centres
from constants import KM_PER_DEG_LAT, KM_PER_DEG_LON

import pandas as pd
import math

# [STUDENT-WRITTEN]
df = pd.read_csv(r"C:\Users\olive\Documents\3150919l_oliverlovatt_project\atlas_open_data_files\distributions.csv")

filtered = df[(df['period'] == "2008-11") & (df['season'] == "B")]

# [AI-GENERATED - Claude AI 19-08-2026]
species_df = pd.read_csv(r"C:\Users\olive\Documents\3150919l_oliverlovatt_project\atlas_open_data_files\species_lookup.csv", encoding="latin-1")

predictions_df = pd.read_csv(r"C:\Users\olive\Documents\3150919l_oliverlovatt_project\predictions.csv")

# [STUDENT-WRITTEN]
#cant use the constants here, some of the names are slightly different
my_species_bto = [
    "Osprey", "Cuckoo", "Swallow", "Arctic Tern", "Puffin",
    "Crested Tit", "Ptarmigan", "Red Kite", "White-tailed Eagle", "Red Grouse",
    "Willow Warbler", "Black Guillemot", "Curlew", "Dipper",
    "Kingfisher", "Long-tailed Tit", "Golden Plover", "Short-eared Owl",
    "Woodpigeon", "Manx Shearwater", "Snow Bunting", "Gannet"
]

matching = species_df[species_df['english_name'].isin(my_species_bto)]


#filter down to just species
matching_codes = matching['speccode'].tolist()

species_filtered = filtered[filtered['speccode'].isin(matching_codes)]

#merge with bto_grid_centres
with_coords = species_filtered.merge(grid_centres, on='grid', how='left')


#apply same scotland bounding box as filter_ebd
LAT_MIN, LAT_MAX = 54.5, 61.0
LON_MIN, LON_MAX = -9.0, 2.0

scotland_data = with_coords[
    (with_coords['lat'] >= LAT_MIN) & (with_coords['lat'] <= LAT_MAX)
    & (with_coords['long'] >= LON_MIN) & (with_coords['long'] <= LON_MAX)
]

#same as distanceKM in getpredictionsNearLocation
def distance_km(lat1, lon1, lat2, lon2):
    lat_diff_km = ((lat2 - lat1) * KM_PER_DEG_LAT)
    lon_diff_km = ((lon2 - lon1) * KM_PER_DEG_LON)

    distance = math.sqrt((lat_diff_km * lat_diff_km) + (lon_diff_km * lon_diff_km))
    return distance

#for each prediction calculate distance from the BTO point to the predicted cell
#keep one with smallest distance
def find_closest_prediction(bto_lat, bto_lon, species_predictions):

    # [AI-GENERATED - Claude AI 19-08-2026]
    species_predictions['distance'] = species_predictions.apply(
        lambda row: distance_km(bto_lat, bto_lon, row['lat_centre'], row['lon_centre']), axis=1
        ) #axis = 1 means apply once per row, not per column 
    
    min_distance = species_predictions['distance'].idxmin()
    likelihood_score = species_predictions.loc[min_distance, 'likelihood_score']

    return likelihood_score

#name mapping bto -> ebd
bto_to_app_name = {
    "Osprey": "Osprey",
    "Cuckoo": "Common Cuckoo",
    "Swallow": "Barn Swallow",
    "Arctic Tern": "Arctic Tern",
    "Puffin": "Atlantic Puffin",
    "Crested Tit": "Crested Tit",
    "Ptarmigan": "Rock Ptarmigan",
    "Red Kite": "Red Kite",
    "White-tailed Eagle": "White-tailed Eagle",
    "Red Grouse": "Red Grouse",
    "Willow Warbler": "Willow Warbler",
    "Black Guillemot": "Black Guillemot",
    "Curlew": "Eurasian Curlew",
    "Dipper": "White-throated Dipper",
    "Kingfisher": "Common Kingfisher",
    "Long-tailed Tit": "Long-tailed Tit",
    "Golden Plover": "European Golden-Plover",
    "Short-eared Owl": "Short-eared Owl",
    "Woodpigeon": "Common Wood-Pigeon",
    "Manx Shearwater": "Manx Shearwater",
    "Snow Bunting": "Snow Bunting",
    "Gannet": "Northern Gannet",
}

#attach bto species name to scotland data
scotland_data = scotland_data.merge(matching[['speccode', 'english_name']], on='speccode', how='left')
scotland_data['app_species_name'] = scotland_data['english_name'].map(bto_to_app_name)

def get_matched_likelihood(row):
    species_predictions = predictions_df[
        (predictions_df['species'] == row['app_species_name']) & 
        (predictions_df['season'] == 'Summer')
    ].copy()
    return find_closest_prediction(row['lat'], row['long'], species_predictions)

scotland_data['matched_likelihood'] = scotland_data.apply(get_matched_likelihood, axis = 1)

#output data
scotland_data.to_csv("bto_scotland_filtered.csv", index=False)


#compute each species baseline average
#attach baseline to BTO row
#compare  matched_likelihood vs baseline_likelihood
#filter SUMMER ONLY HERE TOO
species_baseline = predictions_df[predictions_df['season'] == 'Summer'].groupby('species')['likelihood_score'].mean()

scotland_data['baseline_likelihood'] = scotland_data['app_species_name'].map(species_baseline)

#is matched bigger than baseline?
scotland_data['above_baseline'] = scotland_data['matched_likelihood'] > scotland_data["baseline_likelihood"]

agreement_rate = scotland_data['above_baseline'].mean()
print(agreement_rate)

species_agreement = scotland_data.groupby('app_species_name')['above_baseline'].mean()
print(species_agreement.sort_values(ascending=False))