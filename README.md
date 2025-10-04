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
| **Buy Dip 30%** 🥇 | 2,100% | 71.2% | 1.01 | -76.6% | 10 |
| **Buy Dip 20%** | 1,891% | 68.2% | 0.98 | -76.6% | 10 |
| **HODL** | 1,576% | 63.2% | 0.92 | -76.6% | 1 |
| **Bollinger 20d** | 1,518% | 62.2% | 0.93 | -76.6% | 10 |
| **RSI <30** | 1,322% | 58.7% | 0.89 | -76.6% | 10 |
| **Buy Dip 10%** | 1,270% | 57.6% | 0.88 | -76.6% | 10 |

### Sell Rule Performance (Buy Dip 30% + Exit Strategy)
| Sell Rule | Return | CAGR | Sharpe | Max DD | Trades |
|-----------|--------|------|--------|--------|--------|
| **No Sell** 🏆 | 2,100% | 71.2% | 1.01 | -76.6% | 10 |
| **+25% Profit** | 202% | 21.2% | 0.59 | -64.6% | 77 |
| **SMA Distance** | 143% | 16.7% | 0.50 | -66.1% | 557 |
| **BB Middle** | 127% | 15.3% | 0.70 | **-19.9%** ⬇️ | 1,242 |
| **21-day EMA** | 71% | 9.8% | 0.43 | -38.2% | 1,167 |
| **EMA Cross** | 18% | 2.9% | 0.20 | -51.0% | 945 |
| **50-day SMA** | 13% | 2.1% | 0.18 | -50.9% | 922 |

### Other Strategies
| Strategy | Return | CAGR | Sharpe | Max DD | Trades |
|----------|--------|------|--------|--------|--------|
| **MA Cross 50/200** | 724% | 44.3% | 0.86 | -56.6% | 11 |
| **DCA 30d** | 376% | 31.2% | 0.77 | -56.3% | 69 |
| **Vol-Adjusted DCA** | 318% | 28.2% | 0.74 | -54.0% | 70 |

### Key Findings

**The HODL Thesis is Validated:**
1. **Never sell = maximum returns** - Buy Dip 30% with no selling beats HODL by 524%
2. **All sell rules destroy returns** - Best sell rule (+25% profit) only returns 202% vs 2,100% without selling
3. **Overtrading kills performance** - Sell rules trigger 77-1,242 trades vs just 10 for buy-only
4. **Deeper dips = better entries** - 30% dip beats 20% beats 10% (patience rewarded)
5. **Risk reduction requires sacrifice** - BB middle band reduces drawdown to -20% but loses 94% of gains

**The Verdict:** In a sustained bull market (2020-2025), selling Bitcoin early is the enemy of wealth. The winning strategy is buying severe dips (30%) and holding forever.

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
