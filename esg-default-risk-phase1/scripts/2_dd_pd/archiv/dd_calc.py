"""
Distance to Default Calculation Script

Inputs: 
- /data/model/modeling_data_with_wacc.csv (must have total assets, debt, equity, volatility, etc.)

Outputs: 
- Adds 'distance_to_default' column to dataset.
- Log: /data/logs/dd_calc_log.txt
"""

import pandas as pd
from pathlib import Path
from scipy.stats import norm

# File paths
model_fp = Path('esg-default-risk-phase1/data/model/modeling_data_with_wacc.csv')
log_fp = Path('esg-default-risk-phase1/data/logs/dd_calc_log.txt')

df = pd.read_csv(model_fp)

# --- Distance to Default calculation
# Example formula: DD = (ln(VA/DF) + (mu - 0.5*sigma^2)*T) / (sigma*sqrt(T))
# Here VA = total assets, DF = total debt (or other measure), sigma = volatility
# mu can be set to 0, T = 1

import numpy as np

VA = df['total_assets']
DF = df['debt__total']
sigma = 0.25  # Use historical or proxy, update as needed
mu = 0.0
T = 1.0

df['distance_to_default'] = (np.log(VA / DF) + (mu - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

# QC: Cap negative/implausible DDs if needed

df.to_csv(model_fp.with_name('modeling_data_with_dd.csv'), index=False)

with open(log_fp, 'w') as log:
    log.write(f"Distance to Default calculated for {len(df)} rows\n")
    log.write(str(df['distance_to_default'].describe()))

print("[INFO] Distance to Default calculated and saved.")