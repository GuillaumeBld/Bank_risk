"""
This script cleans and standardizes the raw data for the pipeline.
Inputs: data/raw/Copy of annual_returns-5-20-2025.csv, data/raw/F-F_Research_Data_Factors.csv
Outputs: data/clean/annual_returns_clean.csv, data/clean/fama_french_factors_clean.csv
Log: data/logs/data_cleaning_log.txt
"""

import pandas as pd
from pathlib import Path

raw = Path('esg-default-risk-phase1/data/raw/')
clean = Path('esg-default-risk-phase1/data/clean/')
clean.mkdir(exist_ok=True)

# 1. Annual returns file
annual = pd.read_csv(
    raw/'annual_returns-5-20-2025.csv',
    parse_dates=['Date'],
    dayfirst=False,
    infer_datetime_format=True
)
# Now normalize column names
annual.columns = [c.strip().lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '').replace('%', '').replace(',', '').replace('/', '_').replace('.', '_') for c in annual.columns]
# Fix dates
annual['date'] = pd.to_datetime(annual['date'], format='%Y-%m-%d', errors='coerce')
# Force all numeric columns to numeric
for col in annual.columns:
    if col not in ['instrument', 'instrument_1', 'date']:
        annual[col] = pd.to_numeric(annual[col], errors='coerce')
# Save clean CSV
annual.to_csv(clean/'annual_returns_clean.csv', index=False)

# 2. Fama-French file
ff = pd.read_csv(raw/'F-F_Research_Data_Factors.csv', skiprows=4)
ff.columns = ['yyyymm', 'mkt_rf', 'smb', 'hml', 'rf']
ff['yyyymm'] = ff['yyyymm'].astype(str)
ff = ff[ff['yyyymm'].str.match(r'^[0-9]{6}$')]
ff.to_csv(clean/'fama_french_factors_clean.csv', index=False)

# 3. Log what was done
with open('esg-default-risk-phase1/data/logs/data_cleaning_log.txt', 'w') as log:
    log.write('annual_returns_clean.csv: dates parsed, numeric conversion, columns cleaned\n')
    log.write('fama_french_factors_clean.csv: header rows dropped, columns renamed, years filtered\n')
    log.write('Shapes: annual=%s, ff=%s\n' % (annual.shape, ff.shape))
    log.write('Columns annual: %s\n' % str(list(annual.columns)))
    log.write('Columns ff: %s\n' % str(list(ff.columns))) 