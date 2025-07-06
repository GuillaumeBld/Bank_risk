"""
This script computes the market capitalization for all banks for each year using:
- Outstanding shares: data/clean/bank_outstanding_shares_full_panel_2016_2023.csv
- End-of-year closing price: data/clean/bank_monthly_total_returns_2016_2023.csv (wide format)

Inputs:
  - data/clean/bank_outstanding_shares_full_panel_2016_2023.csv
  - data/clean/bank_monthly_total_returns_2016_2023.csv
Outputs:
  - data/clean/all_banks_marketcap_2016_2023.csv
Log:
  - data/logs/compute_marketcap_from_shares_and_returns_log.txt
"""
import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), '../../data/clean')
FILE_SHARES = os.path.join(BASE, 'bank_outstanding_shares_full_panel_2016_2023.csv')
FILE_RETURNS = os.path.join(BASE, 'bank_monthly_total_returns_2016_2023.csv')
OUT_FILE = os.path.join(BASE, 'all_banks_marketcap_2016_2023.csv')
LOG_FILE = os.path.join(BASE.replace('clean', 'logs'), 'compute_marketcap_from_shares_and_returns_log.txt')

# Load data
shares = pd.read_csv(FILE_SHARES)
returns = pd.read_csv(FILE_RETURNS)

# Ensure year columns are int
def to_int(x):
    try:
        return int(x)
    except:
        return pd.NA
shares['year'] = shares['year'].apply(to_int)

# Prepare returns: melt to long format
returns_long = returns.melt(id_vars=['Bank'], var_name='fiscal_date', value_name='dec_price')
# Extract year from fiscal_date (e.g., '12/31/16' -> 2016)
returns_long['year2d'] = returns_long['fiscal_date'].str.extract(r'(\d{2})$')[0]
returns_long['year'] = returns_long['year2d'].astype(int) + 2000
# Extract base symbol robustly
returns_long['symbol'] = returns_long['Bank'].str.split('.', n=1).str[0]

# Drop rows with missing year or symbol
returns_long = returns_long.dropna(subset=['year', 'symbol'])

# Ensure year is int in both
returns_long['year'] = returns_long['year'].astype(int)
shares['year'] = shares['year'].astype(int)

# Log unmatched pairs before merge
shares_pairs = set(zip(shares['symbol'], shares['year']))
returns_pairs = set(zip(returns_long['symbol'], returns_long['year']))

unmatched_in_returns = shares_pairs - returns_pairs
unmatched_in_shares = returns_pairs - shares_pairs

with open(LOG_FILE, 'w') as f:
    f.write(f"Unmatched (symbol, year) pairs in shares but not in returns: {len(unmatched_in_returns)}\n")
    for s, y in sorted(unmatched_in_returns):
        f.write(f"  {s}, {y}\n")
    f.write(f"\nUnmatched (symbol, year) pairs in returns but not in shares: {len(unmatched_in_shares)}\n")
    for s, y in sorted(unmatched_in_shares):
        f.write(f"  {s}, {y}\n")

# Merge on symbol and year
merged = pd.merge(shares, returns_long, on=['symbol', 'year'], how='inner')

# Compute market cap
merged['market_cap'] = merged['shares_outstanding'] * merged['dec_price']

# Ensure fiscal_date is in the format YYYY-12-31
merged['fiscal_date'] = merged['year'].astype(str) + '-12-31'

# Output only the required columns
merged[['symbol', 'year', 'fiscal_date', 'shares_outstanding', 'dec_price', 'market_cap']].to_csv(OUT_FILE, index=False)

# Append merge summary to log
with open(LOG_FILE, 'a') as f:
    f.write(f"\nComputed market cap for {len(merged)} bank-year pairs.\n")
    f.write(f"Columns: {list(merged.columns)}\n")
    f.write(f"Sample:\n{merged.head()}\n")

print(f"Market cap file saved to {OUT_FILE}")
print(f"Log written to {LOG_FILE}") 