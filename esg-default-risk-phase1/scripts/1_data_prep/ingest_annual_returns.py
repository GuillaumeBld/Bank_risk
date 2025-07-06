import os
import pandas as pd

raw_dir = 'data/raw'
log_dir = 'data/logs'
os.makedirs(log_dir, exist_ok=True)

file_path = os.path.join(raw_dir, 'annual_returns-5-20-2025.csv')
df = pd.read_csv(file_path)

log_file = os.path.join(log_dir, 'annual_returns_ingest_log.txt')
with open(log_file, 'w') as f:
    f.write(f"File: {file_path}\n")
    f.write(f"Shape: {df.shape}\n")
    f.write("Columns:\n")
    for col in df.columns:
        f.write(f"  - {col}\n")
    f.write("\nFirst 3 rows:\n")
    f.write(df.head(3).to_string())
print(f"[INFO] Ingestion log written to {log_file}")