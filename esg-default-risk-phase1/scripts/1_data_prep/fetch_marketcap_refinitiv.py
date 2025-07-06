"""
Fetches annual market cap and shares outstanding for all banks in the modeling dataset using Refinitiv Workspace API.
Inputs: esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv
Outputs: esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2020_refinitiv.csv
Log: esg-default-risk-phase1/data/logs/marketcap_refinitiv_log.txt
"""
import pandas as pd
import pathlib
from datetime import datetime
import time

# Refinitiv Workspace SDK imports
import refinitiv.data as rd

API_KEY = 'ccb11cd4eb384a4c957124f87d10f1e0807803d1'
DATA_PATH = pathlib.Path('esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv')
OUTPUT_PATH = pathlib.Path('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2020_refinitiv.csv')
LOG_PATH = pathlib.Path('esg-default-risk-phase1/data/logs/marketcap_refinitiv_log.txt')
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Load tickers
raw = pd.read_csv(DATA_PATH)
tickers = sorted(set(raw['Instrument'].dropna().unique()))
years = list(range(2016, 2021))
target_dates = [datetime(y, 12, 31) for y in years]

# Authenticate
rd.open_session(app_key=API_KEY)

records = []
with open(LOG_PATH, 'w') as log:
    for ticker in tickers:
        ric = ticker  # Adjust if needed for Refinitiv format
        for target in target_dates:
            try:
                # Fetch close price and shares outstanding as of target date
                response = rd.get_history(
                    universe=ric,
                    fields=['TR.CLOSEPRICE', 'TR.SHARESOUT'],
                    interval='daily',
                    start=target.strftime('%Y-%m-%d'),
                    end=target.strftime('%Y-%m-%d')
                )
                if response.empty:
                    log.write(f"No data for {ric} on {target.date()}\n")
                    continue
                row = response.iloc[-1]
                close = row.get('TR.CLOSEPRICE', None)
                shares = row.get('TR.SHARESOUT', None)
                if close is None or shares is None:
                    log.write(f"Missing data for {ric} on {target.date()}\n")
                    continue
                records.append({
                    'Ticker': ticker,
                    'Date': target.date(),
                    'Close': close,
                    'SharesOutstanding': shares,
                    'MarketCap': close * shares
                })
                log.write(f"Fetched {ric} {target.date()}\n")
                time.sleep(1)  # Be polite to API
            except Exception as e:
                log.write(f"Error fetching {ric} {target.date()}: {e}\n")

result = pd.DataFrame(records)
result.to_csv(OUTPUT_PATH, index=False)
with open(LOG_PATH, 'a') as log:
    log.write(f'Saved → {OUTPUT_PATH}\n')
print(f'Saved → {OUTPUT_PATH}') 