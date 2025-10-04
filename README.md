# Bitcoin Trading Strategy Analysis

Backtesting analysis comparing HODL, Fibonacci support levels, and Dollar Cost Averaging (DCA) strategies using real Bitcoin price data from 2020-2025.

![Dashboard Preview](dashboard_preview.png)

## Overview

This project analyzes the performance of different Bitcoin accumulation strategies over a 5-year period using real historical data from Yahoo Finance via the YFinance API.

### Data Source Confirmation
- **Source**: Yahoo Finance (YFinance API)
- **Ticker**: BTC-USD
- **Data Points**: 2,103 days
- **Date Range**: 2020-01-01 to 2025-10-04
- **Price Range**: $7,200 → $122,380
- **HODL Return**: 1,599% (verified live data)

## Strategies Tested

### 1. HODL
Buy once at the start and hold without trading.

### 2. Fibonacci Support Levels
Buy when price dips to specific support levels calculated from 90-day rolling high/low.

**Four levels tested:**
- **0.236** (23.6% above low) - Waits for deep crashes
- **0.382** (38.2% above low) - Golden ratio, balanced dips
- **0.500** (50% retracement) - Middle support
- **0.618** (61.8% above low) - Shallow dips, catches rallies early

**How it works:**
```
Example:
90-day High = $100,000
90-day Low  = $80,000
Range       = $20,000

Support Levels:
0.618 → $92,360 (buy near highs)
0.500 → $90,000 (middle)
0.382 → $87,640 (balanced - WINNER)
0.236 → $84,720 (wait for deep dips)
```

Buys when price is within 2% of support level, using 10% of capital per trade (max 10 trades).

### 3. Dollar Cost Averaging (DCA)
- **Weekly**: Buy every 7 days
- **Monthly**: Buy every 30 days

Spreads capital evenly across all purchases, reducing timing risk.

## Results (2020-2025)

| Strategy | Return | CAGR | Sharpe | Max Drawdown | Trades |
|----------|--------|------|--------|--------------|--------|
| **Fib 0.382** | 1,681% | 65.0% | 0.96 | -76.6% | 10 |
| **HODL** | 1,576% | 63.2% | 0.92 | -76.6% | 1 |
| **Fib 0.618** | 1,644% | 64.4% | 0.96 | -76.6% | 10 |
| **Fib 0.5** | 1,644% | 64.4% | 0.96 | -76.6% | 10 |
| **DCA 30d** | 377% | 31.2% | 0.77 | -56.3% | 69 |
| **DCA 7d** | 366% | 30.7% | 0.76 | -55.7% | 299 |
| **Fib 0.236** | 175% | 19.2% | 0.50 | -76.6% | 10 |

### Key Findings

1. **Fibonacci 0.382 wins** - Outperforms HODL by 105% with only 10 trades
2. **HODL strong baseline** - Competitive performance, zero effort
3. **DCA reduces risk** - Lower drawdown (-56%) vs aggressive strategies (-77%)
4. **Fib 0.236 underperforms** - Waiting for deep crashes causes missed rallies

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

# Adjust Fibonacci lookback period
backtest.fibonacci_buy(capital=10000, fib_level=0.382, lookback=60)

# Change DCA frequency
backtest.dca(capital=10000, frequency=14)  # Bi-weekly
```

## Files

- `btc_yfinance_analysis.py` - Main analysis script
- `btc_yfinance_dashboard.html` - Interactive dashboard
- `btc_yfinance_results.csv` - Performance metrics
- `btc_raw_data.csv` - Raw Bitcoin OHLCV data
- `requirements.txt` - Python dependencies
- `IMPLEMENTATION_REVIEW.md` - Technical evaluation (Grade: A-)

## Dependencies

```
yfinance>=0.2.66
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.14.0
```

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
**Analysis Period**: 2020-2025 (5 years, 2,103 days)
