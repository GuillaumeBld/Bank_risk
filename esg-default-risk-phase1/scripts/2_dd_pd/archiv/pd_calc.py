"""
Probability of Default Calculation Script

Inputs:
- /data/model/modeling_data_with_dd.csv

Outputs:
- Adds 'probability_of_default' column
- Log: /data/logs/pd_calc_log.txt
"""

import pandas as pd
from pathlib import Path
from scipy.stats import norm

fp = Path('esg-default-risk-phase1/data/model/modeling_data_with_dd_pd.csv')
log_fp = Path('esg-default-risk-phase1/data/logs/pd_calc_log.txt')

df = pd.read_csv(fp)

# PD = N(-DD)
df['probability_of_default'] = norm.cdf(-df['distance_to_default'])

df.to_csv(fp.with_name('modeling_data_with_dd_pd.csv'), index=False)

with open(log_fp, 'w') as log:
    log.write(f"PD calculated for {len(df)} rows\n")
    log.write(str(df['probability_of_default'].describe()))

print("[INFO] Probability of Default calculated and saved.")