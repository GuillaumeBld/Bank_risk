"""
etl.py – One-stop Extract, Transform, Load for the ESG Default Risk Pipeline.

- Reads both raw input files (annual returns, Fama-French factors).
- Cleans and standardizes the data.
- Saves cleaned CSVs for downstream modeling.
- Logs all steps and output details.
"""

import pandas as pd
from pathlib import Path

def run():
    # Define directories
    raw = Path('esg-default-risk-phase1/data/raw/')
    clean = Path('esg-default-risk-phase1/data/clean/')
    logs = Path('esg-default-risk-phase1/data/logs/')
    clean.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    
    # --- 1. Annual Returns File ---
    annual_fp = 'esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv'
    annual = pd.read_csv(annual_fp)
    # Standardize columns
    annual.columns = [c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '').replace('%', '').replace(',', '').replace('/', '_').replace('.', '_') for c in annual.columns]
    # Dates
    annual['date'] = pd.to_datetime(annual['date'], format='%Y-%m-%d', errors='coerce')
    # Numerics
    for col in annual.columns:
        if col not in ['instrument', 'instrument_1', 'date']:
            annual[col] = pd.to_numeric(annual[col], errors='coerce')
    # Save
    annual_clean_fp = clean / 'annual_returns_clean.csv'
    annual.to_csv(annual_clean_fp, index=False)

    # --- 2. Fama-French Factors File ---
    ff_fp = raw / 'F-F_Research_Data_Factors.csv'
    # Skip metadata/header lines and use first valid data row
    ff = pd.read_csv(ff_fp, skiprows=4)
    ff.columns = ['yyyymm', 'mkt_rf', 'smb', 'hml', 'rf']
    ff['yyyymm'] = ff['yyyymm'].astype(str)
    ff = ff[ff['yyyymm'].str.match(r'^[0-9]{6}$')]
    ff_clean_fp = clean / 'fama_french_factors_clean.csv'
    ff.to_csv(ff_clean_fp, index=False)

    # --- 3. Logging ---
    log_fp = logs / 'data_cleaning_log.txt'
    with open(log_fp, 'w') as log:
        log.write('[etl.py] Data cleaning completed.\n')
        log.write(f'Input annual: {annual_fp}\nShape: {annual.shape}\n')
        log.write(f'Columns: {list(annual.columns)}\n')
        log.write(f'Output: {annual_clean_fp}\n\n')
        log.write(f'Input FF: {ff_fp}\nShape: {ff.shape}\n')
        log.write(f'Columns: {list(ff.columns)}\n')
        log.write(f'Output: {ff_clean_fp}\n')

    print(f"[etl.py] ETL complete. Cleaned data in '{clean}', logs in '{logs}'.")

def main():
    run()

if __name__ == "__main__":
    main()