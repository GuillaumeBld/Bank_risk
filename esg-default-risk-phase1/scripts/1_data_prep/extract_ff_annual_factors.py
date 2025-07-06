"""
Extracts annual Fama–French factors for 2016–2023 from the raw F-F_Research_Data_Factors.csv (annual section, lines 1192 onward).
Inputs: esg-default-risk-phase1/data/raw/F-F_Research_Data_Factors.csv
Outputs: esg-default-risk-phase1/data/clean/fama_french_factors_annual_clean.csv
Log: esg-default-risk-phase1/data/logs/ff_annual_factors_extract_log.txt
"""
import pandas as pd
from pathlib import Path

RAW_PATH = Path('esg-default-risk-phase1/data/raw/F-F_Research_Data_Factors.csv')
CLEAN_PATH = Path('esg-default-risk-phase1/data/clean/fama_french_factors_annual_clean.csv')
LOG_PATH = Path('esg-default-risk-phase1/data/logs/ff_annual_factors_extract_log.txt')

# The annual factors start at line 1192 (0-indexed: 1191), but the first line is a header
skiprows = 1192
nrows = 2024 - 1927 + 1  # 1927 to 2024 inclusive

# Read the annual section, skip the header row
annual = pd.read_csv(RAW_PATH, skiprows=skiprows, header=0, names=['year', 'mkt_rf', 'smb', 'hml', 'rf'])
annual = annual[annual['year'].apply(lambda x: str(x).isdigit())]
annual['year'] = annual['year'].astype(int)
# Filter for 2016–2023
annual = annual[(annual['year'] >= 2016) & (annual['year'] <= 2023)]
annual.to_csv(CLEAN_PATH, index=False)

with open(LOG_PATH, 'w') as log:
    log.write(f"Extracted annual Fama–French factors for years: {annual['year'].tolist()}\n")
    log.write(f"Saved to: {CLEAN_PATH}\n")
    log.write(f"Shape: {annual.shape}\n")
    log.write(f"Columns: {list(annual.columns)}\n")
print(f"[extract_ff_annual_factors.py] Saved annual factors to {CLEAN_PATH}") 