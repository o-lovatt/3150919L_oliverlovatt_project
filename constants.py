"""
file for constant values, to reduce deduplication.
"""

import numpy as np


# [STUDENT-WRITTEN]
SHORTLIST = [
    #original 10 species
    "Osprey",
    "Common Cuckoo",
    "Barn Swallow",
    "Arctic Tern",
    "Atlantic Puffin",
    "Crested Tit",
    "Rock Ptarmigan",
    "Red Kite",
    "White-tailed Eagle",
    "Red Grouse",

    #second batch added
    "Willow Warbler",
    "Black Guillemot",
    "Eurasian Curlew",
    "White-throated Dipper",
    "Common Kingfisher",
    "Long-tailed Tit",
    "European Golden-Plover",
    "Short-eared Owl",
    "Common Wood-Pigeon",
    "Manx Shearwater",
    "Snow Bunting",
    "Northern Gannet",
]

SCIENTIFIC_NAMES = {
    "Osprey": "Pandion haliaetus",
    "Common Cuckoo": "Cuculus canorus",
    "Barn Swallow": "Hirundo rustica",
    "Arctic Tern": "Sterna paradisaea",
    "Atlantic Puffin": "Fratercula arctica",
    "Crested Tit": "Lophophanes cristatus",
    "Rock Ptarmigan": "Lagopus muta",
    "Red Kite": "Milvus milvus",
    "White-tailed Eagle": "Haliaeetus albicilla",
    "Red Grouse": "Lagopus scotica",
    "Willow Warbler": "Phylloscopus trochilus",
    "Black Guillemot": "Cepphus grylle",
    "Eurasian Curlew": "Numenius arquata",
    "White-throated Dipper": "Cinclus cinclus",
    "Common Kingfisher": "Alcedo atthis",
    "Long-tailed Tit": "Aegithalos caudatus",
    "European Golden-Plover": "Pluvialis apricaria",
    "Short-eared Owl": "Asio flammeus",
    "Common Wood-Pigeon": "Columba palumbus",
    "Manx Shearwater": "Puffinus puffinus",
    "Snow Bunting": "Plectrophenax nivalis",
    "Northern Gannet": "Morus bassanus",
}

#European Golden-Plover, Short-eared Owl, Snow Bunting are all technically migratory, but can be seen in scotland year round
#these categories aren't used yet other than the database, but might still use them for a migratory/resident toggle function
MIGRATORY_SPECIES = {
    "Osprey", "Common Cuckoo", "Barn Swallow", "Arctic Tern", "Atlantic Puffin",
    "Willow Warbler", "Manx Shearwater", "Northern Gannet", "Snow Bunting", 
    "Short-eared Owl", "European Golden-Plover",
}

RESIDENT_SPECIES = {
    "Crested Tit", "Rock Ptarmigan", "Red Kite", "Red Grouse", "White-tailed Eagle",
    "Black Guillemot", "Eurasian Curlew", "White-throated Dipper", "Common Kingfisher",
    "Long-tailed Tit", "Common Wood-Pigeon",
}

#effort standardization values based on eBirds practices
MAX_DURATION_MIN = 300
MAX_DISTANCE_KM = 10
MAX_OBSERVERS = 10

#grid cell values
CELL_KM = 15
REFERENCE_LAT = 56.5
KM_PER_DEG_LAT = 111.0
KM_PER_DEG_LON = KM_PER_DEG_LAT * np.cos(np.radians(REFERENCE_LAT))
LAT_BIN_SIZE = CELL_KM / KM_PER_DEG_LAT
LON_BIN_SIZE = CELL_KM / KM_PER_DEG_LON

MONTH_TO_SEASON = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}

SEASONS = ["Spring", "Summer", "Autumn", "Winter"]