"""
This script expands the annual market cap data to monthly frequency using the monthly dates from the returns data, and merges in the monthly close price for each bank and month.
Inputs: data/clean/all_banks_marketcap_2016_2023.csv, data/clean/bank_monthly_total_returns_2016_2023.csv, data/raw/bank_monthly_close_prices_2016_2023.csv
Outputs: data/clean/all_banks_marketcap_2016_2023.csv (overwritten, now monthly)
Log: data/logs/update_marketcap_to_monthly_log.txt
"""
import pandas as pd
import numpy as np

# Load data
mcap = pd.read_csv('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv')
returns = pd.read_csv('esg-default-risk-phase1/data/clean/bank_monthly_total_returns_2016_2023.csv')
close_prices = pd.read_csv('esg-default-risk-phase1/data/raw/bank_monthly_close_prices_2016_2023.csv')

# Get monthly dates from returns columns (skip 'Bank' column)
monthly_dates = pd.to_datetime(returns.columns[1:], format='%m/%d/%y')

# Prepare new rows
new_rows = []
for symbol in mcap['symbol'].unique():
    for year in mcap[mcap['symbol'] == symbol]['year'].unique():
        # Get annual shares_outstanding for this bank-year
        shares = mcap[(mcap['symbol'] == symbol) & (mcap['year'] == year)]['shares_outstanding'].iloc[0]
        # For each month in the year, create a row
        for date in monthly_dates:
            if date.year == year:
                row = {
                    'symbol': symbol,
                    'year': year,
                    'fiscal_date': date.strftime('%Y-%m-%d'),
                    'shares_outstanding': shares,
                    'dec_price': np.nan,
                    'market_cap': np.nan
                }
                new_rows.append(row)

# Create new DataFrame
new_mcap = pd.DataFrame(new_rows)

# Merge in monthly close price
close_prices_long = close_prices.melt(id_vars='Date', var_name='symbol', value_name='dec_price')
close_prices_long['fiscal_date'] = pd.to_datetime(close_prices_long['Date'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')
close_prices_long = close_prices_long.drop(columns=['Date'])

# Standardize symbol: remove suffix after '.' for merging
close_prices_long['symbol'] = close_prices_long['symbol'].str.split('.').str[0]

# Merge close price into new_mcap
new_mcap = new_mcap.merge(close_prices_long, on=['symbol', 'fiscal_date'], how='left', suffixes=('', '_close'))
# If dec_price from close is present, use it
new_mcap['dec_price'] = new_mcap['dec_price_close'].combine_first(new_mcap['dec_price'])
new_mcap = new_mcap.drop(columns=['dec_price_close'])

# Save to CSV
new_mcap.to_csv('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv', index=False)

# Log
with open('esg-default-risk-phase1/data/logs/update_marketcap_to_monthly_log.txt', 'w') as f:
    f.write('Market cap file expanded to monthly and close prices merged.\n') 