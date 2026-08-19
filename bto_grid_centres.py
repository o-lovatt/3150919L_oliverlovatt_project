"""
lookup table for mapping BTO's grid references (HP02, HP03 etc...) to real lat/lon points


Filename: bto_grid_centres.py
Author: Oliver Lovatt
Date: 19-08-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 19/08/2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.

"""
import pandas as pd

# [STUDENT-WRITTEN]
#load file
df = pd.read_csv(r"C:\Users\olive\Documents\3150919l_oliverlovatt_project\atlas_open_data_files\grid_square_coordinates_lookup.csv")
 
#remove duplicate point corners
df_dedup = df.drop_duplicates(subset=['grid', 'long', 'lat'])

# [AI-GENERATED - Claude AI 19-08-2026]
#comput avg lon/lat
grid_centres = df_dedup.groupby('grid').agg({'long': 'mean', 'lat': 'mean'})
