"""
Estimate Fama–French betas for each bank-year using ritrf (Rit − RFt) from annual_returns_clean.csv and monthly Fama–French factors.

Inputs:
  - data/clean/annual_returns_clean.csv (monthly, columns: instrument, date, ritrf, ...)
  - data/clean/fama_french_factors_clean.csv (columns: yyyymm, mkt_rf, smb, hml, rf)

Outputs:
  - data/model/bank_ff_betas_annual.csv (columns: instrument, year, beta_mkt, beta_smb, beta_hml, n_obs)
  - log: data/logs/ff_betas_annual_log.txt
"""
import pandas as pd
import numpy as np
from pathlib import Path
import statsmodels.api as sm

RETURNS_FP = Path('esg-default-risk-phase1/data/clean/annual_returns_clean.csv')
FACTORS_FP = Path('esg-default-risk-phase1/data/clean/fama_french_factors_clean.csv')
OUT_FP = Path('esg-default-risk-phase1/data/model/bank_ff_betas_annual.csv')
LOG_FP = Path('esg-default-risk-phase1/data/logs/ff_betas_annual_log.txt')

returns = pd.read_csv(RETURNS_FP)
factors = pd.read_csv(FACTORS_FP)

# Ensure date columns are monthly and aligned
def to_yyyymm(dt):
    return pd.to_datetime(dt).strftime('%Y%m')
returns['yyyymm'] = returns['date'].apply(to_yyyymm)
factors['yyyymm'] = factors['yyyymm'].astype(str)

# Only use years 2016–2023
returns['year'] = pd.to_datetime(returns['date']).dt.year
returns = returns[(returns['year'] >= 2016) & (returns['year'] <= 2023)]

results = []
insufficient = []

for (instrument, year), group in returns.groupby(['instrument', 'year']):
    merged = pd.merge(group, factors, on='yyyymm', how='inner', suffixes=('', '_ff'))
    if len(merged) < 6:
        insufficient.append((instrument, year, len(merged)))
        continue
    X = merged[['mkt_rf', 'smb', 'hml']]
    y = merged['ritrf']
    X = sm.add_constant(X)
    try:
        model = sm.OLS(y, X).fit()
        beta_mkt = model.params.get('mkt_rf', np.nan)
        beta_smb = model.params.get('smb', np.nan)
        beta_hml = model.params.get('hml', np.nan)
    except Exception as e:
        insufficient.append((instrument, year, len(merged), str(e)))
        continue
    results.append({
        'instrument': instrument,
        'year': year,
        'beta_mkt': beta_mkt,
        'beta_smb': beta_smb,
        'beta_hml': beta_hml,
        'n_obs': len(merged)
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
print(f"[estimate_ff_betas_annual.py] Saved Fama–French betas to {OUT_FP}") 