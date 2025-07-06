"""
This script concatenates the cleaned 2016-2020 outstanding shares data with the 2021-2023 data to create a full panel for all banks.

Inputs:
  - data/clean/merged_outstanding_shares_2016_2020.csv
  - data/clean/bank_outstanding_shares_2016_2023.csv
Outputs:
  - data/clean/bank_outstanding_shares_full_panel_2016_2023.csv
Log:
  - data/logs/concat_outstanding_shares_full_panel_log.txt
"""
import pandas as pd
import os

# File paths
BASE = os.path.join(os.path.dirname(__file__), '../../data/clean')
FILE_2016_2020 = os.path.join(BASE, 'merged_outstanding_shares_2016_2020.csv')
FILE_2021_2023 = os.path.join(BASE, 'bank_outstanding_shares_2016_2023.csv')
OUTFILE = os.path.join(BASE, 'bank_outstanding_shares_full_panel_2016_2023.csv')
LOGFILE = os.path.join(BASE, '../logs/concat_outstanding_shares_full_panel_log.txt')

# Read files
df_early = pd.read_csv(FILE_2016_2020)
df_late = pd.read_csv(FILE_2021_2023)

# Standardize columns for 2016-2020
df_early_panel = df_early.rename(columns={
    'Ticker': 'symbol',
    'Year': 'year',
    'Date1': 'fiscal_date',
    'Final Shares Outstanding': 'shares_outstanding'
})[['symbol', 'year', 'fiscal_date', 'shares_outstanding']]

# Standardize columns for 2021-2023
df_late_panel = df_late.rename(columns={
    'shares_outstanding': 'shares_outstanding',
    'symbol': 'symbol',
    'year': 'year',
    'fiscal_date': 'fiscal_date'
})[['symbol', 'year', 'fiscal_date', 'shares_outstanding']]

# Remove 2020 from late panel to avoid overlap
df_late_panel = df_late_panel[df_late_panel['year'] > 2020]

# Concatenate
full_panel = pd.concat([df_early_panel, df_late_panel], ignore_index=True)
full_panel = full_panel.sort_values(['symbol', 'year'])

# Save
full_panel.to_csv(OUTFILE, index=False)

# Log
with open(LOGFILE, 'w') as f:
    f.write(f"Rows in 2016-2020: {len(df_early_panel)}\n")
    f.write(f"Rows in 2021-2023: {len(df_late_panel)}\n")
    f.write(f"Total rows in full panel: {len(full_panel)}\n")
    f.write(f"Symbols: {full_panel['symbol'].nunique()}\n")
    f.write(f"Years: {full_panel['year'].min()} to {full_panel['year'].max()}\n")

print(f"Full panel saved to {OUTFILE}")
print(f"Log written to {LOGFILE}") 