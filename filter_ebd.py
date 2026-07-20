"""
eBird EBD filtering script
Apply four filtering conditions to produce checklist dataset for the bird migration prediction model

    - OBSERVATION TYPE in [Traveling, Stationary]
    - ALL SPECIES REPORTED == 1
    - OBSERVATION DATE year >= 2010
    - LATITUDE/LONGITUDE within Scotland bounding box 

writes a filtered .txt with the same column structure

Filename: filter_edb.py
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
CHUNK_SIZE = 100_000

STANDARD_PROTOCOLS = {"Traveling", "Stationary"}
MIN_YEAR = 2010

#bounding box for mainland Scotland + inhabited island groups
#Shetland, Orkney, Outer Hebrides, St Kilda, excludes offshore seawatching trips
LAT_MIN, LAT_MAX = 54.5, 61.0
LON_MIN, LON_MAX = -9.0, 2.0


def main(in_path, out_path):
    total_rows_in = 0
    total_rows_out = 0
    first_chunk = True

    reader = pd.read_csv(
        in_path,
        sep = "\t",
        chunksize = CHUNK_SIZE,
        dtype = str, #read everything as string
        on_bad_lines = "warn",
        low_memory = False,
    )

    for i, chunk in enumerate(reader):
        total_rows_in += len(chunk)

        #standard protocol only filter
        #check if observation type is travelling or stationary
        mask = chunk["OBSERVATION TYPE"].isin(STANDARD_PROTOCOLS)

        #complete checklists only filter
        #check checklist is completed with no missing values
        #combine existing mask with new conditions
        mask = mask & (chunk["ALL SPECIES REPORTED"] == "1")

        #modern records only (year >= MIN_YEAR) filter
        years = pd.to_datetime(chunk["OBSERVATION DATE"], errors = "coerce").dt.year
        mask = mask & (years >= MIN_YEAR)

        #Scotland bounding box filter
        #convert lat/long columns to numbers
        lat = pd.to_numeric(chunk["LATITUDE"], errors = "coerce")
        lon = pd.to_numeric(chunk["LONGITUDE"], errors = "coerce")
        mask = mask & (lat.between(LAT_MIN, LAT_MAX) & lon.between(LON_MIN, LON_MAX))

        filtered = chunk[mask]
        total_rows_out += len(filtered)

        # [AI-GENERATED - Claude AI 03-07-2026]
        #write incrementally so memory doesn't hold more than one chunk
        #first chunk opens in write mode, chunks after are oppened in append mode
        #only write column header once
        if first_chunk:
            mode = "w"
            write_header = True
        else:
            mode = "a"
            write_header = False

        filtered.to_csv(
            out_path,
            sep = "\t",
            mode = mode,
            header = write_header,
            index = False,
        )
        first_chunk = False


        if (i + 1) % 10 == 0:
            print(
                f"processed {total_rows_in:,} rows in, "
                f"{total_rows_out:,} rows kept so far",
                file = sys.stderr,
            )

    # [STUDENT-WRITTEN]
    if total_rows_in:
         pct_kept = total_rows_out / total_rows_in * 100
    else:
         pct_kept = 0
    
    # [AI-GENERATED - Claude AI 03-07-2026]
    #print summary
    print(f"\nDONE")
    print(f"Rows in:  {total_rows_in:,}")
    print(f"Rows out: {total_rows_out:,} ({pct_kept:.1f}% kept)")#same divide by zero fix
    print(f"Filtered file written to: {out_path}")

# [AI-GENERATED - Claude AI 03-07-2026]
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python filter_ebd.py path/to/ebd_scotland.txt path/to/output_filtered.txt")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
