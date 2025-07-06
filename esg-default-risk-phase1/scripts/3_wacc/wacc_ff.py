#!/usr/bin/env python3
"""
Calculates Fama–French WACC (WACC_FF) for each bank-year using estimated betas and annual factors.

Inputs:
  - data/model/modeling_data_with_wacc.csv (main modeling data, must include: instrument, year, wacc_equity_weight_, wacc_debt_weight_, wacc_cost_of_debt_, wacc_tax_rate_)
  - data/model/bank_ff_betas_annual.csv (columns: instrument, year, beta_mkt, beta_smb, beta_hml)
  - data/clean/fama_french_factors_annual_clean.csv (columns: year, mkt_rf, smb, hml, rf)

Outputs:
  - data/model/modeling_data_with_wacc_ff.csv (main modeling data with kE_FF, WACC_FF columns added)
  - Log: data/logs/wacc_ff_calc_log.txt

All merges are left-joins using the main modeling data as base. Market cap is not required for WACC_FF calculation.
"""

import pandas as pd
from pathlib import Path

MODEL_FP = Path('esg-default-risk-phase1/data/model/modeling_data_with_wacc.csv')
BETAS_FP = Path('esg-default-risk-phase1/data/model/bank_ff_betas_annual.csv')
FACTORS_FP = Path('esg-default-risk-phase1/data/clean/fama_french_factors_annual_clean.csv')
OUT_FP = Path('esg-default-risk-phase1/data/model/modeling_data_with_wacc_ff.csv')
LOG_FP = Path('esg-default-risk-phase1/data/logs/wacc_ff_calc_log.txt')

# Load data
model = pd.read_csv(MODEL_FP)
betas = pd.read_csv(BETAS_FP)
factors = pd.read_csv(FACTORS_FP)

# Ensure year columns are int
model['year'] = pd.to_datetime(model['date']).dt.year
betas['year'] = betas['year'].astype(int)
factors['year'] = factors['year'].astype(int)

# Merge betas and factors (left-join, keep all model rows)
merged = pd.merge(model, betas, on=['instrument', 'year'], how='left', indicator='beta_merge')
merged = pd.merge(merged, factors, on='year', how='left', indicator='factor_merge')

# Rename _y columns from factors for clarity
merged = merged.rename(columns={
    'mkt_rf_y': 'mkt_rf',
    'smb_y': 'smb',
    'hml_y': 'hml',
    'rf_y': 'rf'
})

# Convert Fama–French factors from percent to decimal
for col in ['rf', 'mkt_rf', 'smb', 'hml']:
    merged[col] = merged[col] / 100

# Normalize all weights and rates to decimals (all are in percent in the dataset)
for col in ['wacc_equity_weight_', 'wacc_debt_weight_', 'wacc_cost_of_debt_', 'wacc_tax_rate_']:
    merged[col] = merged[col] / 100.0

# Check sum of weights
merged['weight_sum'] = merged['wacc_equity_weight_'] + merged['wacc_debt_weight_']
flag_weights = merged[(merged['weight_sum'] < 0.99) | (merged['weight_sum'] > 1.01)]

# Calculate Fama–French cost of equity (kE_FF)
for col in ['rf', 'mkt_rf', 'smb', 'hml', 'beta_mkt', 'beta_smb', 'beta_hml']:
    if col not in merged:
        merged[col] = float('nan')
merged['kE_FF'] = merged['rf'] + merged['beta_mkt'] * merged['mkt_rf'] + merged['beta_smb'] * merged['smb'] + merged['beta_hml'] * merged['hml']

# Calculate WACC_FF using normalized decimals
merged['WACC_FF'] = (
    merged['wacc_equity_weight_'] * merged['kE_FF'] +
    merged['wacc_debt_weight_'] * merged['wacc_cost_of_debt_'] * (1 - merged['wacc_tax_rate_'])
)

# Flag and log any WACC_FF > 0.25 (25%) or < 0%
outlier_wacc = merged[(merged['WACC_FF'] > 0.25) | (merged['WACC_FF'] < 0)]

# Save output (include all banks, even if market cap is missing)
merged.to_csv(OUT_FP, index=False)

# Log summary and issues
with open(LOG_FP, 'w') as log:
    log.write(f"Total rows: {len(merged)}\n")
    log.write(f"Rows with missing betas: {(merged['beta_merge'] == 'left_only').sum()}\n")
    log.write(f"Rows with missing factors: {(merged['factor_merge'] == 'left_only').sum()}\n")
    log.write(f"\nWACC_FF summary:\n{merged['WACC_FF'].describe()}\n")
    log.write(f"\nkE_FF summary:\n{merged['kE_FF'].describe()}\n")
    log.write(f"\nRows with weight_sum not close to 1 (n={len(flag_weights)}):\n")
    log.write(str(flag_weights[['instrument','year','wacc_equity_weight_','wacc_debt_weight_','weight_sum']].head(10)))
    log.write(f"\nRows with WACC_FF > 25% or < 0% (n={len(outlier_wacc)}):\n")
    log.write(str(outlier_wacc[['instrument','year','WACC_FF','wacc_equity_weight_','wacc_debt_weight_','kE_FF']].head(10)))
print(f"[wacc_ff.py] WACC_FF calculation complete. Output: {OUT_FP}")