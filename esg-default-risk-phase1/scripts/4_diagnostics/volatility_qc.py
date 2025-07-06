# ONE-OFF DIAGNOSTIC — safe to delete after use: scripts/diagnostics/
"""
Volatility QC script: Plots histograms and outputs summary stats for volatility columns.
Reads from data/model/final_model_data.csv and writes to data/logs/volatility_qc_stats.csv.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

MODEL = Path('esg-default-risk-phase1/data/model/final_model_data.csv')
LOG = Path('esg-default-risk-phase1/data/logs/volatility_qc_stats.csv')

# Load data
print('[INFO] Loading final model data...')
df = pd.read_csv(MODEL)

# Plot histograms for volatility columns
for col in ['equity_vol', 'asset_vol']:
    if col in df.columns:
        plt.figure()
        df[col].hist(bins=20)
        plt.title(f'Histogram of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.savefig(f'esg-default-risk-phase1/data/logs/{col}_hist.png')
        plt.close()

# Write summary stats
stats = df[['equity_vol', 'asset_vol']].describe()
stats.to_csv(LOG)
print('[INFO] Volatility QC complete. Stats and histograms saved to data/logs/.') 