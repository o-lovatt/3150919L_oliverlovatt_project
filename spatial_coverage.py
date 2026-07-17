"""
eBird EBD spatial coverage

this file produces:
- Per-species bounding box + centroid stats for 10 shortlisted species
- scatter plot of Scotland showing where each shortlisted species
  has been recorded -> species_map.png
- overall checklist density hexbin map for all checklists -> effort_density.png. 

Usage:
    python spatial_coverage.py path/to/ebd_GB-SCT_filtered.txt
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  #no GUI needed, just save a png
import matplotlib.pyplot as plt

CHUNK_SIZE = 100_000

SHORTLIST = [
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
]

COLUMNS_NEEDED = ["COMMON NAME", "LATITUDE", "LONGITUDE"]


def main(path):
    #collect every lat/lon value
    #for species in shortlist create a key mapping to lat & lon 
    all_lats = []
    all_lons = []
    species_coords = {s: {"lat": [], "lon": []} for s in SHORTLIST}

    total_rows = 0

    reader = pd.read_csv(
        path,
        sep = "\t",
        usecols = COLUMNS_NEEDED,
        chunksize = CHUNK_SIZE,
        #read lat/lon as float numbers
        dtype = {"COMMON NAME": str, "LATITUDE": float, "LONGITUDE": float},
        on_bad_lines = "warn",
        low_memory = False,
    )

    for i, chunk in enumerate(reader):
        total_rows += len(chunk)

        #overall effort density (every checklist row, all species)
        #convert to numpy array
        #add entire chunk array to the list
        all_lats.append(chunk["LATITUDE"].to_numpy())
        all_lons.append(chunk["LONGITUDE"].to_numpy())

        #per-species points- shortlist only
        #filter chunk to only shortlisted species
        #for each spcies group, append lat/lon arrays into species_coords
        shortlist_chunk = chunk[chunk["COMMON NAME"].isin(SHORTLIST)]
        for species, group in shortlist_chunk.groupby("COMMON NAME"):
            species_coords[species]["lat"].append(group["LATITUDE"].to_numpy())
            species_coords[species]["lon"].append(group["LONGITUDE"].to_numpy())

        if (i + 1) % 10 == 0:
            print(f"processed {total_rows:,} rows so far")

    #flatten list of arrays into one array
    all_lats = np.concatenate(all_lats)
    all_lons = np.concatenate(all_lons)

    print(f"\nTOTAL ROWS: {total_rows:,}\n")

    #Per-species bounding box / centroid stats
    print("SHORTLIST SPECIES: SPATIAL SUMMARY")
    print(f"{'Species':<20}{'N':>8}{'Lat min':>10}{'Lat max':>10}"
          f"{'Lon min':>10}{'Lon max':>10}{'Centroid':>20}")
    
    species_arrays = {}
    #for each shortlist species, flatten into one array
    for species in SHORTLIST:
        if species_coords[species]["lat"]:
            lat = np.concatenate(species_coords[species]["lat"])
        else:
            lat = np.array([])

        if species_coords[species]["lon"]:
            lon = np.concatenate(species_coords[species]["lon"])
        else:
            lon = np.array([])
        
        species_arrays[species] = (lat, lon)

        if len(lat) == 0:
            print(f"{species:<20}{'NO DATA':>8}")
            continue
        centroid = f"({lat.mean():.2f}, {lon.mean():.2f})"
        print(f"{species:<20}{len(lat):>8}{lat.min():>10.2f}{lat.max():>10.2f}"
              f"{lon.min():>10.2f}{lon.max():>10.2f}{centroid:>20}")

    #plot 1 -species scatter map
    #create figure and axis
    fig, ax = plt.subplots(figsize = (9, 12))
    #get colour map --> 10 colours
    cmap = plt.get_cmap("tab10")
    #give position to pick colour
    for idx, species in enumerate(SHORTLIST):
        lat, lon = species_arrays[species]#unpack back to two separate variables
        if len(lat) == 0: #skip species with no data
            continue
        ax.scatter(lon, lat, s = 4, alpha = 0.4, label = species, color = cmap(idx % 10))
        #color = cmap(idx % 10)) is just a futreproofing method if there are ever more than 10 species
        
    
    ax.set_title("Shortlisted species - recorded locations (Scotland EBD, 2010-2026)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(markerscale = 4, fontsize = 8, loc = "upper left", bbox_to_anchor = (1.01, 1))
    ax.set_aspect("equal") #makes sure map isn't distorted
    fig.tight_layout()#auto adjusts spacing
    fig.savefig("species_map.png", dpi = 150)#resolution
    print("\nSaved species_map.png")

    #plot 2 - overall checklist effort density
    #hexbin = hexagonal cells
    fig2, ax2 = plt.subplots(figsize = (9, 12))
    #empty cells are left blank
    hb = ax2.hexbin(all_lons, all_lats, gridsize = 80, cmap = "inferno", mincnt = 1, bins = "log")
    ax2.set_title("Overall checklist density - ALL species (sampling effort proxy)")
    ax2.set_xlabel("Longitude")
    ax2.set_ylabel("Latitude")
    ax2.set_aspect("equal")
    cb = fig2.colorbar(hb, ax=ax2, label="log10(checklist count)")
    fig2.tight_layout()
    fig2.savefig("effort_density.png", dpi = 150)
    print("Saved effort_density.png")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python spatial_coverage.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])
