"""
Variable Definitions: Builds and documents VAR_DEF_TABLE for the ESG Default Risk Pipeline.

- Loads the final cleaned modeling dataset.
- Maps each variable name to a family, units/scale, and documentation string.
- Saves the output as both CSV and Markdown for transparency and reporting.
"""

import pandas as pd
from pathlib import Path

# --- Paths ---
MODEL_FP = Path('esg-default-risk-phase1/data/model/final_model_data.csv')
OUT_CSV = Path('esg-default-risk-phase1/outputs/tables/VAR_DEF_TABLE.csv')
OUT_MD  = Path('esg-default-risk-phase1/outputs/tables/VAR_DEF_TABLE.md')

# --- Variable Map (EDIT AND EXPAND as needed) ---
VAR_DEF_MAP = {
    'beta_levered':      ("Market risk", "unitless", "Beta with leverage (CAPM)"),
    'beta_unlevered':    ("Market risk", "unitless", "Beta without leverage (asset beta)"),
    'lnTA':              ("Size control", "log USD", "Natural log of total assets"),
    'leverage':          ("Capital structure", "ratio", "Total debt / total assets"),
    'PtoB':              ("Valuation", "ratio", "Price-to-book ratio"),
    'CAR':               ("Capital buffer", "%", "Capital adequacy ratio"),
    'WACC_CAPM':         ("Cost of capital", "%", "Weighted average cost of capital (CAPM)"),
    'WACC_FF':           ("Cost of capital", "%", "WACC (Fama–French 3-factor)"),
    'distance_to_default':("Default risk", "σ-units", "Merton-model distance to default"),
    'probability_of_default':("Default risk", "probability", "Probability of default (Merton model)"),
    'esg_score':         ("ESG", "0–100", "Total ESG Score (Refinitiv/LSEG)"),
    'esg_combined_score':("ESG", "0–100", "Controversy-adjusted ESG Score"),
    'environmental_pillar_score':("ESG pillar", "0–100", "Environmental pillar score"),
    'social_pillar_score':("ESG pillar", "0–100", "Social pillar score"),
    'governance_pillar_score':("ESG pillar", "0–100", "Governance pillar score"),
    'year':              ("Fixed effect", "int", "Calendar year indicator (FE dummy)"),
    # ... add all other variables here ...
}

def build_var_table():
    # 1. Load dataset
    df = pd.read_csv(MODEL_FP)
    var_table = []
    
    # 2. For each column, document or flag as "undocumented"
    for col in df.columns:
        family, scale, doc = VAR_DEF_MAP.get(
            col,
            ("UNASSIGNED", "UNASSIGNED", "Documentation needed")
        )
        var_table.append({
            'Variable': col,
            'Family': family,
            'Units/Scale': scale,
            'Description': doc
        })

    # 3. Output as CSV and Markdown
    pd.DataFrame(var_table).to_csv(OUT_CSV, index=False)
    # Markdown output
    with open(OUT_MD, 'w') as f:
        f.write('| Variable | Family | Units/Scale | Description |\n')
        f.write('|---|---|---|---|\n')
        for row in var_table:
            f.write(f"| {row['Variable']} | {row['Family']} | {row['Units/Scale']} | {row['Description']} |\n")
    print(f"Variable definition table saved to:\n- {OUT_CSV}\n- {OUT_MD}")

def main():
    build_var_table()

if __name__ == "__main__":
    main()