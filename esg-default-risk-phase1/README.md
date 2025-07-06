# ESG Default‐Risk Analysis Pipeline

**Decomposing ESG: Environmental, Social, and Governance Effects on Bank Risk**  
This repository implements a complete, end-to-end pipeline for calculating and analyzing U.S. bank default‐risk measures (Distance‐to‐Default & Probability‐of‐Default), cost-of-capital (CAPM & Fama–French WACC), and their relationships with ESG scores. The final outputs feed directly into the accompanying report and presentation.

---

## 📁 Repository Structure

esg-default-risk-phase1/
├── data/
│   ├── raw/                # Untouched source files
│   ├── interim/            # Cleaned & merged panel
│   └── processed/          # Final modelling dataset CSV
├── scripts/
│   ├── run_pipeline.py     # Orchestrates all stages
│   ├── 1_data_prep/        # ETL & variable-definition
│   ├── 2_dd_pd/            # Distance‐to‐Default & PD routines
│   ├── 3_wacc/             # CAPM & Fama-French WACC
│   ├── 4_diagnostics/      # Collinearity & rank checks
│   └── 5_regressions/      # 2SLS & robustness tests
├── outputs/
│   ├── csv/                # Final .csv tables for report
│   ├── figures/            # QC & diagnostic plots
│   └── tables/             # Regression & summary tables
├── notebooks/              # Exploratory & diagnostic Jupyter notebooks
├── tests/                  # Unit tests for each module
├── docs/                   # Report, slides, exported artifacts
├── config/                 # Global thresholds & file-paths
├── requirements.txt        # Python dependencies
├── environment.yml         # (Optional) conda env spec
└── README.md               # ← You are here

---

## 🚀 Quickstart

1. **Clone & install**  
   ```bash
   git clone https://github.com/your-org/esg-default-risk-phase1.git
   cd esg-default-risk-phase1
   pip install -r requirements.txt
   # or, for conda users:
   # conda env create -f environment.yml
   # conda activate esg-risk

	2.	Place your raw data
	•	data/raw/annual_returns-5-20-2025.csv
	•	data/raw/F-F_Research_Data_Factors.csv
	3.	Run the full pipeline

python scripts/run_pipeline.py

This will:
	•	Clean & merge data → data/interim/panel_cleaned.csv
	•	Compute DD & PD with QC plots → outputs/figures/dd_pd_qc_plot.png
	•	Recalculate WACC_FF & winsorise → outputs/figures/wacc_ff_hist_*.png
	•	Run collinearity diagnostics → outputs/tables/vif_summary.csv
	•	Execute all 2SLS regressions & robustness checks → outputs/csv/*.csv
	•	Write final modelling dataset → data/processed/modelling_dataset.csv

	4.	Inspect results
	•	Final tables live in outputs/csv/.
	•	Plots and diagnostic figures in outputs/figures/.
	•	Use notebooks/ for interactive exploration.

⸻

🔧 Pipeline Details

1. Data Preparation (scripts/1_data_prep)
	•	etl.py: loads raw CSVs, merges, cleans missing values, drops negative-beta bank-years.
	•	var_defs.py: documents & enforces variable definitions (0-100 scaling, log‐assets, controls, etc.).

2. Default-Risk (scripts/2_dd_pd)
	•	dd_calc.py: solves Merton’s structural model for Distance-to-Default.
	•	pd_calc.py: maps DD → PD via the Normal CDF.
	•	dd_pd_qc_plot.py: produces QC scatter & summary stats.

3. Cost-of-Capital (scripts/3_wacc)
	•	wacc_capm.py: reads pre-computed CAPM WACC from spreadsheet.
	•	wacc_ff.py: constructs multi-factor WACC, applies caps/floors to curb outliers.

4. Diagnostics (scripts/4_diagnostics/diagnostics.py)
	•	Computes VIF, matrix rank, condition numbers to detect collinearity & identification issues.

5. Regressions (scripts/5_regressions)
	•	regressions.py: runs 2SLS tests for WACC & default-risk hypotheses H1–H6.
	•	robustness.py: size splits, alternative winsorisation, crisis‐year interactions.

⸻

🛠 Configuration

All thresholds and file-paths live in config/config.yaml. You can override:
	•	Winsorisation percentiles (default: 5th/95th)
	•	Beta cut-offs for exclusion
	•	Data directories
	•	Regression specs (controls, FE)

⸻

✅ Testing

Run the unit‐test suite to ensure each module behaves as expected:

pytest tests/


⸻

📖 Documentation & Report
	•	Report draft: docs/Report.docx (live)
	•	Final PDF: docs/Report.pdf
	•	Presentation slides: docs/presentation.pptx

Placeholders like <<<PLACEHOLDER: DD_PD_QC_PLOT>>> in the Word doc are auto-filled by the pipeline’s final CSVs/plots.

⸻

📬 Contributing
	1.	Fork & clone the repo.
	2.	Create a feature branch: git checkout -b feature/my-improvement.
	3.	Add code or update docs; add tests under tests/.
	4.	Run pytest & confirm all tests pass.
	5.	Submit a Pull Request; reference related report sections or issue numbers.

⸻

🙏 Acknowledgments

This workflow was designed for Professor Abol Jalilvand’s bank‐risk research.
created and maintained by the Guillaume Bolivard.

⸻

📜 License

MIT License

