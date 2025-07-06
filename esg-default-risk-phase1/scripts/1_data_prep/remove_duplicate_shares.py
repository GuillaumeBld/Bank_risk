"""
This script removes duplicate (symbol, year) rows from the outstanding shares panel file, keeping the first occurrence.

Inputs:
  - data/clean/bank_outstanding_shares_full_panel_2016_2023.csv
Outputs:
  - data/clean/bank_outstanding_shares_full_panel_2016_2023.csv (cleaned, in place)
Log:
  - data/logs/remove_duplicate_shares_log.txt
"""
import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), '../../data/clean')
IN_FILE = os.path.join(BASE, 'bank_outstanding_shares_full_panel_2016_2023.csv')
LOG_FILE = os.path.join(BASE, '../logs/remove_duplicate_shares_log.txt')

def main():
    df = pd.read_csv(IN_FILE)
    before = len(df)
    df_clean = df.drop_duplicates(subset=['symbol', 'year'], keep='first')
    after = len(df_clean)
    df_clean.to_csv(IN_FILE, index=False)
    with open(LOG_FILE, 'w') as f:
        f.write(f"Removed {before - after} duplicate rows.\n")
        f.write(f"Final row count: {after}\n")

if __name__ == '__main__':
    main() 