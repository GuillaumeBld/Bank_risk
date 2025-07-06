"""
This script compares the 'new wacc' and 'Weighted Average Cost of Capital, (%)' columns in the raw data.
Inputs: data/raw/annual_returns-5-20-2025.csv
Outputs: None (prints results to stdout)
Log: data/logs/compare_wacc_columns_log.txt
"""

import pandas as pd
import os

RAW_CSV = 'esg-default-risk-phase1/data/raw/annual_returns-5-20-2025.csv'
LOG_FILE = 'esg-default-risk-phase1/data/logs/compare_wacc_columns_log.txt'

# Additional audit: check mapping in modeling_data_with_wacc.csv
model_fp = 'esg-default-risk-phase1/data/model/modeling_data_with_wacc.csv'
trace_log = 'esg-default-risk-phase1/data/logs/compare_wacc_columns_trace.txt'

col1 = 'new wacc'
col2 = 'Weighted Average Cost of Capital, (%)'

def main():
    # Ensure log directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'w') as log:
        try:
            df = pd.read_csv(RAW_CSV)
            if col1 not in df.columns or col2 not in df.columns:
                msg = f"One or both columns not found in CSV: {col1}, {col2}\nColumns present: {list(df.columns)}"
                print(msg)
                log.write(msg + '\n')
                return
            identical = (df[col1] == df[col2]).all()
            if identical:
                msg = f"Columns '{col1}' and '{col2}' are identical."
                print(msg)
                log.write(msg + '\n')
            else:
                diff = df[df[col1] != df[col2]][[col1, col2]]
                msg = f"Columns differ in {len(diff)} rows. Showing first 10 differences:\n{diff.head(10)}"
                print(msg)
                log.write(msg + '\n')

            # Additional audit: check mapping in modeling_data_with_wacc.csv
            try:
                df_model = pd.read_csv(model_fp)
                # Sample 10 rows for audit
                sample = df_model[['instrument','date','new_wacc','weighted_average_cost_of_capital_','WACC_CAPM']].head(10)
                # Check if WACC_CAPM matches new_wacc
                all_match = (df_model['WACC_CAPM'] == df_model['new_wacc']).all()
                mismatch_count = (df_model['WACC_CAPM'] != df_model['new_wacc']).sum()
                audit_msg = f"WACC_CAPM matches new_wacc in all rows: {all_match}\nMismatches: {mismatch_count}\n\nSample rows:\n{sample.to_string(index=False)}\n"
                print(audit_msg)
                with open(trace_log, 'w') as tlog:
                    tlog.write(audit_msg)

                # Additional audit: check if WACC_CAPM == weighted_average_cost_of_capital_ / 100
                # Check equivalence
                wacc_capm = df_model['WACC_CAPM']
                wacc_percent = df_model['weighted_average_cost_of_capital_']
                is_equiv = (wacc_capm.round(6) == (wacc_percent / 100).round(6))
                mismatch_count = (~is_equiv).sum()
                sample_mismatch = df_model.loc[~is_equiv, ['instrument','date','WACC_CAPM','weighted_average_cost_of_capital_']].head(10)
                eq_msg = f"WACC_CAPM == weighted_average_cost_of_capital_ / 100 in all rows: {mismatch_count == 0}\nMismatches: {mismatch_count}\n\nSample mismatches:\n{sample_mismatch.to_string(index=False)}\n"
                print(eq_msg)
                with open(trace_log, 'a') as tlog:
                    tlog.write(eq_msg)
            except Exception as e:
                print(f"Error in WACC_CAPM equivalence check: {e}")
                with open(trace_log, 'a') as tlog:
                    tlog.write(f"Error in WACC_CAPM equivalence check: {e}\n")
        except Exception as e:
            msg = f"Error during comparison: {e}"
            print(msg)
            log.write(msg + '\n')

if __name__ == '__main__':
    main() 