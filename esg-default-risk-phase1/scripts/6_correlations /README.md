# Regression Analysis Module

This folder contains all scripts for the main regression analyses in the ESG–Bank Risk project.  
Each script runs a specific regression or a group of regressions used for results tables and robustness checks in the main paper.

# Correlation Analysis Module

This folder contains scripts and utilities to compute pairwise and matrix correlations for the ESG–bank risk dataset. The goal is to provide all correlation diagnostics required for the paper, including:

- Pairwise and heatmap correlations between risk metrics (distance-to-default, probability of default), WACC measures (CAPM, Fama–French), and all ESG variables
- Separate results for total ESG and combined ESG
- Correlations with key bank characteristics (size, leverage, price-to-book, capital adequacy)
- Output in publication-ready tables and figures

## Folder Structure

- `plots/` — Output plots for main and robustness regressions
- `results/` — Regression result tables and pickled model objects
- `WACC_FF_and_ESG.py` — Correlation analysis between Fama–French WACC and ESG scores
- `WACC_FF_and_ESG_combined.py` — Correlation analysis between Fama–French WACC and combined ESG score
- `DD_and_other.py` — Correlation analysis between distance to default and other variables
- `PD_and_other.py` — Correlation analysis between probability of default and other variables
- `DD&PD_and_ESG.py` — Correlation analysis between distance/probability of default and ESG scores
- `DD&PD_and_ESG_combined.py` — Correlation analysis between distance/probability of default and combined ESG score
- `DD&PD_and_other.py` — Correlation analysis between distance/probability of default and other variables
- `README.md` — This file
