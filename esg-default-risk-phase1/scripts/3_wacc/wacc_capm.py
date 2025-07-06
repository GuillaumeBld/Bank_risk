"""
This script calculates WACC_CAPM for the modeling dataset as weighted_average_cost_of_capital_ divided by 100.
Inputs: data/model/modeling_data_stage1.csv
Outputs: data/model/modeling_data_with_wacc_capm.csv (with new column WACC_CAPM)
Log: data/logs/WACC_CAPM_log.txt
"""

import pandas as pd
import os

INFILE = 'esg-default-risk-phase1/data/model/modeling_data_stage1.csv'
OUTFILE = 'esg-default-risk-phase1/data/model/modeling_data_with_wacc_capm.csv'
LOGFILE = 'esg-default-risk-phase1/data/logs/WACC_CAPM_log.txt'

os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)

try:
    df = pd.read_csv(INFILE)
    if 'weighted_average_cost_of_capital_' not in df.columns:
        raise ValueError("Column 'weighted_average_cost_of_capital_' not found in input data.")
    df['WACC_CAPM'] = df['weighted_average_cost_of_capital_'] / 100
    df.to_csv(OUTFILE, index=False)
    with open(LOGFILE, 'w') as log:
        log.write(f"WACC_CAPM column created as weighted_average_cost_of_capital_ / 100.\n")
        log.write(f"Input: {INFILE}\nOutput: {OUTFILE}\n")
        log.write(f"First 5 rows:\n{df[['instrument','date','weighted_average_cost_of_capital_','WACC_CAPM']].head().to_string(index=False)}\n")
    print("WACC_CAPM column created and saved to output file.")
except Exception as e:
    with open(LOGFILE, 'w') as log:
        log.write(f"Error: {e}\n")
    print(f"Error: {e}") 