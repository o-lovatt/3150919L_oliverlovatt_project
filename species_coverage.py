"""
eBird EBD species-level coverage

- How many distinct species are present
- checklists-per-species distribution (sparse vs well sampled species)
- Spatial spread per species 
- focused look at shortlisted species specifically

Filename: species_coverage.py
Author: Oliver Lovatt
Date: 20-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 09-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""

import sys
import pandas as pd

# [STUDENT-WRITTEN]
CHUNK_SIZE = 100_000

#Golden Eagle, Western Capercaillie and corncrake dropped
SHORTLIST = [
    "Osprey",
    "Common Cuckoo",
    "Barn Swallow",
    "Arctic Tern",
    "Atlantic Puffin",
    "Crested Tit",
    "Rock Ptarmigan",
    "Red Kite",
    "White-tailed Eagle", #replaced Golden Eagle
    "Red Grouse",
]

COLUMNS_NEEDED = [
    "COMMON NAME",
    "SCIENTIFIC NAME",
    "COUNTY",
    "LOCALITY ID",
    "SAMPLING EVENT IDENTIFIER",
]

# [STUDENT-WRITTEN]
def main(path):
    checklist_counts = pd.Series(dtype="int64") #per species
    #dictionaries start empty
    #build as species are discovered
    county_sets = {} #species --> set of counties
    locality_sets = {} #species --> set of locality

    total_rows = 0

    reader = pd.read_csv(
        path,
        sep = "\t",
        usecols = COLUMNS_NEEDED,
        chunksize = CHUNK_SIZE,
        dtype = str,
        on_bad_lines = "warn",
        low_memory = False,
    )

    # [STUDENT-WRITTEN]
    for i, chunk in enumerate(reader):
        total_rows += len(chunk)

        #checklists per species each row = one species on one checklist
        checklist_counts = checklist_counts.add(
            chunk["COMMON NAME"].value_counts(dropna = False), fill_value = 0
        )

        #split chunk into smaller tables
        #one table per unique species
        for species, group in chunk.groupby("COMMON NAME"):
            if species not in county_sets:
                county_sets[species] = set()
            county_sets[species].update(group["COUNTY"].dropna().unique())
            
            if species not in locality_sets:
                locality_sets[species] = set()
            locality_sets[species].update(group["LOCALITY ID"].dropna().unique())
            

        if (i + 1) % 10 == 0:
            print(f"processed {total_rows:,} rows so far")


    checklist_counts = checklist_counts.sort_values(ascending = False)
    n_species = len(checklist_counts) #number of distinct species

    # [AI-GENERATED - Claude AI 09-07-2026]
    print(f"\nTOTAL ROWS: {total_rows:,}")
    print(f"DISTINCT SPECIES: {n_species:,}\n")

    print("CHECKLISTS-PER-SPECIES: SUMMARY STATS")
    print(checklist_counts.describe().to_string())#gives count mean, std, min/max

    #first 20 entries
    print("\nTOP 20 MOST-RECORDED SPECIES")
    print(checklist_counts.head(20).to_string())

    #last 20 entries
    print("\nBOTTOM 20 LEAST-RECORDED SPECIES")
    print(checklist_counts.tail(20).to_string())

    # [AI-GENERATED - Claude AI 09-07-2026]
    #sort species checklist count into buckets
    print("\nDISTRIBUTION BUCKETS (species count by checklist volume)")
    bins = [0, 10, 50, 100, 500, 1000, 5000, 10000, float("inf")] #(infinity)
    labels = ["1-10", "11-50", "51-100", "101-500", "501-1000",
              "1001-5000", "5001-10000", "10000+"]
    bucketed = pd.cut(checklist_counts, bins = bins, labels = labels)
    print(bucketed.value_counts().sort_index().to_string())

    print("\nSHORTLIST SPECIES: DETAILED COVERAGE")
    print("Species", "Checklists", "Counties", "Localities", sep = "\t")

    # [STUDENT-WRITTEN]
    #loop through species shortlist specifically
    for species in SHORTLIST:
        n_checklists = int(checklist_counts.get(species, 0))#get this species count, or 0
        n_counties = len(county_sets.get(species, set()))#default to empty set
        n_localities = len(locality_sets.get(species, set()))
        # [AI-GENERATED - Claude AI 09-07-2026]
        flag = "  <-- LOW" if n_checklists < 100 else "" #flag for sparse/empty species
        print(species, n_checklists, n_counties, n_localities, flag, sep = "\t")

# [AI-GENERATED - Claude AI 09-07-2026]
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python species_coverage.py path/to/ebd_GB-SCT_filtered.txt")
        sys.exit(1)
    main(sys.argv[1])
