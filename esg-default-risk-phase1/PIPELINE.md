# ESG Default Risk Pipeline – Process Map

Welcome! This document is your step-by-step guide to the entire project pipeline—from raw data to final results. It's written for everyone: whether you code or not.

- **New user?** See the Quickstart below.
- **Researcher or collaborator?** Check the Output Table to connect files with report sections.
- **Running the whole pipeline?** Use `python utils/run_pipeline.py` for a one-command solution.

If you hit a snag, see Troubleshooting below or check the `/data/logs/` folder for detailed logs.

---

## Quickstart
- **New?** Start here for a guided tour of the workflow.
- **To run the full pipeline:**
  1. Install dependencies (see README.md)
  2. Run `python utils/run_pipeline.py`
  3. All outputs and logs will be created in the appropriate folders.

---

## Pipeline Overview Diagram

```
Raw Data (data/raw/)
  │
  └──▶ Ingestion (scripts/1_data_prep/ingest_annual_returns.py, ingest_fama_french_factors.py)
            │
            └──▶ Cleaning (scripts/1_data_prep/data_cleaning.py)
                      │
                      └──▶ Filtering (scripts/1_data_prep/filter_model_data.py)
                                │
                                └──▶ Calculations (scripts/3_wacc/wacc_capm.py, scripts/3_wacc/wacc_ff.py, scripts/2_dd_pd/dd_calc.py, scripts/2_dd_pd/pd_calc.py)
                                          │
                                          └──▶ QC/Export (scripts/1_data_prep/final_model_qc_export.py)
                                                    │
                                                    └──▶ Analysis/Reporting (notebooks/, scripts/4_diagnostics/, scripts/5_regressions/)
```

---

## Step-by-Step Pipeline

### 1. Ingest Raw Data
- **Scripts:** `ingest_annual_returns.py`, `ingest_fama_french_factors.py`
- **Purpose:** Loads raw CSVs and logs their structure for traceability.
- **Input:** `/data/raw/`
- **Output:** `/data/logs/ingest_*.txt`
- **What to expect:** Log files confirming data loaded, shapes, and columns.

### 2. Clean and Standardize
- **Script:** `data_cleaning.py`
- **Purpose:** Cleans and standardizes raw data, fixes column names, parses dates, and saves clean CSVs.
- **Input:** `/data/raw/`
- **Output:** `/data/clean/annual_returns_clean.csv`, `/data/clean/fama_french_factors_clean.csv`
- **What to expect:** Cleaned CSVs with standardized columns, logs of cleaning steps.

### 3. Filter and Model Prep
- **Script:** `filter_model_data.py`
- **Purpose:** Filters out rows with missing or implausible values, prepares data for modeling.
- **Input:** `/data/clean/`
- **Output:** `/data/model/modeling_data_stage1.csv`
- **What to expect:** Filtered dataset, log of exclusions and columns.

### 4. Calculate Risk Metrics
- **Scripts:** `wacc_capm.py`, `wacc_ff.py`, `dd_calc.py`, `pd_calc.py`
- **Purpose:** Adds WACC (cost of capital), Distance to Default (DD), and Probability of Default (PD) columns to the modeling dataset.
- **Input:** `/data/model/modeling_data_stage1.csv`
- **Output:** `/data/model/modeling_data_with_wacc.csv`, `/data/model/modeling_data_with_dd_pd.csv`
- **What to expect:** New columns for WACC, DD, PD; logs of calculations and stats.

### 5. Quality Control and Export
- **Script:** `final_model_qc_export.py`
- **Purpose:** Final quality check, removes any remaining implausible values, and exports the analysis-ready dataset.
- **Input:** `/data/model/modeling_data_with_dd_pd.csv`
- **Output:** `/data/model/final_model_data.csv`
- **What to expect:** Final, analysis-ready dataset; log of QC and summary stats.

### 6. Analysis and Diagnostics
- **Scripts:** Notebooks, `4_diagnostics/`, `5_regressions/`
- **Purpose:** Runs regressions, diagnostics, and generates figures/tables for reporting.
- **Input:** `/data/model/final_model_data.csv`
- **Output:** `/outputs/figures/`, `/outputs/tables/`
- **What to expect:** Figures, tables, regression outputs for reporting.

---

## Output Table: Where Used in Report
| Output File                              | Where Used in Report         | Purpose/Notes                        |
|------------------------------------------|------------------------------|--------------------------------------|
| data/clean/annual_returns_clean.csv      | Data section, Appendix       | Cleaned annual returns data          |
| data/clean/fama_french_factors_clean.csv | Data section, Appendix       | Cleaned Fama-French factors          |
| data/model/modeling_data_stage1.csv      | Methods, Data Filtering      | Filtered, pre-modeling dataset       |
| data/model/modeling_data_with_wacc.csv   | Methods, WACC Calculation    | Dataset with WACC columns            |
| data/model/modeling_data_with_dd_pd.csv  | Methods, DD/PD Calculation   | Dataset with DD/PD columns           |
| data/model/final_model_data.csv          | Results, Regression, Tables  | Final analysis-ready dataset         |
| outputs/figures/*                        | Results, Figures             | Plots for QC, diagnostics, reporting |
| outputs/tables/*                         | Results, Tables              | Summary/regression tables            |

**Reproducibility tip:**
If you change input data or want to rerun the analysis, delete/replace only the necessary downstream files and rerun from that step forward.

---

## Typical Failure Modes & Troubleshooting
- **FileNotFoundError:** Check that all input files are in the correct `/data/raw/` or `/data/clean/` folders.
- **PermissionError:** Ensure you have write access to the data/output folders.
- **Missing Columns:** If a script fails due to missing columns, check that all previous steps completed successfully and outputs are present.
- **Path Issues:** Always run scripts from the project root unless otherwise specified.
- **Log Files:** Check `/data/logs/` for detailed error and progress logs after each step.
- **If in doubt:** Run `utils/run_pipeline.py` and check the console for error guidance.

---

## For Researchers/Collaborators
- See the top of `README.md` for a link to this file.
- Each script and output is documented here for transparency and reproducibility.
- For questions or contributions, see `CONTRIBUTING.md` (if present) or contact the project lead.
- For bug reports or enhancement requests, open an Issue in GitHub (if repo is public), or email the project lead.

---

## Next Steps
- To run the full pipeline, see `utils/run_pipeline.py` (or follow the stepwise instructions above).
- For interpretation/reporting, see the Output Table above and the logs in `/data/logs/`. 