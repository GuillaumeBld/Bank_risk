"""
DD and PD Calculation Using Market Equity Data (Merton Model)
Market capitalization figures are scaled to millions of dollars to match the accounting data.

Inputs:
- data/clean/annual_returns_clean.csv (main input; monetary values in millions of USD)
- data/clean/all_banks_marketcap_2016_2023.csv (monthly, with close prices)

Outputs:
- data/model/modeling_data_with_dd_pd_market.csv (DD and PD using market equity)
- Log: data/logs/dd_pd_market_log.txt
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import root
from pathlib import Path
import logging

model_fp = Path('esg-default-risk-phase1/data/clean/annual_returns_clean.csv')
log_fp = Path('esg-default-risk-phase1/data/logs/dd_pd_market_log.txt')
output_fp = Path('esg-default-risk-phase1/data/model/modeling_data_with_dd_pd_market.csv')

T = 1.0

# Load data
print('[INFO] Loading annual returns...')
df = pd.read_csv(model_fp)

# Compute risk-free rate as rf = rit - ritrf
if 'rit' in df.columns and 'ritrf' in df.columns:
    df['rf'] = df['rit'] - df['ritrf']
else:
    raise ValueError('Columns rit and ritrf must be present in the input file.')

df['Year'] = pd.to_datetime(df['date']).dt.year

def get_prefix(ticker):
    if pd.isna(ticker):
        return None
    return str(ticker).split('.')[0]

# Load updated monthly market cap file
marketcap = pd.read_csv('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv')
# Convert market capitalization to millions of dollars so that it matches the
# scale of the accounting variables (which are reported in millions USD)
marketcap['market_cap'] = (
    marketcap['dec_price'] * marketcap['shares_outstanding'] / 1_000_000
)
marketcap['ticker_prefix'] = marketcap['symbol'].apply(get_prefix)

# Load annualized equity volatility
vol_fp = 'esg-default-risk-phase1/data/clean/bank_annual_equity_vol.csv'
equity_vol = pd.read_csv(vol_fp)
equity_vol['Year'] = equity_vol['Year'].astype(int)
# Standardize symbol column for merge
if 'symbol' not in equity_vol.columns:
    equity_vol['symbol'] = equity_vol['Bank'].apply(lambda x: str(x).split('.')[0])

# Prepare modeling data for merge
df['ticker_prefix'] = df['instrument'].apply(get_prefix)
df['date'] = pd.to_datetime(df['date'])
df['Month'] = df['date'].dt.month
df['symbol'] = df['instrument'].apply(lambda x: str(x).split('.')[0])
marketcap['fiscal_date'] = pd.to_datetime(marketcap['fiscal_date'])
marketcap['Year'] = marketcap['fiscal_date'].dt.year
marketcap['Month'] = marketcap['fiscal_date'].dt.month
df = df.merge(marketcap[['symbol', 'Year', 'Month', 'market_cap']], on=['symbol', 'Year', 'Month'], how='left', suffixes=('', '_mcap'))

# Market cap fallback
if 'market_cap' not in df.columns:
    if 'share_price' in df.columns and 'shares_outstanding' in df.columns:
        df['market_cap'] = (
            df['share_price'] * df['shares_outstanding'] / 1_000_000
        )
        market_cap_source = 'share_price * shares_outstanding (millions)'
    else:
        df['market_cap'] = 'Marketcap_missing'
        market_cap_source = 'missing (set to Marketcap_missing)'
else:
    market_cap_source = 'market_cap column present'

# === Ensure debt is expressed in millions of dollars ===
# Values in `annual_returns_clean.csv` are already reported in millions USD, so
# no additional scaling is required. Keep the column as numeric for the solver.
df['debt__total'] = pd.to_numeric(df['debt__total'], errors='coerce')

# Merge in equity volatility
merge_cols = ['symbol', 'Year']
df = df.merge(equity_vol[['symbol', 'Year', 'equity_vol']], on=merge_cols, how='left')

# Use observed equity volatility, fallback to 0.25 if missing
sigma = 0.25
def get_equity_vol(row):
    if not np.isnan(row['equity_vol']):
        return row['equity_vol']
    return sigma

df['equity_vol'] = df.apply(get_equity_vol, axis=1)

# 2. Merton model estimation using a numerical root solver
def merton_solver(row, T=T):
    rf = row['rf']
    E = row['market_cap']
    F = row['debt__total']
    sigma_E = row['equity_vol']
    if np.isnan(E) or np.isnan(F) or np.isnan(sigma_E) or E <= 0 or F < 0 or sigma_E <= 0:
        return np.nan, np.nan, 'input_nan_or_invalid'
    if F == 0:
        # Zero debt implies infinite distance to default; return equity values directly
        return E, sigma_E, 'no_debt'

    def equations(x):
        V, sigma_V = x
        d1 = (np.log(V / F) + (rf + 0.5 * sigma_V ** 2) * T) / (sigma_V * np.sqrt(T))
        d2 = d1 - sigma_V * np.sqrt(T)
        eq1 = V * norm.cdf(d1) - F * np.exp(-rf * T) * norm.cdf(d2) - E
        eq2 = sigma_E - (V / E) * norm.cdf(d1) * sigma_V
        return [eq1, eq2]

    try:
        sol = root(equations, [E + F, sigma_E], method='hybr')
        if sol.success:
            return sol.x[0], sol.x[1], 'converged'
        else:
            return np.nan, np.nan, 'not_converged'
    except Exception as e:
        return np.nan, np.nan, f'error: {e}'

print('[INFO] Running Merton solver for each bank-year...')
results = df.apply(merton_solver, axis=1)
df['asset_value'], df['asset_vol'], df['merton_status'] = zip(*results)

df['distance_to_default'] = (
    np.log(df['asset_value'] / df['debt__total']) + (df['rf'] - 0.5 * df['asset_vol'] ** 2) * T
) / (df['asset_vol'] * np.sqrt(T))
df['probability_of_default'] = norm.cdf(-df['distance_to_default'])

df.to_csv(output_fp, index=False)

with open(log_fp, 'w') as log:
    log.write(f"DD/PD calculated for {len(df)} rows\n")
    log.write(f"Market cap source: {market_cap_source}\n")
    log.write(f"Rows with NaN equity_vol: {df['equity_vol'].isna().sum()}\n")
    log.write(f"Rows with failed Merton convergence: {(df['merton_status'] == 'not_converged').sum()}\n")
    log.write(f"Rows with error in Merton: {df['merton_status'].str.startswith('error').sum()}\n")
    log.write(f"Rows with NaN DD: {df['distance_to_default'].isna().sum()}\n")
    log.write(f"Rows with NaN PD: {df['probability_of_default'].isna().sum()}\n")
    log.write(str(df[['distance_to_default', 'probability_of_default']].describe()))
    log.write('\nRows with missing/failed estimation: %d\n' % df['distance_to_default'].isna().sum())
    log.write('\nSample of failed rows (first 5):\n')
    log.write(str(df[df['distance_to_default'].isna()].head()))

print("[INFO] Market-based DD/PD calculation complete. See log for diagnostics.") 