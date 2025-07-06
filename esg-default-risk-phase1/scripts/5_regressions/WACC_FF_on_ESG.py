"""
Regression: WACC_FF on ESG Pillar Scores
- Dependent: WACC_FF
- Predictors: Environmental, Social, Governance Pillar Scores (+controls optional)
Data: modeling_data_with_wacc_ff.csv
Output: Regression summary (printed and saved), coefficients table (CSV)
"""

import pandas as pd
import statsmodels.api as sm
from pathlib import Path

infile = Path("esg-default-risk-phase1/data/model/modeling_data_with_wacc_ff.csv")
outfile = Path("esg-default-risk-phase1/outputs/WACC_FF_on_ESG_results.csv")

df = pd.read_csv(infile)
X = df[["environmental_pillar_score", "social_pillar_score", "governance_pillar_score"]]
y = df["WACC_FF"]
mask = X.notna().all(axis=1) & y.notna()
X = X[mask]
y = y[mask]
X = sm.add_constant(X)
model = sm.OLS(y, X).fit(cov_type="HC3")
print(model.summary())
results_df = pd.DataFrame({
    "coef": model.params,
    "std_err": model.bse,
    "p_value": model.pvalues
})
results_df.to_csv(outfile)