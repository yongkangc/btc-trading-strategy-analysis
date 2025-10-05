# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bitcoin trading strategy backtesting framework that analyzes 15+ accumulation strategies using real BTC-USD price data from Yahoo Finance (2020-2025). Tests passive strategies (HODL, DCA) and active trading approaches (dip buying, technical indicators, profit-taking rules) to compare risk-adjusted returns.

**Core Question**: Should you ever sell Bitcoin?
**Verdict**: Buy-and-hold strategies (especially Buy Dip 30% without selling) significantly outperform active trading with sell rules.

## Commands

### Running Analysis

```bash
# Main strategy analysis (generates dashboard and results)
python btc_yfinance_analysis.py

# Yearly breakdown analysis (2020-2025, generates reports/ folder)
python btc_yearly_analysis.py

# Create consolidated yearly reports
python create_yearly_report.py
```

### Environment Setup

```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Using pip
pip install -r requirements.txt
```

### Dependencies
- yfinance>=0.2.66 (Yahoo Finance data)
- pandas>=2.0.0 (data processing)
- numpy>=1.24.0 (numerical operations)
- plotly>=5.14.0 (interactive charts)

## Architecture

### Core Components

**btc_yfinance_analysis.py** - Main backtesting engine
- `fetch_btc_data()`: Downloads BTC-USD from Yahoo Finance, saves to btc_raw_data.csv
- `BTCBacktest` class: Core strategy engine with 8 strategy methods
- `calculate_metrics()`: Computes performance metrics (CAGR, Sharpe, drawdown)
- `run_all_strategies()`: Executes all 15 strategies and generates dashboard

**btc_yearly_analysis.py** - Year-by-year analysis
- Splits data into yearly chunks (2020-2025)
- Runs all strategies independently per year
- Generates reports/ folder with CSV files and HTML dashboards

**create_yearly_report.py** - Consolidated yearly reporting
- Aggregates yearly performance data
- Creates comparison tables and visualizations
- Generates markdown reports

### Strategy Implementation Pattern

All strategies in `BTCBacktest` class follow this structure:

```python
def strategy_name(self, capital=10000, param=value, fee=0.001):
    prices = self.data['Close']
    cash = capital
    btc = 0
    trades = 0
    portfolio_values = []

    for i, (date, price) in enumerate(prices.items()):
        # Buy logic with fee: btc += (amount * (1 - fee)) / price
        # Update portfolio: portfolio_values.append(cash + btc * price)

    return {
        'name': 'Strategy Name',
        'portfolio': pd.Series(portfolio_values, index=prices.index),
        'returns': portfolio_series.pct_change().fillna(0),
        'trades': trades
    }
```

### Strategies Implemented

1. **HODL** (btc_yfinance_analysis.py:62-75) - Buy once and hold
2. **Buy the Dip** (btc_yfinance_analysis.py:143-256) - Buy when price drops X% from ATH
   - Variants: 10%, 20%, 30% dips
   - Optional sell rules: profit_25, sma_50, ema_21, bb_middle, ema_cross, sma_distance
3. **RSI Oversold** (btc_yfinance_analysis.py:258-293) - Buy when RSI < 30
4. **Moving Average Crossover** (btc_yfinance_analysis.py:295-336) - Golden Cross (50/200 SMA)
5. **Bollinger Bands** (btc_yfinance_analysis.py:338-378) - Buy at lower band (mean reversion)
6. **DCA** (btc_yfinance_analysis.py:111-141) - Dollar cost averaging (30-day intervals)
7. **Volatility-Adjusted DCA** - DCA with 0.5x-2x multiplier based on volatility

### Critical Implementation Details

**Sell Rule Crossover Detection** (btc_yfinance_analysis.py:180-230)
- Uses proper crossover logic to prevent excessive trading
- Checks `prev_value <= threshold and curr_value > threshold`
- Fixed bug where continuous conditions (price > SMA every day) caused 900-1200 trades
- Now correctly identifies 50-300 crossover events

**Sharpe Ratio Calculation** (btc_yfinance_analysis.py:483-484)
- Uses 365 days for Bitcoin (trades 24/7) NOT 252 days (stock market)
- Formula: `(mean_return * 365) / (std * sqrt(365))`
- Critical fix: Previous version understated Sharpe by ~20%

**Transaction Fees** (0.1% on all trades)
- Buy: `btc += (amount * (1 - fee)) / price`
- Sell: `cash += btc * price * (1 - fee)`
- Fee parameter: `fee=0.001` (0.1%)

**Position Sizing**
- Most strategies use 10% of initial capital per signal: `buy_amount = capital * 0.1`
- Max 10 trades per strategy (by design, prevents capital exhaustion)
- MA Crossover uses 100% capital (all-in/all-out)

### Performance Metrics

Calculated in `calculate_metrics()` (btc_yfinance_analysis.py:436-499):

- **Total Return**: `((final / initial) - 1) * 100`
- **CAGR**: `((final / initial) ** (1 / years) - 1) * 100`
- **Sharpe Ratio**: `(mean_return * 365) / (std * sqrt(365))` ← Note: 365 not 252
- **Max Drawdown**: `min((portfolio - rolling_max) / rolling_max)`
- **Volatility**: `std * sqrt(365)` ← Note: 365 not 252
- **Win Rate**: `percentage of profitable days`

### Output Files

**Generated by btc_yfinance_analysis.py:**
- `btc_yfinance_dashboard.html` - Interactive Plotly dashboard (4 charts)
- `btc_yfinance_results.csv` - Performance metrics table (all strategies)
- `btc_raw_data.csv` - Raw OHLCV data from Yahoo Finance

**Generated by btc_yearly_analysis.py:**
- `reports/yearly_performance_YYYY.csv` - Per-year strategy results
- `reports/yearly_summary.csv` - Aggregated metrics across years
- `reports/strategy_comparison_by_year.csv` - Strategy vs strategy comparison
- `reports/yearly_analysis_dashboard.html` - Yearly performance charts

## Key Findings (2020-2025 Analysis)

1. **Never sell = maximum returns**: Buy Dip 30% (no sell) = 2,100% vs best sell rule (SMA Distance) = 232%
2. **Sell rules destroy returns**: Even optimized crossover detection shows 89% loss vs hold-only
3. **Deeper dips = better entries**: 30% dip (2,100%) > 20% dip (1,891%) > 10% dip (1,270%)
4. **Transaction fees matter**: Excessive trading (900+ trades) causes massive fee drag
5. **Sharpe ratios**: Use 365 days for crypto (24/7 trading) not 252 (stock market)

## Common Modifications

### Testing New Dip Percentages

```python
# In btc_yfinance_analysis.py, modify run_all_strategies():
backtest.buy_the_dip(capital, dip_percent=25)  # Test 25% dip
```

### Adding New Sell Rules

```python
# In buy_the_dip(), add new elif block around line 210:
elif sell_rule == 'your_rule' and condition:
    prev_value = indicator.iloc[i-1]
    curr_value = indicator.iloc[i]
    if prev_value <= threshold and curr_value > threshold:  # Crossover
        should_sell = True
```

### Changing Initial Capital

```python
# In main execution block:
backtest.run_all_strategies(capital=50000)  # Default is 10000
```

### Adjusting Transaction Fees

```python
# Pass fee parameter to any strategy:
backtest.hodl(capital=10000, fee=0.002)  # 0.2% fee instead of 0.1%
```

## Data Source Details

- **Ticker**: BTC-USD (Yahoo Finance)
- **API**: yfinance library
- **Date Range**: 2020-01-01 to present (2,102 days as of Oct 2025)
- **Price Range**: $4,970 (low) → $123,344 (high)
- **HODL Return**: 1,576% (verified live data)
- **Update Frequency**: Run script to fetch latest data

## Known Issues & Fixes

### Recent Bug Fixes (Oct 2025)

1. **Sharpe Ratio Calculation** (FIXED)
   - Issue: Used 252 trading days (stocks) instead of 365 (Bitcoin trades 24/7)
   - Impact: All Sharpe ratios understated by ~20%
   - Fix: Updated to `np.sqrt(365)` in btc_yfinance_analysis.py:483-484

2. **Volatility Calculation** (FIXED)
   - Same 252 vs 365 issue
   - Fix: Updated to use 365 days for annualization

3. **Sell Rule Logic** (FIXED)
   - Issue: Continuous conditions (price > SMA every day) instead of crossovers
   - Impact: 900-1,200 trades (should be 50-300), destroying returns via fees
   - Fix: Implemented crossover detection in btc_yfinance_analysis.py:189-223
   - Results: Buy Dip 30% (sma_50) improved from 12.8% → 103% (8x improvement)

See IMPLEMENTATION_REVIEW.md for detailed analysis.

## Testing Strategy Changes

When modifying strategies:

1. **Verify crossover detection**: Ensure sell rules use `prev <= threshold and curr > threshold`
2. **Check transaction fees**: Confirm `(1 - fee)` multiplier on all buys/sells
3. **Validate metrics**: Use 365 days for Sharpe/volatility calculations (crypto trades 24/7)
4. **Test with small capital first**: Use `capital=1000` to verify logic before full run
5. **Compare with HODL baseline**: New strategies should justify complexity with better risk-adjusted returns

## Extending the Framework

### Adding a New Strategy

1. Add method to `BTCBacktest` class:
```python
def your_strategy(self, capital=10000, fee=0.001):
    # Follow the strategy implementation pattern above
    pass
```

2. Add to `run_all_strategies()` execution list:
```python
strategies = [
    # ... existing strategies ...
    backtest.your_strategy(capital),
]
```

3. Run analysis and check dashboard output

### Modifying Date Range

```python
# In main execution block of btc_yfinance_analysis.py:
btc_data = fetch_btc_data(start_date='2021-01-01', end_date='2024-12-31')
```

## Git Workflow

Current branch: main
Recent commits focus on bug fixes and yearly reporting features.

When committing strategy changes:
- Include before/after performance metrics in commit message
- Update README.md if results change significantly
- Regenerate dashboard HTML files for visual verification
