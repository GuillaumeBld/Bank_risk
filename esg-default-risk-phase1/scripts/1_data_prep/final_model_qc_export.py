"""
This script performs final quality control and exports the analysis-ready modeling dataset.
Inputs: data/model/modeling_data_with_dd_pd.csv
Outputs: data/model/final_model_data.csv
Log: data/logs/final_model_qc_log.txt
"""

import pandas as pd

model = 'esg-default-risk-phase1/data/model/'
logs = 'esg-default-risk-phase1/data/logs/'
df = pd.read_csv(model + 'modeling_data_with_dd_pd.csv')

# Drop any rows with missing or implausible DD/PD (negative DD, PD < 0 or > 1)
df = df[df['distance_to_default'] >= 0]
df = df[(df['probability_of_default'] >= 0) & (df['probability_of_default'] <= 1)]

# Save final file
df.to_csv(model + 'final_model_data.csv', index=False)

# Compute describe and filter out columns with NaN std
desc = df.describe()
if 'std' in desc.index:
    desc = desc.loc[:, ~desc.loc['std'].isna()]

with open(logs + 'final_model_qc_log.txt', 'w') as log:
    log.write('Final model dataset exported after QC.\n')
    log.write(f'Rows: {len(df)}\n')
    log.write('Columns: %s\n' % str(list(df.columns)))
    log.write(str(desc)) 