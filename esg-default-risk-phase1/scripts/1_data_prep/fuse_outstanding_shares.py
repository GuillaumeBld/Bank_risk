"""
This script finalizes the outstanding shares data by moving the full panel file to outstanding_shares.csv and deleting all intermediate files used in the process.

Inputs:
  - data/clean/bank_outstanding_shares_full_panel_2016_2023.csv
  - data/clean/merged_outstanding_shares_2016_2020.csv
  - data/clean/corrected_bank_outstanding_shares_2016_2020.csv
  - data/clean/bank_outstanding_shares_2016_2023.csv
  - data/clean/outstanding_shares.csv (to be replaced)
Outputs:
  - data/clean/outstanding_shares.csv (final, fused file)
Log:
  - data/logs/fuse_outstanding_shares_log.txt
"""
import os
import shutil

BASE = os.path.join(os.path.dirname(__file__), '../../data/clean')
LOGFILE = os.path.join(BASE, '../logs/fuse_outstanding_shares_log.txt')

final_file = os.path.join(BASE, 'bank_outstanding_shares_full_panel_2016_2023.csv')
fused_file = os.path.join(BASE, 'outstanding_shares.csv')

# List of files to delete (except the final fused file)
files_to_delete = [
    os.path.join(BASE, 'merged_outstanding_shares_2016_2020.csv'),
    os.path.join(BASE, 'corrected_bank_outstanding_shares_2016_2020.csv'),
    os.path.join(BASE, 'bank_outstanding_shares_2016_2023.csv'),
]
# If an old outstanding_shares.csv exists, delete it
if os.path.exists(fused_file):
    files_to_delete.append(fused_file)

# Move the final file to outstanding_shares.csv
shutil.copyfile(final_file, fused_file)

# Delete intermediate files
deleted = []
for f in files_to_delete:
    if os.path.exists(f):
        os.remove(f)
        deleted.append(f)

# Log
with open(LOGFILE, 'w') as f:
    f.write(f"Fused file created: {fused_file}\n")
    f.write(f"Deleted files:\n")
    for d in deleted:
        f.write(f"  {d}\n")

print(f"Fused file created: {fused_file}")
print(f"Deleted files: {deleted}") 