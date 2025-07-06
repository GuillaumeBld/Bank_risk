"""
Fetches annual market cap for all banks in the modeling dataset using Alpha Vantage.
Inputs: esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv
Outputs: esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2020_av.csv
Log: esg-default-risk-phase1/data/logs/marketcap_alpha_vantage_log.txt
"""
import requests
import pandas as pd
import pathlib
import time
from datetime import datetime

API_KEY = 'KZLYWQZPWG2HMPN0'
DATA_PATH = pathlib.Path('esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv')
OUTPUT_PATH = pathlib.Path('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2020_av.csv')
LOG_PATH = pathlib.Path('esg-default-risk-phase1/data/logs/marketcap_alpha_vantage_log.txt')
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)
tickers = sorted(set(df['Instrument'].dropna().unique()))
years = list(range(2016, 2021))  # Only 2016 to 2020 inclusive
target_dates = [datetime(y, 12, 31) for y in years]

records = []
with open(LOG_PATH, 'w') as log:
    for ticker in tickers:
        av_ticker = ticker.split('.')[0]
        try:
            # 1. Get monthly adjusted close prices
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={av_ticker}&apikey={API_KEY}'
            r = requests.get(url)
            data = r.json()
            if 'Monthly Adjusted Time Series' not in data:
                log.write(f"No price data for {ticker}: {data.get('Note', data)}\n")
                continue
            monthly = data['Monthly Adjusted Time Series']
            # Convert to DataFrame
            monthly_df = pd.DataFrame([
                {'Date': pd.to_datetime(date), 'Close': float(row['5. adjusted close'])}
                for date, row in monthly.items()
            ])
            monthly_df = monthly_df.sort_values('Date')
            # 2. Get shares outstanding (latest only)
            url2 = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={av_ticker}&apikey={API_KEY}'
            r2 = requests.get(url2)
            overview = r2.json()
            shares = overview.get('SharesOutstanding', None)
            if shares is not None:
                shares = int(shares)
            else:
                log.write(f"No shares outstanding for {ticker}\n")
                continue
            # 3. For each target year, get last available price on or before Dec 31
            for target in target_dates:
                subset = monthly_df[monthly_df['Date'] <= target]
                if subset.empty:
                    log.write(f"No price for {ticker} on or before {target.date()}\n")
                    continue
                last_row = subset.iloc[-1]
                records.append({
                    'Ticker': ticker,
                    'Date': target.date(),
                    'Close': last_row['Close'],
                    'SharesOutstanding': shares,
                    'MarketCap': last_row['Close'] * shares
                })
            log.write(f"Fetched {ticker}\n")
            time.sleep(13)  # Alpha Vantage free API: 5 requests/minute (12s/request); use 13s to be safe
        except Exception as e:
            log.write(f"Error fetching {ticker}: {e}\n")

result = pd.DataFrame(records)
result.to_csv(OUTPUT_PATH, index=False)
with open(LOG_PATH, 'a') as log:
    log.write(f'Saved → {OUTPUT_PATH}\n')
print(f'Saved → {OUTPUT_PATH}') 