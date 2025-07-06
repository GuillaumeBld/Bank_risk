"""
Estimate Fama–French betas for each bank-year using monthly returns (wide format) and Fama–French factors.

Inputs:
  - data/clean/bank_monthly_total_returns_2016_2023.csv (wide format: one row per bank, columns are months)
  - data/clean/fama_french_factors_clean.csv (columns: yyyymm, mkt_rf, smb, hml, rf)

Outputs:
  - data/model/bank_ff_betas_annual.csv (columns: instrument, year, beta_mkt, beta_smb, beta_hml, n_obs)
  - log: data/logs/beta_estim_log.txt
"""
import pandas as pd
import numpy as np
from pathlib import Path
import statsmodels.api as sm
from dateutil import parser

RETURNS_FP = Path('esg-default-risk-phase1/data/clean/bank_monthly_total_returns_2016_2023.csv')
FACTORS_FP = Path('esg-default-risk-phase1/data/clean/fama_french_factors_clean.csv')
OUT_FP = Path('esg-default-risk-phase1/data/model/bank_ff_betas_annual.csv')
LOG_FP = Path('esg-default-risk-phase1/data/logs/beta_estim_log.txt')

# 1. Load wide monthly returns and melt to long
wide = pd.read_csv(RETURNS_FP)
long = wide.melt(id_vars=[wide.columns[0]], var_name='date', value_name='rit')
long = long.rename(columns={wide.columns[0]: 'instrument'})

# 2. Parse date to YYYY-MM-DD
# Some dates may be in M/D/YY or MM/DD/YY format
long['date'] = long['date'].apply(lambda x: parser.parse(x).strftime('%Y-%m-%d'))
long['rit'] = pd.to_numeric(long['rit'], errors='coerce')
long = long.dropna(subset=['rit'])
long['date'] = pd.to_datetime(long['date'])
long['year'] = long['date'].dt.year
long['yyyymm'] = long['date'].dt.strftime('%Y%m')

# 3. Load Fama–French factors
factors = pd.read_csv(FACTORS_FP)
factors['yyyymm'] = factors['yyyymm'].astype(str)

# 4. Merge on yyyymm
merged = pd.merge(long, factors, on='yyyymm', how='inner', suffixes=('', '_ff'))
merged['ritrf'] = merged['rit'] - merged['rf']

results = []
insufficient = []

for (instrument, year), group in merged.groupby(['instrument', 'year']):
    if len(group) < 6:
        insufficient.append((instrument, year, len(group)))
        continue
    X = group[['mkt_rf', 'smb', 'hml']]
    y = group['ritrf']
    X = sm.add_constant(X)
    try:
        model = sm.OLS(y, X).fit()
        beta_mkt = model.params.get('mkt_rf', np.nan)
        beta_smb = model.params.get('smb', np.nan)
        beta_hml = model.params.get('hml', np.nan)
    except Exception as e:
        insufficient.append((instrument, year, len(group), str(e)))
        continue
    results.append({
        'instrument': instrument,
        'year': year,
        'beta_mkt': beta_mkt,
        'beta_smb': beta_smb,
        'beta_hml': beta_hml,
        'n_obs': len(group)
    })

betas = pd.DataFrame(results)
betas.to_csv(OUT_FP, index=False)

with open(LOG_FP, 'w') as log:
    log.write(f"Total valid regressions: {len(betas)}\n")
    log.write(f"Total insufficient data: {len(insufficient)}\n")
    if insufficient:
        log.write("Insufficient data (instrument, year, n_obs):\n")
        for row in insufficient:
            log.write(str(row) + '\n')
    if not betas.empty:
        log.write("\nBeta summary stats:\n")
        for col in ['beta_mkt', 'beta_smb', 'beta_hml']:
            log.write(f"{col}: mean={betas[col].mean():.3f}, std={betas[col].std():.3f}, min={betas[col].min():.3f}, max={betas[col].max():.3f}\n")
print(f"[beta_estim.py] Saved Fama–French betas to {OUT_FP}")
