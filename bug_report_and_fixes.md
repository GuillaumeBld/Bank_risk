# Bug Report and Fixes for ESG Default Risk Codebase

## Bug 1: Data Type Inconsistency in Market Cap Handling (Critical)

**File:** `esg-default-risk-phase1/scripts/2_dd_pd/dd_pd_market.py`  
**Lines:** 67-71  
**Severity:** Critical  

### Description
The code sets `market_cap` to a string value `'Marketcap_missing'` when market cap data is not available, but this column is expected to contain numeric values for downstream calculations. This creates a data type inconsistency that will cause the Merton model calculations to fail.

### Current Code:
```python
if 'market_cap' not in df.columns:
    if 'share_price' in df.columns and 'shares_outstanding' in df.columns:
        df['market_cap'] = df['share_price'] * df['shares_outstanding']
        market_cap_source = 'share_price * shares_outstanding'
    else:
        df['market_cap'] = 'Marketcap_missing'  # BUG: String in numeric column
        market_cap_source = 'missing (set to Marketcap_missing)'
```

### Impact
- Causes type errors in numerical calculations
- Makes the Merton solver fail silently or with confusing errors
- Breaks downstream distance-to-default and probability-of-default calculations

### Fix ✅ IMPLEMENTED
Replaced the string with `np.nan` to maintain data type consistency:
```python
df['market_cap'] = np.nan  # Fixed: Use NaN instead of string to maintain numeric type
market_cap_source = 'missing (set to NaN)'
```

---

## Bug 2: Insufficient NaN/Zero Handling in Financial Calculations (High)

**File:** `esg-default-risk-phase1/scripts/2_dd_pd/dd_pd_market.py`  
**Lines:** 125-127  
**Severity:** High  

### Description
The distance-to-default calculation doesn't properly validate that `asset_value` and `asset_vol` are valid numbers before performing logarithmic and division operations. This can lead to invalid financial metrics being calculated.

### Current Code:
```python
df['distance_to_default'] = (
    np.log(df['asset_value'] / df['debt__total']) + (df['rf'] - 0.5 * df['asset_vol'] ** 2) * T
) / (df['asset_vol'] * np.sqrt(T))
```

### Impact
- Produces invalid distance-to-default values when inputs are NaN or zero
- Can result in infinite or undefined values in critical risk metrics
- Makes risk assessment unreliable for affected banks

### Fix ✅ IMPLEMENTED
Added comprehensive validation with a safe calculation function:
```python
def safe_distance_to_default(row):
    """Calculate distance to default with proper validation for edge cases."""
    # Check for invalid inputs including NaN, zero, and negative values
    if (pd.isna(asset_value) or pd.isna(debt_total) or pd.isna(rf) or pd.isna(asset_vol) or
        asset_value <= 0 or debt_total <= 0 or asset_vol <= 0):
        return np.nan
    
    try:
        # Perform calculation with exception handling
        dd = (np.log(asset_value / debt_total) + (rf - 0.5 * asset_vol ** 2) * T) / (asset_vol * np.sqrt(T))
        return dd
    except (ZeroDivisionError, ValueError, OverflowError):
        return np.nan
```

---

## Bug 3: No Rate Limiting in Yahoo Finance API Calls (Medium)

**File:** `esg-default-risk-phase1/scripts/1_data_prep/fetch_marketcap_yf.py`  
**Lines:** 20-45  
**Severity:** Medium  

### Description
The script makes sequential API calls to Yahoo Finance without any rate limiting, retry logic, or proper error handling. This can lead to API rate limiting, temporary bans, and incomplete data fetching.

### Current Code:
```python
for ticker in tickers:
    try:
        yf_ticker = ticker.split('.')[0]
        t = yf.Ticker(yf_ticker)
        hist = t.history(start='2016-01-01', end='2024-01-10', interval='1d')
        # ... immediate processing without delays
    except Exception as e:
        log.write(f"Error fetching {ticker}: {e}\n")
```

### Impact
- API calls may fail due to rate limiting
- Incomplete data collection when processing many tickers
- No retry mechanism for temporary failures
- Poor performance during peak usage times

### Fix ✅ IMPLEMENTED
Added comprehensive rate limiting and retry logic:
```python
def fetch_ticker_with_retry(ticker, max_retries=3, base_delay=1.0):
    """Fetch ticker data with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            # API call logic
            return hist, shares, None
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                time.sleep(delay)
            else:
                return None, None, str(e)

# Added 100ms delay between requests for rate limiting
for i, ticker in enumerate(tickers):
    if i > 0:
        time.sleep(0.1)  # Rate limiting
    hist, shares, error = fetch_ticker_with_retry(ticker)
```

---

## Summary

These three bugs represent different categories of common software issues:
1. **Data Type Inconsistency** - A critical logic error that breaks core functionality ✅ FIXED
2. **Numerical Computation Safety** - Missing validation in financial calculations ✅ FIXED  
3. **External API Integration** - Performance and reliability issues with third-party services ✅ FIXED

## Implementation Status

✅ **All 3 bugs have been successfully fixed!**

### Files Modified:
- `esg-default-risk-phase1/scripts/2_dd_pd/dd_pd_market.py` - Fixed data type inconsistency and added numerical validation
- `esg-default-risk-phase1/scripts/1_data_prep/fetch_marketcap_yf.py` - Added rate limiting and retry logic

### Key Improvements:
1. **Robust Data Handling**: Market cap missing values now properly handled as `np.nan` instead of strings
2. **Financial Calculation Safety**: Distance-to-default calculations now validate all inputs and handle edge cases
3. **API Reliability**: Yahoo Finance fetching now includes rate limiting (100ms delays) and exponential backoff retry (up to 3 attempts)

These fixes ensure the ESG Default Risk pipeline is more robust, reliable, and production-ready for financial risk assessment.