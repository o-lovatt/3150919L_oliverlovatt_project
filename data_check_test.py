import sys
import pandas as pd

#edited (makes script portable and hides username+folder structure)
if len(sys.argv) != 3:
    print("Usage: python data_check_test.py path/to/ebd_file.txt path/to/output.txt")
    sys.exit(1) #if count is wrong, exit

path = sys.argv[1]
output_path = sys.argv[2]


#Read the header row to see the column names
header = pd.read_csv(path, sep = '\t', nrows = 0)
#\t for tab separated file, nrows = 0 just checks the headers
print("COLUMN NAMES")
for col in header.columns:
    print(col)

#Read a sample of 20 rows to see real values
sample = pd.read_csv(path, sep = '\t', nrows = 20, low_memory = False)#read the whole chunk in one pass
print("\nSAMPLE ROWS (first 20)")
print(sample.to_string())#convert sample table to printable text

#Save column list + sample to a separate file you 
with open(output_path, "w", encoding = "utf-8") as f: #safe for special characters
    f.write("COLUMNS:\n")
    f.write("\n".join(header.columns))
    f.write("\n\nSAMPLE:\n")
    f.write(sample.to_string())

print(f"\nsaved inspection output to {output_path}")