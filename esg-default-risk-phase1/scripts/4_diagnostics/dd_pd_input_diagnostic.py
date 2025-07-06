import pandas as pd
import numpy as np
from pathlib import Path
import os

# File paths
model_fp = Path('esg-default-risk-phase1/data/model/modeling_data_with_wacc.csv')
marketcap_fp = Path('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv')
returns_fp = Path('esg-default-risk-phase1/data/clean/bank_monthly_total_returns_2016_2023.csv')
output_dir = Path('esg-default-risk-phase1/outputs/tables')
output_dir.mkdir(parents=True, exist_ok=True)
output_csv = output_dir / 'dd_pd_input_diagnostic.csv'

# Helper for ticker prefix
def get_prefix(ticker):
    if pd.isna(ticker):
        return None
    return str(ticker).split('.')[0]

# Load modeling data
print('[INFO] Loading modeling data...')
df = pd.read_csv(model_fp)

# Merge in market cap
print('[INFO] Merging market cap...')
marketcap = pd.read_csv(marketcap_fp)
marketcap['Date'] = pd.to_datetime(marketcap['Date'])
marketcap['Year'] = marketcap['Date'].dt.year
marketcap['Month'] = marketcap['Date'].dt.month
marketcap['ticker_prefix'] = marketcap['Ticker'].apply(get_prefix)
df['ticker_prefix'] = df['instrument'].apply(get_prefix)
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month
else:
    raise ValueError('Modeling data must have a date column for market cap merge.')
df = df.merge(marketcap[['ticker_prefix', 'Year', 'Month', 'MarketCap']], on=['ticker_prefix', 'Year', 'Month'], how='left', suffixes=('', '_mcap'))
df['market_cap'] = df['MarketCap']
df.drop(['MarketCap'], axis=1, inplace=True)

# Merge in equity_vol (from returns)
print('[INFO] Calculating equity volatility...')
returns = pd.read_csv(returns_fp)
returns_long = returns.melt(id_vars='Bank', var_name='Date', value_name='Return')
returns_long = returns_long.rename(columns={'Bank': 'instrument'})
returns_long['Date'] = pd.to_datetime(returns_long['Date'], format='%m/%d/%y')
returns_long['Year'] = returns_long['Date'].dt.year
returns_long['ticker_prefix'] = returns_long['instrument'].apply(get_prefix)
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

# Diagnostics
print('[INFO] Running diagnostics...')
cond_market_cap = df['market_cap'].notna() & (df['market_cap'] > 0)
cond_debt = df['debt__total'].notna() & (df['debt__total'] > 0)
cond_equity_vol = df['equity_vol'].notna() & (df['equity_vol'] > 0)
cond_all = cond_market_cap & cond_debt & cond_equity_vol

total_rows = len(df)
fail_market_cap = (~cond_market_cap).sum()
fail_debt = (~cond_debt).sum()
fail_equity_vol = (~cond_equity_vol).sum()
fail_any = (~cond_all).sum()
pass_all = cond_all.sum()

print('\n=== DD/PD Input Diagnostic Summary ===')
print(f'Total rows: {total_rows}')
print(f'Rows with missing/non-positive market_cap: {fail_market_cap}')
print(f'Rows with missing/non-positive debt__total: {fail_debt}')
print(f'Rows with missing/non-positive equity_vol: {fail_equity_vol}')
print(f'Rows failing any input check: {fail_any}')
print(f'Rows passing all input checks: {pass_all}')

# Breakdown by bank and year
print('\nBreakdown by bank and year (top 10 with most failures):')
grouped = df.loc[~cond_all].groupby(['ticker_prefix', 'Year']).size().reset_index(name='n_failed')
top_failed = grouped.sort_values('n_failed', ascending=False).head(10)
print(top_failed)

# Save summary CSV
summary = pd.DataFrame({
    'total_rows': [total_rows],
    'fail_market_cap': [fail_market_cap],
    'fail_debt': [fail_debt],
    'fail_equity_vol': [fail_equity_vol],
    'fail_any': [fail_any],
    'pass_all': [pass_all]
})
summary.to_csv(output_csv, index=False)
print(f'\n[INFO] Summary saved to {output_csv}')

top_failed.to_csv(output_dir / 'dd_pd_input_diagnostic_top_failed.csv', index=False)
print(f'[INFO] Top failed breakdown saved to {output_dir / "dd_pd_input_diagnostic_top_failed.csv"}') 