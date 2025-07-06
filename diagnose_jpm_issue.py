"""
Diagnostic Script for JPM Missing Data Issue
This script helps identify why JPM bank produces missing data in dd_pd_market.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

def diagnose_jpm_issue():
    """
    Diagnose why JPM produces missing data in the Merton model calculation
    """
    print("=== JPM Missing Data Diagnostic ===\n")
    
    # File paths (same as in original script)
    model_fp = Path('esg-default-risk-phase1/data/clean/annual_returns_clean.csv')
    marketcap_fp = Path('esg-default-risk-phase1/data/clean/all_banks_marketcap_2016_2023.csv')
    vol_fp = Path('esg-default-risk-phase1/data/clean/bank_annual_equity_vol.csv')
    
    try:
        # Load datasets
        print("1. Loading datasets...")
        df = pd.read_csv(model_fp)
        marketcap = pd.read_csv(marketcap_fp)
        equity_vol = pd.read_csv(vol_fp)
        print(f"   - Main dataset: {len(df)} rows")
        print(f"   - Market cap dataset: {len(marketcap)} rows")
        print(f"   - Equity vol dataset: {len(equity_vol)} rows\n")
        
    except FileNotFoundError as e:
        print(f"ERROR: Could not find file {e.filename}")
        return
    
    # Helper function (same as original)
    def get_prefix(ticker):
        if pd.isna(ticker):
            return None
        return str(ticker).split('.')[0]
    
    # Prepare data (similar to original script)
    df['symbol'] = df['instrument'].apply(lambda x: str(x).split('.')[0])
    marketcap['symbol'] = marketcap['symbol'].apply(get_prefix) if 'symbol' in marketcap.columns else None
    
    # Check for JPM in each dataset
    print("2. Checking JPM presence in each dataset...")
    
    # Main dataset
    jpm_main = df[df['symbol'].str.contains('JPM', na=False, case=False)]
    print(f"   - JPM in main dataset: {len(jpm_main)} rows")
    if len(jpm_main) > 0:
        print(f"     Symbols found: {jpm_main['symbol'].unique()}")
        print(f"     Years: {sorted(jpm_main['date'].apply(lambda x: pd.to_datetime(x).year).unique())}")
    
    # Market cap dataset
    if 'symbol' in marketcap.columns:
        jpm_marketcap = marketcap[marketcap['symbol'].str.contains('JPM', na=False, case=False)]
        print(f"   - JPM in market cap dataset: {len(jpm_marketcap)} rows")
        if len(jpm_marketcap) > 0:
            print(f"     Symbols found: {jpm_marketcap['symbol'].unique()}")
            marketcap['fiscal_date'] = pd.to_datetime(marketcap['fiscal_date'])
            print(f"     Years: {sorted(jpm_marketcap['fiscal_date'].dt.year.unique())}")
    else:
        print("   - No 'symbol' column in market cap dataset")
        print(f"     Available columns: {marketcap.columns.tolist()}")
    
    # Equity vol dataset
    if 'symbol' in equity_vol.columns:
        jpm_vol = equity_vol[equity_vol['symbol'].str.contains('JPM', na=False, case=False)]
        print(f"   - JPM in equity vol dataset: {len(jpm_vol)} rows")
        if len(jpm_vol) > 0:
            print(f"     Symbols found: {jpm_vol['symbol'].unique()}")
            print(f"     Years: {sorted(jpm_vol['Year'].unique())}")
    elif 'Bank' in equity_vol.columns:
        equity_vol['symbol'] = equity_vol['Bank'].apply(lambda x: str(x).split('.')[0])
        jpm_vol = equity_vol[equity_vol['symbol'].str.contains('JPM', na=False, case=False)]
        print(f"   - JPM in equity vol dataset (using Bank column): {len(jpm_vol)} rows")
        if len(jpm_vol) > 0:
            print(f"     Symbols found: {jpm_vol['symbol'].unique()}")
            print(f"     Years: {sorted(jpm_vol['Year'].unique())}")
    else:
        print("   - No 'symbol' or 'Bank' column in equity vol dataset")
        print(f"     Available columns: {equity_vol.columns.tolist()}")
    
    print()
    
    # Check for common JPM variations
    print("3. Checking for JPM variations...")
    jpm_patterns = ['JPM', 'JPMORGAN', 'JP MORGAN', 'CHASE', 'JPMC']
    
    for pattern in jpm_patterns:
        print(f"   Pattern: '{pattern}'")
        
        # Main dataset
        main_matches = df[df['symbol'].str.contains(pattern, na=False, case=False)]
        if len(main_matches) > 0:
            print(f"     Main dataset: {main_matches['symbol'].unique()}")
        
        # Market cap dataset
        if 'symbol' in marketcap.columns:
            mcap_matches = marketcap[marketcap['symbol'].str.contains(pattern, na=False, case=False)]
            if len(mcap_matches) > 0:
                print(f"     Market cap dataset: {mcap_matches['symbol'].unique()}")
        
        # Equity vol dataset
        if 'symbol' in equity_vol.columns:
            vol_matches = equity_vol[equity_vol['symbol'].str.contains(pattern, na=False, case=False)]
            if len(vol_matches) > 0:
                print(f"     Equity vol dataset: {vol_matches['symbol'].unique()}")
    
    print()
    
    # If JPM found, check data quality
    if len(jpm_main) > 0:
        print("4. Checking JPM data quality in main dataset...")
        
        # Check required columns
        required_cols = ['debt__total', 'rit', 'ritrf']
        for col in required_cols:
            if col in df.columns:
                missing_count = jpm_main[col].isna().sum()
                zero_count = (jpm_main[col] == 0).sum()
                negative_count = (jpm_main[col] < 0).sum()
                print(f"   - {col}: {missing_count} missing, {zero_count} zeros, {negative_count} negative")
            else:
                print(f"   - {col}: COLUMN MISSING")
        
        # Check merge potential
        print("\n5. Checking merge compatibility...")
        
        df['Year'] = pd.to_datetime(df['date']).dt.year
        df['Month'] = pd.to_datetime(df['date']).dt.month
        
        if 'symbol' in marketcap.columns and len(jpm_marketcap) > 0:
            marketcap['Year'] = pd.to_datetime(marketcap['fiscal_date']).dt.year
            marketcap['Month'] = pd.to_datetime(marketcap['fiscal_date']).dt.month
            
            # Check if JPM data can be merged
            jpm_main_merge_keys = set(zip(jpm_main['symbol'], jpm_main['Year'], jpm_main['Month']))
            jpm_mcap_merge_keys = set(zip(jpm_marketcap['symbol'], jpm_marketcap['Year'], jpm_marketcap['Month']))
            
            overlapping_keys = jpm_main_merge_keys.intersection(jpm_mcap_merge_keys)
            print(f"   - JPM merge keys in main: {len(jpm_main_merge_keys)}")
            print(f"   - JPM merge keys in market cap: {len(jpm_mcap_merge_keys)}")
            print(f"   - Overlapping merge keys: {len(overlapping_keys)}")
            
            if len(overlapping_keys) == 0:
                print("   - NO OVERLAPPING MERGE KEYS FOUND!")
                print(f"     Main dataset keys sample: {list(jpm_main_merge_keys)[:3]}")
                print(f"     Market cap keys sample: {list(jpm_mcap_merge_keys)[:3]}")
        
        # Sample JPM data
        print("\n6. Sample JPM data from main dataset:")
        sample_cols = ['date', 'symbol', 'debt__total', 'rit', 'ritrf']
        available_cols = [col for col in sample_cols if col in jpm_main.columns]
        print(jpm_main[available_cols].head())
    
    else:
        print("4. JPM not found in main dataset - this is the primary issue!")
        print("   Checking what symbols are available:")
        unique_symbols = df['symbol'].unique()
        print(f"   Total unique symbols: {len(unique_symbols)}")
        print(f"   Sample symbols: {unique_symbols[:10]}")
        
        # Look for partial matches
        financial_symbols = [s for s in unique_symbols if any(term in str(s).upper() for term in ['BANK', 'FINANCIAL', 'JP', 'MORGAN', 'CHASE'])]
        if financial_symbols:
            print(f"   Financial-related symbols: {financial_symbols}")

if __name__ == "__main__":
    diagnose_jpm_issue()