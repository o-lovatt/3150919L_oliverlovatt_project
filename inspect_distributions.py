"""
eBird EBD column distribution inspector
get value counts for the key columns used for filtering.

Filename: inspect_distributions.py
Author: Oliver Lovatt
Date: 20-07-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 03-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""
import sys
import pandas as pd

# [STUDENT-WRITTEN]
CHUNK_SIZE = 100_000 #CONSTANT, how many rows read to memory at once 

#columns needed for filtering decision
COLUMNS_OF_INTEREST = [
    "OBSERVATION TYPE",   #renamed from PROTOCOL TYPE in EBD schema v1.16 (Mar 2025 Projects release)
    "PROTOCOL NAME",      #new field alongside OBSERVATION TYPE
    "PROTOCOL CODE",      #""
    "ALL SPECIES REPORTED",
    "OBSERVATION DATE",
    "BREEDING CODE",
    "BREEDING CATEGORY",
    "DURATION MINUTES",
    "EFFORT DISTANCE KM",
    "NUMBER OBSERVERS",
]

# [STUDENT-WRITTEN]
def main(path):
    #function variables
    observation_type_counts = pd.Series(dtype = "int64") #hold whole numbers
    protocol_name_counts = pd.Series(dtype = "int64")
    all_species_counts = pd.Series(dtype = "int64")
    year_counts = pd.Series(dtype = "int64")
    breeding_code_counts = pd.Series(dtype = "int64")
    breeding_category_counts = pd.Series(dtype = "int64")

    total_rows = 0 #counter
    null_counts = {} #dictionary, every key is a column name
    for col in COLUMNS_OF_INTEREST:
        null_counts[col] = 0


    # [STUDENT-WRITTEN]
    reader = pd.read_csv(
        path,
        sep = "\t", #tab separated
        usecols = COLUMNS_OF_INTEREST, #only keep columns in our list
        chunksize = CHUNK_SIZE,
        dtype = str, #read everything as string first
        on_bad_lines=  "warn", #print warning if row hs wrong number of columns
        low_memory = False,
    )

    # [AI-GENERATED - Claude AI 03-07-2026]
    for i, chunk in enumerate(reader): #loop over reader
        total_rows += len(chunk)

        # [STUDENT-WRITTEN]
        if "OBSERVATION TYPE" in chunk:
            #count how many times unique values appear
            #include missing values
            #add chunk count to total
            #count values not seen before as 0
            observation_type_counts = observation_type_counts.add(
                chunk["OBSERVATION TYPE"].value_counts(dropna = False), fill_value = 0
            )

        if "PROTOCOL NAME" in chunk:
            protocol_name_counts = protocol_name_counts.add(
                chunk["PROTOCOL NAME"].value_counts(dropna = False), fill_value = 0
            )

        if "ALL SPECIES REPORTED" in chunk:
            all_species_counts = all_species_counts.add(
                chunk["ALL SPECIES REPORTED"].value_counts(dropna = False), fill_value = 0
            )

        if "OBSERVATION DATE" in chunk:
            #convert text date to date object
            #if date is wrong/malformed, convert to NaN
            years = pd.to_datetime( 
                chunk["OBSERVATION DATE"], errors = "coerce"
            ).dt.year
            year_counts = year_counts.add(
                years.value_counts(dropna = False), fill_value = 0
            )

        if "BREEDING CODE" in chunk:
            breeding_code_counts = breeding_code_counts.add(
                chunk["BREEDING CODE"].value_counts(dropna = False), fill_value = 0
            )

        if "BREEDING CATEGORY" in chunk:
            breeding_category_counts = breeding_category_counts.add(
                chunk["BREEDING CATEGORY"].value_counts(dropna = False), fill_value = 0
            )

        #loop over every column of interest
        for col in COLUMNS_OF_INTEREST:
            if col in chunk:
                #true = column is missing 
                #give count of missing values
                null_counts[col] += chunk[col].isna().sum()
                
        # [AI-GENERATED - Claude AI 03-07-2026]
        if (i + 1) % 10 == 0:
            print(f"processed {total_rows:,} rows so far")
        #for better output formatting

    # [AI-GENERATED - Claude AI 03-07-2026]
    #print everything
    print(f"\nTOTAL ROWS: {total_rows:,}\n")

    print("OBSERVATION TYPE")
    print(observation_type_counts.sort_values(ascending=False).to_string())

    print("\nPROTOCOL NAME")
    print(protocol_name_counts.sort_values(ascending=False).to_string())

    print("\nALL SPECIES REPORTED")
    print(all_species_counts.sort_values(ascending=False).to_string())

    print("\nOBSERVATION YEAR (chronologically)")
    print(year_counts.sort_index().to_string())

    print("\nBREEDING CODE")
    print(breeding_code_counts.sort_values(ascending=False).to_string())

    print("\nBREEDING CATEGORY")
    print(breeding_category_counts.sort_values(ascending=False).to_string())

    print("\nNULL COUNTS (per column of interest)")

    # [STUDENT-WRITTEN]
    for col, count in null_counts.items():
        if total_rows:
            pct = (count / total_rows * 100)
        else:
            pct = 0
            
        #if total_rows = 0, stop divide by 0 crash
        # [AI-GENERATED - Claude AI 03-07-2026]
        print(f"{col}: {count:,} nulls ({pct:.1f}%)") #format number to 1 decimal place


# [AI-GENERATED - Claude AI 03-07-2026]
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspect_distributions.py path/to/ebd_scotland.txt")
        sys.exit(1)
    main(sys.argv[1])
