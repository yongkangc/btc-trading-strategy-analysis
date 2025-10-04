# Bitcoin Trading Strategy Analysis

Comprehensive backtesting comparing 15+ Bitcoin accumulation strategies using real price data from 2020-2025. Tests HODL, Buy the Dip (with/without sell rules), RSI, Moving Averages, Bollinger Bands, and DCA variants to answer: **Should you ever sell Bitcoin?**

![Dashboard Preview](dashboard_preview.png)

## Overview

This project analyzes the performance of popular Bitcoin trading strategies over a 5-year period (2020-2025) using real historical data from Yahoo Finance. Tests passive strategies (HODL, DCA) and active trading approaches (dip buying, technical indicators, profit-taking rules) to determine optimal risk-adjusted returns.

### Data Source Confirmation
- **Source**: Yahoo Finance (YFinance API)
- **Ticker**: BTC-USD
- **Data Points**: 2,102 days
- **Date Range**: 2020-01-01 to 2025-10-02
- **Price Range**: $4,970 → $123,344
- **HODL Return**: 1,576% (verified live data)
- **Transaction Fees**: 0.1% included on all buys and sells

## Strategies Tested

### 1. HODL (Baseline)
Buy once at the start and hold forever. The ultimate passive strategy.

### 2. Buy the Dip (No Sell)
Buy when price drops from recent all-time high:
- **10% Dip**: Buy when -10% from ATH
- **20% Dip**: Buy when -20% from ATH
- **30% Dip**: Buy when -30% from ATH (WINNER - 2,100% return)

Uses 10% of capital per dip signal. Never sells.

### 3. Buy Dip 30% + Sell Rules
Tests 6 different profit-taking strategies on the winning 30% dip strategy:
- **+25% Profit**: Sell when up 25% from average buy price
- **50-day SMA**: Sell when price crosses above 50-day moving average
- **21-day EMA**: Sell when price crosses above 21-day exponential moving average
- **Bollinger Middle**: Sell when price reaches 20-day moving average
- **EMA Crossover**: Sell when 9-EMA crosses above 21-EMA
- **SMA Distance**: Sell when price is 20% above 200-day SMA

### 4. RSI Oversold
Buy when Relative Strength Index drops below 30 (oversold condition). Classic momentum indicator.

### 5. Moving Average Crossover (Golden Cross)
Buy when 50-day MA crosses above 200-day MA. Sell when it crosses below (Death Cross). Trend-following strategy.

### 6. Bollinger Bands
Buy when price touches lower band (mean - 2σ). Mean reversion strategy.

### 7. Dollar Cost Averaging (DCA)
- **Standard DCA**: Buy every 30 days
- **Volatility-Adjusted DCA**: Buy more during high volatility (0.5x-2x multiplier)

## Results (2020-2025)

### Top Performers (Never Sell)
| Strategy | Return | CAGR | Sharpe | Max DD | Trades |
|----------|--------|------|--------|--------|--------|
| **Buy Dip 30%** 🥇 | 2,100% | 71.2% | **1.21** | -76.6% | 10 |
| **Buy Dip 20%** | 1,891% | 68.2% | **1.18** | -76.6% | 10 |
| **HODL** | 1,576% | 63.2% | **1.11** | -76.6% | 1 |
| **Bollinger 20d** | 1,518% | 62.2% | **1.12** | -76.6% | 10 |
| **RSI <30** | 1,322% | 58.7% | **1.07** | -76.6% | 10 |
| **Buy Dip 10%** | 1,270% | 57.6% | **1.06** | -76.6% | 10 |

### Sell Rule Performance (Buy Dip 30% + Exit Strategy) - FIXED
| Sell Rule | Return | CAGR | Sharpe | Max DD | Trades |
|-----------|--------|------|--------|--------|--------|
| **No Sell** 🏆 | 2,100% | 71.2% | **1.21** | -76.6% | 10 |
| **SMA Distance** | 232% | 23.2% | **0.72** | -66.1% | 239 |
| **BB Middle** | 219% | 22.4% | **0.86** | **-48.7%** ⬇️ | 740 |
| **+25% Profit** | 202% | 21.2% | **0.71** | -64.6% | 77 |
| **21-day EMA** | 181% | 19.7% | **0.72** | -56.4% | 598 |
| **EMA Cross** | 139% | 16.3% | **0.59** | -59.3% | 317 |
| **50-day SMA** | 103% | 13.1% | **0.52** | -60.0% | 299 |

### Other Strategies
| Strategy | Return | CAGR | Sharpe | Max DD | Trades |
|----------|--------|------|--------|--------|--------|
| **MA Cross 50/200** | 724% | 44.3% | **1.03** | -56.6% | 11 |
| **DCA 30d** | 376% | 31.2% | **0.92** | -56.3% | 69 |
| **Vol-Adjusted DCA** | 318% | 28.2% | **0.89** | -54.0% | 70 |

### Key Findings

**The HODL Thesis is Validated:**
1. **Never sell = maximum returns** - Buy Dip 30% with no selling beats HODL by 524%
2. **Sell rules significantly underperform** - Best sell rule (SMA Distance: 232%) vs 2,100% without selling = 89% loss
3. **Crossover detection improves results** - With proper implementation, sell rules now show 103-232% returns (vs 13-143% before fix)
4. **Deeper dips = better entries** - 30% dip beats 20% beats 10% (patience rewarded)
5. **Risk reduction requires sacrifice** - BB middle band reduces drawdown to -48.7% but still loses 90% of gains
6. **Sharpe ratios corrected** - Now using 365 days (crypto trades 24/7) instead of 252 days (stocks), ~20% higher

**The Verdict:** Even with optimized sell rules, buy-and-hold strategies (HODL, Buy Dip without selling) crush active trading. In 2020-2025 bull market, the winning strategy is buying severe dips (30%) and holding forever.

## Installation

**Using UV (recommended):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Using pip:**
```bash
pip install -r requirements.txt
```

## Usage

Run the analysis:
```bash
python btc_yfinance_analysis.py
```

**Outputs generated:**
1. `btc_yfinance_dashboard.html` - Interactive Plotly charts
2. `btc_yfinance_results.csv` - Performance metrics table
3. `btc_raw_data.csv` - Raw Bitcoin price data (OHLCV)

## Performance Metrics

- **Total Return** - Overall percentage gain/loss
- **CAGR** - Compound Annual Growth Rate (annualized)
- **Sharpe Ratio** - Risk-adjusted returns (higher is better)
- **Max Drawdown** - Largest peak-to-trough decline
- **Volatility** - Annualized standard deviation of returns
- **Win Rate** - Percentage of profitable days
- **Trades** - Number of buy transactions

## Customization

Modify parameters in the script:

```python
# Change initial capital
backtest.run_all_strategies(capital=50000)

# Test custom dip percentage with sell rule
backtest.buy_the_dip(capital=10000, dip_percent=25, sell_rule='profit_25')

# Available sell rules:
# 'profit_25', 'sma_50', 'ema_21', 'bb_middle', 'ema_cross', 'sma_distance'

# Change DCA frequency
backtest.dca(capital=10000, frequency=14)  # Bi-weekly DCA
```

## Files

- `btc_yfinance_analysis.py` - Main analysis script with sell rule implementations
- `btc_yfinance_dashboard.html` - Interactive Plotly dashboard (4 charts)
- `btc_yfinance_results.csv` - Performance metrics (all 15 strategies)
- `btc_raw_data.csv` - Raw Bitcoin OHLCV data (2,102 days)
- `dashboard_preview.png` - Dashboard screenshot
- `requirements.txt` - Python dependencies

## Dependencies

```
yfinance>=0.2.66
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.14.0
```

## Code Quality & Bug Fixes

### Recent Improvements (Oct 2025)

**Three critical bugs were identified and fixed:**

1. **Sharpe Ratio Calculation (FIXED)** ✅
   - **Issue**: Used 252 trading days (stock market) instead of 365 (Bitcoin trades 24/7)
   - **Impact**: All Sharpe ratios were understated by ~20%
   - **Fix**: Updated calculation to use `np.sqrt(365)` for Bitcoin
   - **Result**: HODL Sharpe improved from 0.92 → **1.11** (+20%)

2. **Volatility Calculation (FIXED)** ✅
   - **Issue**: Same 252 vs 365 problem
   - **Impact**: All volatility metrics were understated by ~20%
   - **Fix**: Updated to use 365 days for annualization

3. **Sell Rule Logic (FIXED)** ✅
   - **Issue**: Strategies triggered on continuous conditions (price > SMA every day) instead of crossovers
   - **Impact**: Massive overtrading (900-1,200 trades instead of 50-300), destroying returns via fee drag
   - **Fix**: Implemented proper crossover detection (previous day below, current day above)
   - **Result**:
     - Buy Dip 30% (sma_50): **12.8%** → **103%** (8x improvement)
     - Buy Dip 30% (bb_middle): **127%** → **219%** (1.7x improvement)
     - Trade counts reduced by 50-75%

**All results in this README reflect the corrected implementation.**

---

## Disclaimer

This analysis is for educational purposes only. Past performance does not guarantee future results.

- Do your own research
- Never invest more than you can afford to lose
- Consider your risk tolerance
- Consult with financial advisors

## License

MIT License - Free to use and modify

---

**Created with**: Python, YFinance, Pandas, NumPy, Plotly
**Data Source**: Yahoo Finance (Live data via YFinance API)
**Analysis Period**: 2020-2025 (5 years, 2,102 days)
**Strategies Tested**: 15 (buy-only + 6 sell rule variants)
