"""
Fetches annual market cap and shares outstanding for all banks in the modeling dataset using Finnhub API.
Inputs: esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv
Outputs: esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2020_finnhub.csv
Log: esg-default-risk-phase1/data/logs/marketcap_finnhub_log.txt
"""
import requests
import pandas as pd
import pathlib
import time
from datetime import datetime, timedelta

API_KEY = 'cv2kmkhr01qhefskt9f0cv2kmkhr01qhefskt9fg'
DATA_PATH = pathlib.Path('esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv')
OUTPUT_PATH = pathlib.Path('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2020_finnhub.csv')
LOG_PATH = pathlib.Path('esg-default-risk-phase1/data/logs/marketcap_finnhub_log.txt')
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

raw = pd.read_csv(DATA_PATH)
tickers = sorted(set(raw['Instrument'].dropna().unique()))
years = list(range(2016, 2021))

records = []
with open(LOG_PATH, 'w') as log:
    for ticker in tickers:
        finnhub_ticker = ticker.split('.')[0]  # Remove .N, .OQ, etc.
        for year in years:
            target_date = datetime(year, 12, 31)
            # Find the last trading day on or before Dec 31
            # Use /stock/candle endpoint to get close price
            candle_url = f'https://finnhub.io/api/v1/stock/candle'
            params = {
                'symbol': finnhub_ticker,
                'resolution': 'D',
                'from': int((target_date - timedelta(days=7)).timestamp()),
                'to': int(target_date.timestamp()),
                'token': API_KEY
            }
            try:
                r = requests.get(candle_url, params=params)
                data = r.json()
                if data.get('s') != 'ok' or not data.get('c'):
                    log.write(f"No price data for {ticker} {year}\n")
                    continue
                # Get the last available close price
                close = data['c'][-1]
                # Get shares outstanding and market cap (latest available)
                metric_url = f'https://finnhub.io/api/v1/stock/metric'
                metric_params = {
                    'symbol': finnhub_ticker,
                    'metric': 'all',
                    'token': API_KEY
                }
                r2 = requests.get(metric_url, params=metric_params)
                metrics = r2.json().get('metric', {})
                shares = metrics.get('sharesOutstanding', None)
                marketcap = metrics.get('marketCapitalization', None)
                if shares is None:
                    log.write(f"No shares outstanding for {ticker} {year}\n")
                    continue
                # If market cap is not available, calculate it
                if marketcap is None and close is not None:
                    marketcap = close * shares
                records.append({
                    'Ticker': ticker,
                    'Year': year,
                    'Close': close,
                    'SharesOutstanding': shares,
                    'MarketCap': marketcap
                })
                log.write(f"Fetched {ticker} {year}\n")
                time.sleep(1)  # Be polite to API
            except Exception as e:
                log.write(f"Error fetching {ticker} {year}: {e}\n")

result = pd.DataFrame(records)
result.to_csv(OUTPUT_PATH, index=False)
with open(LOG_PATH, 'a') as log:
    log.write(f'Saved → {OUTPUT_PATH}\n')
print(f'Saved → {OUTPUT_PATH}') 