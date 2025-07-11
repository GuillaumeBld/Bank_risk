"""
Fetches annual market cap for all banks in the modeling dataset using yfinance.
Inputs: esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv
Outputs: esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv
Log: esg-default-risk-phase1/data/logs/marketcap_script_log.txt
"""
import yfinance as yf
import pandas as pd
import pathlib
import sys
from datetime import datetime, timedelta

DATA_PATH = pathlib.Path('esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv')
LOG_PATH = pathlib.Path('esg-default-risk-phase1/data/logs/marketcap_script_log.txt')
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = pathlib.Path('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023_yf.csv')

# 1️⃣ Load unique tickers from the main data file
df = pd.read_csv(DATA_PATH)
tickers = sorted(set(df['Instrument'].dropna().unique()))

# 2️⃣ Define target years
years = list(range(2016, 2024))
target_dates = [datetime(y, 12, 31) for y in years]

records = []
with open(LOG_PATH, 'w') as log:
    for ticker in tickers:
        try:
            yf_ticker = ticker.split('.')[0]  # Remove .N, .OQ, etc. for yfinance
            t = yf.Ticker(yf_ticker)
            hist = t.history(start='2016-01-01', end='2024-01-10', interval='1d')
            shares = t.info.get('sharesOutstanding', None)
            if hist.empty or shares is None:
                log.write(f"No data for {ticker}\n")
                continue
            hist = hist.reset_index()
            hist['Date'] = pd.to_datetime(hist['Date'])
            for target in target_dates:
                # Find the last available trading day on or before Dec 31
                subset = hist[hist['Date'] <= target]
                if subset.empty:
                    log.write(f"No price for {ticker} on or before {target.date()}\n")
                    continue
                last_row = subset.iloc[-1]
                close = last_row['Close']
                records.append({
                    'Ticker': ticker,
                    'Date': target.date(),
                    'Close': close,
                    'SharesOutstanding': shares,
                    'MarketCap': close * shares if shares is not None else None
                })
        except Exception as e:
            log.write(f"Error fetching {ticker}: {e}\n")

result = pd.DataFrame(records)
result.to_csv(OUTPUT_PATH, index=False)
with open(LOG_PATH, 'a') as log:
    log.write(f'Saved → {OUTPUT_PATH}\n')
print(f'Saved → {OUTPUT_PATH}') 