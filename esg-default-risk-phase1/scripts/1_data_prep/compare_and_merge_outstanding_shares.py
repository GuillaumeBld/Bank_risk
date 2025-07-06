"""
This script compares and merges annual outstanding shares for each bank from two sources:
- corrected_bank_outstanding_shares_2016_2020.csv
- outstanding_shares.csv

Inputs:
  - data/clean/corrected_bank_outstanding_shares_2016_2020.csv
  - data/clean/outstanding_shares.csv
Outputs:
  - data/clean/merged_outstanding_shares_2016_2020.csv (with conflicts flagged)
  - data/logs/compare_and_merge_outstanding_shares_log.txt
Log:
  - data/logs/compare_and_merge_outstanding_shares_log.txt
"""
import pandas as pd
import os

# File paths
BASE = os.path.join(os.path.dirname(__file__), '../../data/clean')
FILE1 = os.path.join(BASE, 'corrected_bank_outstanding_shares_2016_2020.csv')
FILE2 = os.path.join(BASE, 'outstanding_shares.csv')
OUTFILE = os.path.join(BASE, 'merged_outstanding_shares_2016_2020.csv')
LOGFILE = os.path.join(BASE, '../logs/compare_and_merge_outstanding_shares_log.txt')

# Read files
df1 = pd.read_csv(FILE1)
df2 = pd.read_csv(FILE2)

# Standardize column names for merging
df1 = df1.rename(columns={
    'Bank': 'Ticker',
    'Outstanding_Shares': 'Outstanding_Shares',
    'Date': 'Date1'
})
df2 = df2.rename(columns={
    'Shares Outstanding': 'Outstanding_Shares',
    'Source': 'Source2'
})

# Merge on Ticker and Year
merged = pd.merge(df1, df2, on=['Ticker', 'Year'], how='outer', suffixes=('_file1', '_file2'))

# Compare values and flag conflicts
def resolve_row(row):
    shares1 = row.get('Outstanding_Shares_file1', None)
    shares2 = row.get('Outstanding_Shares_file2', None)
    # If both are present and equal, keep one
    if pd.notnull(shares1) and pd.notnull(shares2):
        if shares1 == shares2:
            return shares1, 'OK'
        else:
            return shares1, f'CONFLICT: file1={shares1}, file2={shares2}'
    elif pd.notnull(shares1):
        return shares1, 'ONLY_FILE1'
    elif pd.notnull(shares2):
        return shares2, 'ONLY_FILE2'
    else:
        return None, 'MISSING'

merged[['Final Shares Outstanding', 'Status']] = merged.apply(lambda row: pd.Series(resolve_row(row)), axis=1)

# Prepare output DataFrame
out_cols = ['Ticker', 'Year', 'Date1', 'Outstanding_Shares_file1', 'Outstanding_Shares_file2', 'Final Shares Outstanding', 'Status']
merged_out = merged[out_cols]
merged_out = merged_out.sort_values(['Ticker', 'Year'])

# Save merged file
merged_out.to_csv(OUTFILE, index=False)

# Log summary
total = len(merged_out)
conflicts = merged_out['Status'].str.contains('CONFLICT').sum()
only1 = (merged_out['Status'] == 'ONLY_FILE1').sum()
only2 = (merged_out['Status'] == 'ONLY_FILE2').sum()
missing = (merged_out['Status'] == 'MISSING').sum()

with open(LOGFILE, 'w') as f:
    f.write(f"Total rows: {total}\n")
    f.write(f"Conflicts: {conflicts}\n")
    f.write(f"Only in file1: {only1}\n")
    f.write(f"Only in file2: {only2}\n")
    f.write(f"Missing: {missing}\n")
    f.write("\nConflicts detail:\n")
    f.write(merged_out[merged_out['Status'].str.contains('CONFLICT')].to_string(index=False))

print(f"Merged file saved to {OUTFILE}")
print(f"Log written to {LOGFILE}") 