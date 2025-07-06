"""
Filters the market cap file to only include one row per (Ticker, year) for 2016-2023, using the last available date on or before December 31st of each year for each ticker.
Inputs: esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv
Outputs: esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv (overwritten)
Log: prints summary to terminal
"""
import pandas as pd
from pathlib import Path

INPUT = Path('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv')

mc = pd.read_csv(INPUT)
mc['Date'] = pd.to_datetime(mc['Date'])
mc = mc[(mc['Date'].dt.year >= 2016) & (mc['Date'].dt.year <= 2023)]

# For each Ticker and year, keep the row with the latest date on or before Dec 31
filtered = (
    mc.assign(year=mc['Date'].dt.year)
      .sort_values(['Ticker', 'Date'])
      .groupby(['Ticker', 'year'], as_index=False)
      .apply(lambda df: df[df['Date'] <= pd.Timestamp(f"{df['year'].iloc[0]}-12-31")].tail(1))
      .reset_index(drop=True)
)
filtered = filtered.drop(columns=['year'])
filtered = filtered.sort_values(['Ticker', 'Date'])
filtered.to_csv(INPUT, index=False)
print(f"Filtered market cap file saved with {len(filtered)} rows.") 