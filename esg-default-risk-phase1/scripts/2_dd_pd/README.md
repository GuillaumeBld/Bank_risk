# Distance to Default & Probability of Default (DD/PD) Scripts

This folder contains scripts for calculating Distance to Default (DD) and Probability of Default (PD) for banks using the Merton model, as well as supporting data preparation and quality control routines.

## Overview
- **Main Goal:** Compute robust, monthly DD and PD estimates for each bank using market and balance sheet data.
- **Approach:** Uses the Merton model, iterative asset value/volatility estimation, and monthly market cap with close prices.
- **Inputs:** Cleaned modeling data, monthly returns, monthly market cap, and close prices.
- **Outputs:** Monthly DD/PD panel, diagnostics, and QC plots.

## Scripts

| Script                          | Main Functionality                                 |
|----------------------------------|----------------------------------------------------|
| `dd_pd_calc.py`                  | Full pipeline: DD & PD (Merton, monthly, robust)   |
| `dd_calc.py`                     | Simple DD calculation (annual, book values)        |
| `pd_calc.py`                     | Standalone PD calculation from DD                  |
| `dd_pd_qc_plot.py`               | QC plot: DD vs. PD scatter                        |
| `update_marketcap_to_monthly.py` | Expand/merge market cap to monthly with prices     |
| `__init__.py`                    | Marks folder as a Python package                   |

---

### `dd_pd_calc.py`
**Main script for robust, monthly DD/PD calculation using the Merton model.**
- Loads modeling data, monthly returns, and monthly market cap (with close prices).
- Merges all data to monthly frequency, aligns dates, and computes market cap.
- Calculates annualized equity volatility for each bank-year.
- Runs an iterative Merton solver to estimate asset value and asset volatility.
- Computes DD and PD for each row.
- Outputs a detailed CSV and a log with diagnostics and missing data info.

### `dd_calc.py`
**Simpler/older script for annual DD calculation.**
- Uses a fixed volatility and book values.
- Outputs a CSV with DD and a log file.

### `pd_calc.py`
**Standalone script for calculating PD from a precomputed DD column.**
- Loads a CSV with DD values.
- Computes PD as the cumulative normal of -DD.
- Outputs a CSV with PD and a log file.

### `dd_pd_qc_plot.py`
**Quality control plotting script.**
- Loads the main DD/PD output file.
- Plots a scatterplot of DD vs. PD for diagnostics.

### `update_marketcap_to_monthly.py`
**Data preparation script to expand annual market cap to monthly and merge in close prices.**
- Loads annual market cap and monthly returns data.
- Expands market cap to monthly rows for each bank-year.
- Merges in monthly close prices from a wide-format file.
- Outputs a new monthly market cap file for use in DD/PD calculations.

### `__init__.py`
Marks the folder as a Python package (for imports).

---

For more details on the workflow or how to run each script, see the docstrings in each file or ask for help! 