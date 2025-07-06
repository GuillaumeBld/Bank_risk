"""
DD and PD Calculation Using Market Equity Data (Merton Model)

Inputs:
- data/clean/annual_returns_clean.csv (main input)
- data/clean/all_banks_marketcap_2016_2023.csv (monthly, with close prices)

Outputs:
- data/model/modeling_data_with_dd_pd_market.csv (DD and PD using market equity)
- Log: data/logs/dd_pd_market_log.txt
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
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
marketcap['market_cap'] = marketcap['dec_price'] * marketcap['shares_outstanding']
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
        df['market_cap'] = df['share_price'] * df['shares_outstanding']
        market_cap_source = 'share_price * shares_outstanding'
    else:
        df['market_cap'] = 'Marketcap_missing'
        market_cap_source = 'missing (set to Marketcap_missing)'
else:
    market_cap_source = 'market_cap column present'

# === Apply debt scaling: convert debt__total from thousands to dollars ===
df['debt__total'] = df['debt__total'] * 1_000

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

# 2. Merton model iterative estimation
def merton_solver(row, T=T, tol=1e-6, max_iter=100):
    rf = row['rf']
    E = row['market_cap']
    F = row['debt__total']
    sigma_E = row['equity_vol']
    if np.isnan(E) or np.isnan(F) or np.isnan(sigma_E) or E <= 0 or F <= 0 or sigma_E <= 0:
        return np.nan, np.nan, 'input_nan_or_invalid'
    V = E + F  # initial guess
    sigma_V = sigma_E
    for i in range(max_iter):
        try:
            d1 = (np.log(V / F) + (rf + 0.5 * sigma_V ** 2) * T) / (sigma_V * np.sqrt(T))
            d2 = d1 - sigma_V * np.sqrt(T)
            E_calc = V * norm.cdf(d1) - F * np.exp(-rf * T) * norm.cdf(d2)
            sigma_E_calc = (V * norm.cdf(d1) * sigma_V) / E_calc if E_calc != 0 else np.nan
            if np.abs(E - E_calc) < tol and np.abs(sigma_E - sigma_E_calc) < tol:
                return V, sigma_V, 'converged'
            V = V - (E_calc - E) * 0.5
            sigma_V = sigma_V - (sigma_E_calc - sigma_E) * 0.5
        except Exception as e:
            return np.nan, np.nan, f'error: {e}'
    return np.nan, np.nan, 'not_converged'

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