"""
Final Quality DD/PD Calculation Without Proxies

Inputs:
- /data/model/modeling_data_with_wacc.csv
- /data/clean/bank_monthly_total_returns_2016_2023.csv

Outputs:
- /data/model/modeling_data_with_dd_pd.csv
- Log: /data/logs/dd_pd_final_log.txt
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
from pathlib import Path
import logging

model_fp = Path('esg-default-risk-phase1/data/model/modeling_data_with_wacc.csv')
returns_fp = Path('esg-default-risk-phase1/data/clean/bank_monthly_total_returns_2016_2023.csv')
log_fp = Path('esg-default-risk-phase1/data/logs/dd_pd_final_log.txt')

T = 1.0
rf = 0.03

# Load data
print('[INFO] Loading modeling and returns data...')
df = pd.read_csv(model_fp)
returns = pd.read_csv(returns_fp)

# Load updated monthly market cap file
marketcap = pd.read_csv('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv')

# Calculate market cap as dec_price * shares_outstanding
marketcap['market_cap'] = marketcap['dec_price'] * marketcap['shares_outstanding']

# Add a 'ticker_prefix' column for matching (before '.')
def get_prefix(ticker):
    if pd.isna(ticker):
        return None
    return str(ticker).split('.')[0]

df['ticker_prefix'] = df['instrument'].apply(get_prefix)
marketcap['ticker_prefix'] = marketcap['symbol'].apply(get_prefix)

# Prepare modeling data for merge
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month
else:
    raise ValueError('Modeling data must have a date column for market cap merge.')

# Merge market cap by symbol, year, and fiscal_date
# First, create 'symbol' in df from 'instrument' (by splitting at '.')
df['symbol'] = df['instrument'].apply(lambda x: str(x).split('.')[0])
df['date'] = pd.to_datetime(df['date'])
marketcap['fiscal_date'] = pd.to_datetime(marketcap['fiscal_date'])
df = df.merge(marketcap[['symbol', 'year', 'fiscal_date', 'market_cap']], left_on=['symbol', 'Year', 'date'], right_on=['symbol', 'year', 'fiscal_date'], how='left', suffixes=('', '_mcap'))
df['market_cap'] = df['market_cap']
df.drop(['market_cap'], axis=1, inplace=False)

# Handle new wide format: first column is 'Bank', rest are dates
returns_long = returns.melt(id_vars='Bank', var_name='fiscal_date', value_name='Return')
returns_long = returns_long.rename(columns={'Bank': 'instrument'})
returns_long['fiscal_date'] = pd.to_datetime(returns_long['fiscal_date'], format='%m/%d/%y')
returns_long['Year'] = returns_long['fiscal_date'].dt.year
returns_long['Month'] = returns_long['fiscal_date'].dt.month

# For returns_long, add ticker_prefix for matching in volatility assignment
returns_long['ticker_prefix'] = returns_long['instrument'].apply(get_prefix)

# --- NEW: Merge monthly returns date into main df so each row gets the correct monthly date ---
df = df.merge(
    returns_long[['instrument', 'Year', 'Month', 'fiscal_date']],
    on=['instrument', 'Year', 'Month'],
    how='left',
    suffixes=('', '_monthly')
)
# Overwrite the 'date' column with the monthly date from returns
df['date'] = df['fiscal_date']
del df['fiscal_date']

# Market cap fallback
if 'market_cap' not in df.columns:
    if 'share_price' in df.columns and 'shares_outstanding' in df.columns:
        df['market_cap'] = df['share_price'] * df['shares_outstanding']
        market_cap_source = 'share_price * shares_outstanding'
    else:
        # Tag missing market cap with a string for easier diagnostics
        df['market_cap'] = 'Marketcap_missing'
        market_cap_source = 'missing (set to Marketcap_missing)'
else:
    market_cap_source = 'market_cap column present'

# === Apply debt scaling: convert debt__total from thousands to dollars ===
df['debt__total'] = df['debt__total'] * 1_000

# 1. Calculate equity volatility for each bank-year
print('[INFO] Calculating annualized equity volatility for each bank-year...')
vol_dict = {}
insufficient_returns = set()
for prefix, group in returns_long.groupby('ticker_prefix'):
    for year, year_group in group.groupby('Year'):
        if len(year_group) < 6:
            insufficient_returns.add((prefix, year))
            continue
        log_returns = np.log(year_group['Return'] + 1)
        monthly_vol = log_returns.std()
        vol_dict[(prefix, year)] = monthly_vol * np.sqrt(12)

def get_equity_vol(row):
    key = (row['ticker_prefix'], pd.to_datetime(row['date']).year)
    return vol_dict.get(key, np.nan)

df['equity_vol'] = df.apply(get_equity_vol, axis=1)

# 2. Merton model iterative estimation
def merton_solver(row, rf=rf, T=T, tol=1e-6, max_iter=100):
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

# === Diagnostic: Print sample volatility and asset/debt values ===
sample = df.sample(n=5, random_state=42)
for idx, row in sample.iterrows():
    vol = row.get('asset_vol', np.nan)
    print(f"[DIAG] Firm {row['instrument']} ({row['Year']}): asset_vol = {vol}")
sample2 = df[['instrument','Year','asset_value','debt__total']].sample(n=5, random_state=24)
print("[DIAG] Checking scales for asset/debt:")
print(sample2.to_string(index=False))

# === Diagnostics: NaN counts and summary stats ===
nan_asset_value = df['asset_value'].isna().sum()
nan_debt = df['debt__total'].isna().sum()
nan_asset_vol = df['asset_vol'].isna().sum() if 'asset_vol' in df.columns else -1
print(f"[DIAG] NaN counts: asset_value={nan_asset_value}, debt__total={nan_debt}, asset_vol={nan_asset_vol}")
print("[DIAG] asset_value summary:")
print(df['asset_value'].describe())
print("[DIAG] debt__total summary:")
print(df['debt__total'].describe())
if 'asset_vol' in df.columns:
    print("[DIAG] asset_vol summary:")
    print(df['asset_vol'].describe())

# === Placeholder: Align units if needed ===
# Uncomment and adjust if you confirm a unit mismatch
# df['debt__total'] *= 1_000

# === Placeholder: Annualize volatility correctly ===
# If asset_vol is monthly, use np.sqrt(12); if daily, use np.sqrt(252)
# Uncomment and adjust if needed
# df['asset_vol'] = df['asset_vol_raw'] * np.sqrt(12)

# === Print a larger sample for review ===
sample3 = df[['instrument','Year','asset_value','debt__total','asset_vol']].sample(n=10, random_state=123)
print("[DIAG] Sample asset_value, debt__total, asset_vol:")
print(sample3.to_string(index=False))

# === Print first 10 missing rows for asset_value or asset_vol ===
missing = df[df['asset_value'].isna() | df['asset_vol'].isna()]
print("First 10 rows with missing asset inputs:")
print(missing[['instrument','Year']].drop_duplicates().head(10).to_string(index=False))

# === DTD/PD calculation using book total assets and total debt ===
def safe_dd(row):
    try:
        # Use book total assets and total debt for DTD calculation
        if (
            np.isnan(row['total_assets']) or np.isnan(row['asset_vol']) or
            row['total_assets'] <= 0 or row['asset_vol'] <= 0 or row['debt__total'] <= 0
        ):
            return np.nan
        return (
            np.log(row['total_assets'] / row['debt__total']) + (rf - 0.5 * row['asset_vol'] ** 2) * T
        ) / (row['asset_vol'] * np.sqrt(T))
    except Exception:
        return np.nan

# Apply the updated DTD calculation
df['distance_to_default'] = df.apply(safe_dd, axis=1)
df['probability_of_default'] = norm.cdf(-df['distance_to_default'])

# 4. Save and log
df.to_csv(model_fp.with_name('modeling_data_with_dd_pd.csv'), index=False)

with open(log_fp, 'w') as log:
    log.write(f"DD/PD calculated for {len(df)} rows\n")
    log.write(f"Market cap source: {market_cap_source}\n")
    log.write(f"Rows with insufficient returns for volatility: {len(insufficient_returns)}\n")
    log.write(f"Rows with NaN equity_vol: {df['equity_vol'].isna().sum()}\n")
    log.write(f"Rows with failed Merton convergence: {(df['merton_status'] == 'not_converged').sum()}\n")
    log.write(f"Rows with error in Merton: {df['merton_status'].str.startswith('error').sum()}\n")
    log.write(f"Rows with NaN DD: {df['distance_to_default'].isna().sum()}\n")
    log.write(f"Rows with NaN PD: {df['probability_of_default'].isna().sum()}\n")
    log.write(str(df[['distance_to_default', 'probability_of_default']].describe()))
    log.write('\nRows with missing/failed estimation: %d\n' % df['distance_to_default'].isna().sum())
    log.write('\nSample of failed rows (first 5):\n')
    log.write(str(df[df['distance_to_default'].isna()].head()))

print("[INFO] Final DD/PD calculation complete. See log for diagnostics.")

# Load cleaned annual returns data for backfilling missing values
annual_clean_fp = Path('esg-default-risk-phase1/data/clean/annual_returns_clean.csv')
annual_clean = pd.read_csv(annual_clean_fp)
annual_clean['date'] = pd.to_datetime(annual_clean['date'])

# Standardize column names for merging
annual_clean = annual_clean.rename(columns={
    'total_assets': 'total_assets_clean',
    'debt__total': 'debt__total_clean',
    'rit': 'rit_clean',
    'instrument': 'instrument_clean'
})

# Merge cleaned annual returns into modeling data on instrument/date
merge_cols = ['instrument', 'date'] if 'date' in df.columns else ['instrument', 'Year']
df = df.merge(
    annual_clean[['instrument_clean', 'date', 'total_assets_clean', 'debt__total_clean', 'rit_clean']],
    left_on=['instrument', 'date'],
    right_on=['instrument_clean', 'date'],
    how='left'
)

# Fill missing total_assets and debt__total from clean file
for col in ['total_assets', 'debt__total']:
    clean_col = f'{col}_clean'
    if clean_col in df.columns:
        df[col] = df[col].combine_first(df[clean_col])

# Optionally, fill asset_vol from rit_clean if needed (e.g., use rit_clean as proxy for volatility)

# Add columns 'Year' and 'Month' to the marketcap DataFrame, derived from the 'fiscal_date' column, before merging
marketcap['fiscal_date'] = pd.to_datetime(marketcap['fiscal_date'])
marketcap['Year'] = marketcap['fiscal_date'].dt.year
marketcap['Month'] = marketcap['fiscal_date'].dt.month