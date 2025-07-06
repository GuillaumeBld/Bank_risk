# Data Preparation Scripts

This folder contains scripts for data ingestion, cleaning, and preparation for downstream modeling and analysis.

## Overview
- **Purpose:** Prepare raw data for use in the DD/PD pipeline and other modeling steps.
- **Typical Steps:** Ingest raw files, clean and standardize data, merge panels, and output clean CSVs for modeling.

## Scripts

- `ingest_xxx.py`: Ingests raw data from source xxx and outputs a standardized CSV.
- `clean_xxx.py`: Cleans and standardizes data from source xxx.
- `merge_xxx.py`: Merges multiple cleaned panels into a single modeling-ready file.
- `__init__.py`: Marks the folder as a Python package.

_See individual script docstrings for details on inputs, outputs, and logic._ 