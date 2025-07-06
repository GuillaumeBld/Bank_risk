"""
run_pipeline.py: Orchestrates the full ESG Default Risk pipeline.

This script runs all major steps in order:
1. Ingest raw data
2. Clean and standardize
3. Filter/model prep
4. Calculate risk metrics (WACC, DD, PD)
5. Quality control/export
6. (Optional) Analysis/diagnostics

See PIPELINE.md for a process map and detailed step descriptions.

Outputs and logs are created in /data/clean/, /data/model/, /data/logs/, and /outputs/.
"""

import subprocess
import sys
import os

STEPS = [
    # (step name, script path)
    ("Ingest annual returns", "scripts/1_data_prep/ingest_annual_returns.py"),
    ("Ingest Fama-French factors", "scripts/1_data_prep/ingest_fama_french_factors.py"),
    ("Clean data", "scripts/1_data_prep/data_cleaning.py"),
    ("Filter/model prep", "scripts/1_data_prep/filter_model_data.py"),
    ("Calculate WACC (CAPM)", "scripts/3_wacc/wacc_capm.py"),
    ("Calculate WACC (Fama-French)", "scripts/3_wacc/wacc_ff.py"),
    ("Calculate Distance to Default", "scripts/2_dd_pd/dd_calc.py"),
    ("Calculate Probability of Default", "scripts/2_dd_pd/pd_calc.py"),
    ("Final QC/export", "scripts/1_data_prep/final_model_qc_export.py"),
    # ("Diagnostics/analysis", "scripts/4_diagnostics/diagnostics.py"),
]


def run_step(name, script):
    print(f"\n=== {name} ===")
    if not os.path.exists(script):
        print(f"[SKIP] Script not found: {script}")
        return False
    try:
        result = subprocess.run([sys.executable, script], check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("[Warning] STDERR:", result.stderr)
        print(f"[OK] {name} completed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {name} failed. See log for details.")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    print("\nESG Default Risk Pipeline Orchestrator\nSee PIPELINE.md for details.\n")
    completed = []
    for name, script in STEPS:
        ok = run_step(name, script)
        completed.append((name, ok))
        if not ok:
            print(f"[STOP] Pipeline halted at step: {name}")
            break
    print("\nPipeline summary:")
    for name, ok in completed:
        print(f" - {name}: {'OK' if ok else 'FAILED'}")
    print("\nAll outputs and logs are in data/ and outputs/. For interpretation/reporting, see PIPELINE.md.")

if __name__ == "__main__":
    main() 