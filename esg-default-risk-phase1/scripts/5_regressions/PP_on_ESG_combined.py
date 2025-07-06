"""
Regression: Probability of Default (PD) on Combined ESG Score
- Dependent: probability_of_default
- Predictor: ESG Combined Score
Data: modeling_data_with_wacc_capm.csv
Output: Regression summary (printed and saved), coefficients table (CSV)
"""

import pandas as pd
import statsmodels.api as sm
from pathlib import Path

infile = Path("esg-default-risk-phase1/data/model/modeling_data_with_wacc_capm.csv")
outfile = Path("esg-default-risk-phase1/scripts/5_regressions/results/PP_on_ESG_combined_results.csv")

# Load data
try:
df = pd.read_csv(infile)
except Exception as e:
    print(f"Error loading input file: {e}")
    exit(1)

# Check for dependent variable
if 'probability_of_default' in df.columns:
    y = df['probability_of_default']
else:
    print("Column 'probability_of_default' not found in input data. Skipping regression.")
    exit(0)

# Predictor
predictor = "esg_combined_score"
if predictor not in df.columns:
    print(f"Missing predictor column: {predictor}. Skipping regression.")
    exit(0)
X = df[[predictor]]

# Run regression
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()

# Save results
results_df = pd.DataFrame({
    'coef': model.params,
    'std_err': model.bse,
    't': model.tvalues,
    'p': model.pvalues
})
results_df.to_csv(outfile)
print(f"Regression results saved to {outfile}")