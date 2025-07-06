import os
import pandas as pd

raw_dir = 'data/raw'
log_dir = 'data/logs'
os.makedirs(log_dir, exist_ok=True)

file_path = os.path.join(raw_dir, 'F-F_Research_Data_Factors.csv')
# Skip metadata/header lines and read from the first data row
df = pd.read_csv(file_path, skiprows=5)

log_file = os.path.join(log_dir, 'fama_french_ingest_log.txt')
with open(log_file, 'w') as f:
    f.write(f"File: {file_path}\n")
    f.write(f"Shape: {df.shape}\n")
    f.write("Columns:\n")
    for col in df.columns:
        f.write(f"  - {col}\n")
    f.write("\nFirst 3 rows:\n")
    f.write(df.head(3).to_string())
print(f"[INFO] Ingestion log written to {log_file}")