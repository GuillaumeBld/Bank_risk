# Summary: JPM Missing Data Issue in dd_pd_market.py

## Key Findings

After analyzing the `dd_pd_market.py` script from the Bank_risk repository, I've identified the most likely reasons why JPM (JPMorgan Chase) bank produces missing data:

## Primary Issues

### 1. **Symbol Mismatch Across Datasets** (Most Likely)
- The script merges three datasets using bank symbols
- JPM may be represented differently in each dataset:
  - Main dataset: `annual_returns_clean.csv`
  - Market cap data: `all_banks_marketcap_2016_2023.csv`
  - Volatility data: `bank_annual_equity_vol.csv`
- Common variations: "JPM", "JPM.N", "JPM.US", "JPMORGAN", "CHASE"

### 2. **Missing Market Cap Data**
- Market cap is calculated as: `dec_price * shares_outstanding`
- JPM might be missing from the market cap file entirely
- Or missing price/shares data for specific time periods

### 3. **Date/Time Alignment Issues**
- The script merges on `symbol`, `Year`, and `Month`
- JPM's fiscal dates might not align with the annual returns data
- Monthly market cap data may not match annual returns timing

### 4. **Data Quality Issues**
- The Merton model requires all inputs to be positive and non-null:
  - Market cap > 0
  - Total debt > 0  
  - Equity volatility > 0
- Any missing/invalid input results in NaN output

## Script Workflow That Could Fail

1. **Load annual returns** → JPM data present
2. **Merge market cap** → JPM symbol mismatch → market_cap = NaN
3. **Merge volatility** → May work with fallback to 0.25
4. **Merton model** → Fails due to NaN market cap → Returns NaN
5. **Calculate DD/PD** → NaN inputs → Final result is missing

## Recommended Diagnostic Steps

1. **Check symbol consistency** across all three datasets
2. **Verify JPM exists** in the market cap file
3. **Check date alignment** between datasets
4. **Examine data quality** for JPM's financial data

## Files Created

- `JPM_missing_data_analysis.md` - Detailed technical analysis
- `diagnose_jpm_issue.py` - Diagnostic script to identify the specific issue
- `dd_pd_market.py` - Copy of the original script for reference

## Quick Fix Recommendations

1. **Standardize symbols** to uppercase before merging
2. **Use fuzzy matching** for JPM symbol variations
3. **Check for partial symbol matches** (e.g., contains "JPM")
4. **Add detailed logging** to track where data is lost in the pipeline

The issue is likely in the data preparation phase rather than the Merton model calculation itself.