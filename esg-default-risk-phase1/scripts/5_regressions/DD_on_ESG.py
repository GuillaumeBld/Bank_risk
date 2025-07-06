"""
Regression: Distance to Default (DD) on ESG Pillar Scores
- Dependent: distance_to_default
- Predictors: Environmental, Social, Governance Pillar Scores (+controls optional)
Data: modeling_data_with_wacc_capm.csv
Output: Regression summary (printed and saved), coefficients table (CSV)
"""

import pandas as pd
import statsmodels.api as sm
from pathlib import Path

# Paths
infile = Path("esg-default-risk-phase1/data/model/modeling_data_with_wacc_capm.csv")
outfile = Path("esg-default-risk-phase1/scripts/5_regressions/results/DD_on_ESG_results.csv")

# Load data
try:
df = pd.read_csv(infile)
except Exception as e:
    print(f"Error loading input file: {e}")
    exit(1)

# Check for dependent variable
if 'distance_to_default' in df.columns:
    y = df['distance_to_default']
else:
    print("Column 'distance_to_default' not found in input data. Skipping regression.")
    exit(0)

# Predictors
predictors = ["environmental_pillar_score", "social_pillar_score", "governance_pillar_score"]
missing = [col for col in predictors if col not in df.columns]
if missing:
    print(f"Missing predictor columns: {missing}. Skipping regression.")
    exit(0)
X = df[predictors]

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