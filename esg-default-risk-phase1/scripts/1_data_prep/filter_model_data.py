"""
This script filters the cleaned data for modeling, removing implausible or missing values.
Inputs: data/clean/annual_returns_clean.csv
Outputs: data/model/modeling_data_stage1.csv
Log: data/logs/modeling_data_filter_log.txt
"""

import pandas as pd
from pathlib import Path

clean = Path('esg-default-risk-phase1/data/clean/')
model = Path('esg-default-risk-phase1/data/model/')
logs = Path('esg-default-risk-phase1/data/logs/')
model.mkdir(exist_ok=True)

# Load cleaned data
annual = pd.read_csv(clean/'annual_returns_clean.csv')

# Relaxed filter: allow beta_levered >= 0 and up to one missing ESG pillar/ESG field
filtered = annual[annual['beta_levered'] >= 0].copy()
key_vars = ['esg_score', 'environmental_pillar_score', 'social_pillar_score', 'governance_pillar_score']
filtered['n_missing'] = filtered[key_vars].isna().sum(axis=1)
filtered = filtered[filtered['n_missing'] <= 1].drop(columns=['n_missing'])

# Save output
filtered.to_csv(model/'modeling_data_stage1.csv', index=False)

# Log
with open(logs/'modeling_data_filter_log.txt', 'w') as log:
    log.write(f'Initial rows: {len(annual)}\n')
    log.write(f'Filtered (beta_levered >= 0, <=1 NA in pillars/ESG): {len(filtered)}\n')
    log.write('Columns: %s\n' % str(list(filtered.columns))) 