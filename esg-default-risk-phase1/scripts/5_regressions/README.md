# Regression Analysis Scripts

This folder contains scripts for running regression analyses on DD/PD and related risk metrics.

## Overview
- **Purpose:** Analyze the relationship between DD/PD and explanatory variables using regression models.
- **Typical Steps:** Load modeling data, specify regression models, run regressions, and output results or plots.

## Scripts

- `regressions.py`: Main script for running regression analyses on DD/PD and other risk metrics.
- `robustness.py`: Runs robustness checks and alternative model specifications.
- `__init__.py`: Marks the folder as a Python package.

_See individual script docstrings for details on inputs, outputs, and logic._

# 5_regressions — Regression Analysis Module

This module contains all scripts for estimating the main regression models of the ESG–Bank Risk study. The scripts implement the two-stage least squares (2SLS) and OLS regressions specified in the paper, as discussed with Prof. Abol Jalilvand.

**Key regression types:**
- WACC (CAPM and Fama–French) on ESG and controls
- Distance-to-Default (DD) and Probability of Default (PD) on ESG and controls
- Pillar-level regressions: Environmental, Social, Governance (E, S, G) components

**Script guide:**
- `WACC_FF_on_ESG.py` — Fama–French WACC on ESG (total & combined)
- `WACC_FF_on_ESG_combined.py` — Fama–French WACC on combined ESG
- `DD_on_ESG.py` — Distance-to-default on ESG (total)
- `DD_on_ESG_combined.py` — Distance-to-default on combined ESG
- `PP_on_ESG.py` — Probability of default on ESG (total)
- `PP_on_ESG_combined.py` — Probability of default on combined ESG

**Results and plots** are saved to the `results/` and `plots/` subfolders.

---

## 2. **What are the "controls" for the regressions?**

Based on the instructions and your conversation with Abol Jalilvand, the **control variables** used in all main regressions are:

- **log of total assets** (proxy for bank size)
- **total debt to total assets** (leverage ratio)
- **price to book value per share**
- **capital adequacy ratio**

These appear in the regression equations as controls for both WACC (CAPM and FF) and for risk outcomes (distance-to-default, probability of default).

**In short, your control variables are:**
- `log(Total Assets)`
- `Total Debt / Total Assets` (or `D/TA`)
- `Price to Book Value per Share`
- `Capital Adequacy Ratio`

---

Let me know if you need the README.md for the `/regression` folder rewritten or want a schematic for folder structure!