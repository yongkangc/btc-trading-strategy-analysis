# BTC Trading Strategy Comparison: HODL vs Active Trading

## 📊 Project Overview

This project analyzes whether **HODL-ing** (buy and hold) or **active trading strategies** perform better for Bitcoin over different time periods (2017-2021, 2022-2025, etc.).

## 🎯 Strategies Analyzed

### 1. **HODL** (Baseline)
- Buy Bitcoin once at the start
- Hold without any trading
- Simplest strategy with minimal fees

### 2. **Fibonacci Retracement Buying**
- Buy when price touches Fibonacci support levels:
  - **Level 0.236** (23.6% retracement)
  - **Level 0.382** (38.2% retracement - Golden ratio)
  - **Level 0.5** (50% retracement)
  - **Level 0.618** (61.8% retracement)
- Uses 90-day rolling high/low for calculation
- Buys 10% of initial capital per signal

### 3. **Dollar Cost Averaging (DCA)**
- **Weekly DCA** - Buy every 7 days
- **Monthly DCA** - Buy every 30 days
- Spreads capital evenly across all purchases
- Reduces timing risk

## 📈 Key Metrics

For each strategy, we calculate:

| Metric | Description |
|--------|-------------|
| **Total Return** | Overall percentage gain/loss |
| **CAGR** | Compound Annual Growth Rate |
| **Sharpe Ratio** | Risk-adjusted returns (higher is better) |
| **Max Drawdown** | Largest peak-to-trough decline |
| **Volatility** | Annualized standard deviation of returns |
| **Win Rate** | Percentage of profitable days |
| **Number of Trades** | Total buy transactions |

## 📁 Files Generated

### Main Outputs
1. **btc_strategy_dashboard.html** - Interactive dashboard with:
   - Portfolio value over time (all strategies)
   - Performance comparison bar chart
   - Returns distribution box plots
   - Risk-return scatter plot
   - Drawdown analysis

2. **btc_strategy_results.csv** - Complete results table

3. **btc_period_analysis.csv** - Performance by time period (2017-2021, 2022-2025, etc.)

### Python Scripts
1. **btc_comprehensive_analysis.py** - Main analysis with simulated data
2. **btc_real_data_analysis.py** - Analysis using real BTC data (requires JSON input)

## 🚀 How to Use

### Prerequisites

**Using UV (Recommended - Fast & Modern):**
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Using pip (Traditional):**
```bash
pip install -r requirements.txt
```

### Option 1: Run with Real Data (Recommended - YFinance)
```bash
python btc_yfinance_analysis.py
```
This fetches real Bitcoin data from Yahoo Finance (2020-present) and runs all strategies.

### Option 2: Run with Simulated Data
```bash
python btc_comprehensive_analysis.py
```
Uses synthetic data for demonstration purposes.

### Option 3: Run with Custom Data
```bash
python btc_real_data_analysis.py
```
Loads data from `btc_data.json` (custom format).

## 📊 Sample Results (Simulated Data)

### Performance Ranking
1. **Fibonacci Buy (Level 0.236)** - 251,900% return
2. **Fibonacci Buy (Level 0.382)** - 234,670% return
3. **HODL** - 190,892% return
4. **DCA (Monthly)** - 53,097% return
5. **DCA (Weekly)** - 51,773% return

### Key Insights
- **Best Strategy**: Fibonacci Level 0.236 buying
- **Outperformance vs HODL**: +61,007%
- **Best Sharpe Ratio**: 2.06 (Fib 0.236)
- **Lowest Drawdown**: DCA strategies (~40%)

## 🎨 Dashboard Features

The interactive HTML dashboard includes:

1. **Time Series Chart** - Track all strategies simultaneously
2. **Performance Bars** - Quick visual comparison
3. **Risk Analysis** - Box plots showing return distributions
4. **Risk-Return Plot** - Find the optimal strategy for your risk tolerance

## 💡 Key Findings

### HODL vs Active Trading
- In strongly trending markets (2020-2021), **HODL often wins**
- In volatile/ranging markets (2022-2023), **Fibonacci buying can outperform**
- **DCA reduces risk** but may underperform in bull markets

### Strategy Recommendations
- **Risk-averse investors**: DCA (smoother returns, lower drawdown)
- **Trend followers**: HODL (simplest, no timing needed)
- **Active traders**: Fibonacci buying (requires discipline, can outperform)

## 🔧 Customization

You can easily modify:

```python
# Change initial capital
backtest.run_all_strategies(initial_capital=50000)

# Adjust Fibonacci lookback period
strategy_fibonacci_buy(initial_capital=10000, buy_level=0.382, lookback=60)

# Change DCA frequency
strategy_dca(initial_capital=10000, frequency=14)  # Bi-weekly
```

## 📚 Dependencies

```bash
pip install pandas numpy plotly
```

## ⚠️ Disclaimer

This analysis is for **educational purposes only**. Past performance does not guarantee future results. Always:
- Do your own research (DYOR)
- Never invest more than you can afford to lose
- Consider your risk tolerance
- Consult with financial advisors

## 🤝 Contributing

Feel free to:
- Add new trading strategies
- Improve visualization
- Optimize code performance
- Add more comprehensive backtesting features

## 📄 License

MIT License - Free to use and modify

---

**Created with:** Python, Pandas, NumPy, Plotly  
**Data Source:** Crypto pricing APIs (CoinGecko, CoinMarketCap, DeFiLlama)  
**Analysis Period:** 2020-2025 (5 years)

Happy Trading! 🚀📈
