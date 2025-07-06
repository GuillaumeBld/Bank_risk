"""
Calculate and save annualized equity volatility for each bank and year from monthly returns.

Inputs:
- data/clean/bank_monthly_total_returns_2016_2023.csv
Outputs:
- data/clean/bank_annual_equity_vol.csv (columns: Bank, Year, equity_vol)
"""
import pandas as pd

# Load monthly returns
returns_fp = 'esg-default-risk-phase1/data/clean/bank_monthly_total_returns_2016_2023.csv'
df = pd.read_csv(returns_fp)
df = df.set_index('Bank')

# Parse columns as dates, group by year, calculate annualized vol
col_years = pd.to_datetime(df.columns, errors='coerce').year
unique_years = sorted(set(col_years.dropna().astype(int)))

def annualized_vol(row):
    vols = []
    for y in unique_years:
        mask = col_years == y
        vals = row[mask].astype(float)
        vols.append(vals.std() * (12 ** 0.5))
    return pd.Series(vols, index=unique_years)

df_annual_vol = df.apply(annualized_vol, axis=1)
df_annual_vol['Bank'] = df.index
df_annual_vol = df_annual_vol.reset_index(drop=True)
df_melt = df_annual_vol.melt(id_vars='Bank', var_name='Year', value_name='equity_vol')
df_melt.to_csv('esg-default-risk-phase1/data/clean/bank_annual_equity_vol.csv', index=False)
print('Saved annualized equity volatility to data/clean/bank_annual_equity_vol.csv') 