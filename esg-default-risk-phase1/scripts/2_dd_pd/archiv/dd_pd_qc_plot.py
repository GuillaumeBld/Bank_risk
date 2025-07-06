"""
QC Plot: DD vs. PD

Inputs:
- /data/model/modeling_data_with_dd_pd.csv

Outputs:
- /outputs/figures/dd_vs_pd_scatter.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

model_fp = Path('esg-default-risk-phase1/data/model/modeling_data_with_dd_pd.csv')
out_dir = Path('esg-default-risk-phase1/outputs/figures/')
out_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(model_fp)

plt.figure(figsize=(6, 5))
plt.scatter(df['distance_to_default'], df['probability_of_default'], alpha=0.6)
plt.xlabel('Distance to Default')
plt.ylabel('Probability of Default')
plt.title('QC: DD vs. PD')
plt.tight_layout()
plt.savefig(out_dir / 'dd_vs_pd_scatter.png')
plt.close()

print("[INFO] DD vs PD plot saved.")