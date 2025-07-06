# Analysis: Missing Data for JPM Bank in dd_pd_market.py

## Overview
The script `dd_pd_market.py` calculates Distance-to-Default (DD) and Probability of Default (PD) using the Merton model for banks based on market equity data. This analysis identifies potential reasons why JPM (JPMorgan Chase) bank produces missing data.

## Identified Issues

### 1. **Data Merging Problems**

#### Market Cap Data Merge (Lines 54-55)
```python
df = df.merge(marketcap[['symbol', 'Year', 'Month', 'market_cap']], 
              on=['symbol', 'Year', 'Month'], how='left', suffixes=('', '_mcap'))
```

**Potential Issues:**
- **Symbol Mismatch**: JPM's symbol might be represented differently across datasets
- **Date Alignment**: JPM's fiscal dates might not align properly between annual returns and monthly market cap data
- **Missing Market Cap Data**: JPM might be missing from the `all_banks_marketcap_2016_2023.csv` file

#### Equity Volatility Merge (Lines 70-71)
```python
merge_cols = ['symbol', 'Year']
df = df.merge(equity_vol[['symbol', 'Year', 'equity_vol']], on=merge_cols, how='left')
```

**Potential Issues:**
- JPM might be missing from the `bank_annual_equity_vol.csv` file
- Symbol standardization issues between datasets

### 2. **Symbol Standardization Issues**

#### Ticker Prefix Function (Lines 33-36)
```python
def get_prefix(ticker):
    if pd.isna(ticker):
        return None
    return str(ticker).split('.')[0]
```

**Potential Issues:**
- JPM might use different ticker formats (e.g., "JPM.N", "JPM.US", "JPM")
- Case sensitivity issues ("JPM" vs "jpm")
- Special characters or spaces in ticker symbols

### 3. **Market Cap Calculation Issues**

#### Market Cap Calculation (Line 40)
```python
marketcap['market_cap'] = marketcap['dec_price'] * marketcap['shares_outstanding']
```

**Potential Issues:**
- Missing `dec_price` for JPM in specific periods
- Missing `shares_outstanding` for JPM
- Zero or negative values that get filtered out

### 4. **Merton Model Input Validation**

#### Strict Input Validation (Lines 82-84)
```python
if np.isnan(E) or np.isnan(F) or np.isnan(sigma_E) or E <= 0 or F <= 0 or sigma_E <= 0:
    return np.nan, np.nan, 'input_nan_or_invalid'
```

**Potential Issues:**
- **Market Cap (E)**: JPM's market cap is NaN, zero, or negative
- **Total Debt (F)**: JPM's debt data is missing or invalid
- **Equity Volatility (sigma_E)**: JPM's volatility data is missing or zero

### 5. **Data Scaling Issues**

#### Debt Scaling (Line 67)
```python
df['debt__total'] = df['debt__total'] * 1_000
```

**Potential Issues:**
- JPM's debt might already be in dollars instead of thousands
- Inconsistent units across different banks
- Missing debt data gets converted to NaN after scaling

## Most Likely Root Causes

### 1. **Symbol Inconsistency**
JPM might be represented differently across the three main data sources:
- `annual_returns_clean.csv` (main dataset)
- `all_banks_marketcap_2016_2023.csv` (market cap data)
- `bank_annual_equity_vol.csv` (volatility data)

### 2. **Missing Market Cap Data**
JPM might be completely missing from the market cap dataset or have missing values for specific time periods.

### 3. **Date/Period Alignment Issues**
JPM's data might be available but for different time periods than expected, causing merge failures.

### 4. **Data Quality Issues**
JPM might have zero or negative values for critical inputs that get filtered out by the Merton model validation.

## Debugging Recommendations

### 1. **Check Symbol Consistency**
```python
# Check how JPM appears in each dataset
print("JPM in main dataset:", df[df['symbol'].str.contains('JPM', na=False)]['symbol'].unique())
print("JPM in market cap:", marketcap[marketcap['symbol'].str.contains('JPM', na=False)]['symbol'].unique())
print("JPM in volatility:", equity_vol[equity_vol['symbol'].str.contains('JPM', na=False)]['symbol'].unique())
```

### 2. **Verify Data Availability**
```python
# Check if JPM has market cap data
jpm_marketcap = marketcap[marketcap['symbol'] == 'JPM']
print(f"JPM market cap records: {len(jpm_marketcap)}")
print(f"Years available: {jpm_marketcap['Year'].unique()}")
```

### 3. **Check Merge Results**
```python
# Check merge success for JPM
jpm_data = df[df['symbol'] == 'JPM']
print(f"JPM rows after merge: {len(jpm_data)}")
print(f"Market cap missing: {jpm_data['market_cap'].isna().sum()}")
print(f"Equity vol missing: {jpm_data['equity_vol'].isna().sum()}")
```

### 4. **Examine Merton Model Inputs**
```python
# Check JPM's inputs to Merton model
jpm_inputs = jpm_data[['market_cap', 'debt__total', 'equity_vol', 'rf']]
print("JPM Merton inputs:")
print(jpm_inputs.describe())
print(f"Invalid inputs: {(jpm_inputs <= 0).any(axis=1).sum()}")
```

## Quick Fixes to Try

### 1. **Case-Insensitive Symbol Matching**
```python
# Make symbol matching case-insensitive
df['symbol'] = df['symbol'].str.upper()
marketcap['symbol'] = marketcap['symbol'].str.upper()
equity_vol['symbol'] = equity_vol['symbol'].str.upper()
```

### 2. **More Flexible Symbol Matching**
```python
# Try partial matching for JPM
jpm_patterns = ['JPM', 'JPMORGAN', 'JP MORGAN']
for pattern in jpm_patterns:
    mask = marketcap['symbol'].str.contains(pattern, na=False, case=False)
    if mask.any():
        print(f"Found JPM using pattern '{pattern}': {marketcap[mask]['symbol'].unique()}")
```

### 3. **Add Fallback for Missing Volatility**
The script already includes a fallback (sigma = 0.25), but this might not be working properly for JPM.

## Conclusion

The most likely cause of missing data for JPM is **symbol inconsistency** across the different datasets, followed by **missing market cap data** or **data quality issues**. The script's strict validation in the Merton model means that any missing or invalid input will result in NaN outputs for Distance-to-Default and Probability of Default calculations.