# Bitcoin & Cryptocurrency Quantitative Research

Comprehensive quantitative research on Bitcoin trading strategies and cryptocurrency market dynamics. Two major research areas with actionable trading insights backed by data.

---

## 📚 Research Topics

### 1. [Bitcoin Strategy Backtesting (2020-2025)](1_btc_strategy_backtesting/)

**Question**: Should you ever sell Bitcoin?

Comprehensive backtesting of 15+ Bitcoin accumulation strategies over 5 years using real price data. Tests HODL, Buy the Dip, RSI, Moving Averages, Bollinger Bands, and DCA variants with and without sell rules.

**Key Finding**: ✅ **Never sell wins**
- Buy Dip 30% (no sell): **2,100% return**
- Buy Dip 30% (best sell rule): **232% return** (89% loss)
- HODL: **1,576% return**

**Conclusion**: Even with optimized sell rules, buy-and-hold crushes active trading in bull markets.

📁 [View Full Analysis](1_btc_strategy_backtesting/README.md)

---

### 2. [Crypto Market Analysis & Trading Signals](2_crypto_market_analysis/)

**Question**: When to enter and exit ETH/SOL positions?

Analyzes capital rotation patterns, correlation dynamics, and generates real-time trading signals for ETH, SOL, and HYPE. Includes alpha/beta analysis, upside/downside capture ratios, and BTC dominance tracking.

**Key Findings**:
- **Entry**: Buy ETH/SOL immediately when BTC.D peaks (77% same-day correlation)
- **Hold**: Capital stays in ETH/SOL for ~22 days (69.66% average ETH return)
- **Exit**: When ETH.D/SOL.D decline >0.3% over 7 days (signals rotation to smaller caps)
- **Current Status**: Exit signals INACTIVE ✅ (safe to hold)

**Asset Selection**:
- **SOL**: NOT defensive (goes up 50% more AND down 60% more than BTC)
- **ETH**: More defensive (beta 1.427 vs SOL 1.578)
- **HYPE**: Best alpha (275.9% annually) but highest volatility

📁 [View Full Analysis](2_crypto_market_analysis/README.md)

---

## 🎯 Quick Comparison

| Topic | Focus | Period | Key Metric | Best Strategy |
|-------|-------|--------|------------|---------------|
| **BTC Backtesting** | Should you sell? | 2020-2025 (5 years) | Total Return | Buy Dip 30% + Never Sell (2,100%) |
| **Crypto Market Analysis** | When to trade? | 2024-2025 (1 year) | Risk-Adjusted | Entry: BTC.D peak, Exit: ETH.D decline |

---

## 📁 Repository Structure

```
btc-trading-strategy-analysis/
├── README.md                           # This file (navigation hub)
├── 1_btc_strategy_backtesting/         # Bitcoin strategy backtesting
│   ├── README.md                       # Full analysis & results
│   ├── scripts/                        # Python backtesting scripts
│   ├── data/                           # Price data & results
│   ├── dashboards/                     # Interactive visualizations
│   ├── reports/                        # Yearly performance reports
│   └── CLAUDE.md                       # Developer notes
├── 2_crypto_market_analysis/           # Crypto market dynamics
│   ├── README.md                       # Entry point for all analyses
│   ├── scripts/                        # Python analysis scripts
│   ├── data/                           # Raw & processed data
│   ├── dashboards/                     # Interactive dashboards
│   └── reports/                        # 4 detailed reports
│       ├── CAPITAL_ROTATION_EXIT_SIGNALS.md
│       ├── BTC_CAPITAL_FLOW_SUMMARY.md
│       ├── ALPHA_BETA_REPORT.md
│       └── CRYPTO_CORRELATION_3YEAR.md
├── requirements.txt                    # Python dependencies (root)
└── .gitignore                          # Git ignore rules
```

---

## 🚀 Getting Started

### Installation

**Using UV (recommended):**
```bash
# Clone repository
git clone https://github.com/yongkangc/btc-trading-strategy-analysis.git
cd btc-trading-strategy-analysis

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

**Using pip:**
```bash
pip install -r requirements.txt
```

### Run Analyses

**Bitcoin Strategy Backtesting:**
```bash
# Run main backtesting analysis
python 1_btc_strategy_backtesting/scripts/btc_yfinance_analysis.py

# Generate yearly performance report
python 1_btc_strategy_backtesting/scripts/btc_yearly_analysis.py
```

**Crypto Market Analysis:**
```bash
# Capital rotation exit signals (live trading signals)
python 2_crypto_market_analysis/scripts/capital_rotation_exit_signals.py

# BTC capital flow analysis (entry timing)
python 2_crypto_market_analysis/scripts/btc_lag_correlation_1year.py

# Alpha/beta analysis (risk assessment)
python 2_crypto_market_analysis/scripts/alpha_beta_analysis.py

# 3-year correlation (long-term performance)
python 2_crypto_market_analysis/scripts/crypto_correlation_analysis.py
```

---

## 📊 Key Insights Summary

### From BTC Strategy Backtesting

1. **Never sell = maximum returns** (2,100% vs 232% with sell rules)
2. **Deeper dips = better entries** (30% dip beats 20% beats 10%)
3. **Sell rules destroy returns** even with optimized crossover detection
4. **Risk reduction requires sacrifice** (Lower drawdown = 90% less gains)
5. **Sharpe ratios favor no-sell** strategies (1.21 vs 0.72 best sell rule)

### From Crypto Market Analysis

1. **No exploitable time lag** - Capital flows same-day, not 2 weeks later
2. **BTC.D is the signal** - Monitor for peaks to time entries
3. **ETH.D/SOL.D for exits** - Decline signals rotation to smaller caps
4. **SOL is NOT defensive** - Amplifies both upside (150%) and downside (160%)
5. **Hold duration: ~22 days** from BTC.D peak to ETH.D peak

---

## 💡 Actionable Trading Strategies

### Long-Term Bitcoin Accumulation

**Strategy**: Buy Dip 30% + Never Sell

1. Calculate all-time high (ATH) daily
2. When price drops 30% from ATH → Buy with 10% of capital
3. Never sell, regardless of market conditions
4. Expected: 2,100% return over 5 years (vs HODL 1,576%)

**Why it works**: Combines dip buying (better entries) with HODL thesis (no sell pressure)

---

### Short-Term ETH/SOL Trading

**Strategy**: BTC Dominance Capital Rotation

**ENTRY**:
1. Monitor BTC.D in real-time (TradingView chart)
2. When BTC.D peaks and starts declining → Buy ETH/SOL immediately
3. Don't wait for lag - capital flows same-day

**HOLD**:
1. Monitor ETH.D and SOL.D for ~22 days
2. Average return during this period: 69.66% (ETH)
3. Watch for dominance peaks

**EXIT**:
1. Exit when ETH.D/SOL.D decline >0.3% over 7 days
2. OR when BTC.D starts rising >0.3% (capital returning to BTC)
3. Current status (Oct 5, 2025): Signals INACTIVE ✅

**Asset Selection**:
- Choose ETH for defense (lower beta: 1.427)
- Choose SOL for aggression (higher upside capture: 150%)
- Avoid SOL if you want downside protection (160% downside capture)

---

## 📈 Performance Comparison

### Bitcoin Strategies (5 years, 2020-2025)

| Strategy | Total Return | Sharpe Ratio | Max Drawdown | Philosophy |
|----------|--------------|--------------|--------------|------------|
| **Buy Dip 30%** | 2,100% | 1.21 | -76.6% | Never sell |
| **Buy Dip 20%** | 1,891% | 1.18 | -76.6% | Never sell |
| **HODL** | 1,576% | 1.11 | -76.6% | Never sell |
| **Buy Dip 30% + SMA Distance** | 232% | 0.72 | -66.1% | Sell rule |

### Crypto Assets (3 years, 2022-2025)

| Asset | Total Return | Sortino Ratio | Beta vs BTC | Alpha vs BTC |
|-------|--------------|---------------|-------------|--------------|
| **SOL** | 598.81% | 16.49 | 1.578 | -25.4% |
| **ETH** | 234.01% | 6.37 | 1.427 | +3.5% |
| **HYPE** | 714.14% | N/A (11mo) | 1.536 | +275.9% |

---

## 🛠️ Technical Stack

- **Python**: pandas, numpy, scipy, yfinance, plotly
- **Data**: Yahoo Finance API (live data)
- **Analysis**: Linear regression, correlation matrices, backtesting, peak detection
- **Visualization**: Plotly (interactive dashboards)

---

## ⚠️ Disclaimers

**This research is for educational purposes only. Not financial advice.**

### General Disclaimers
- Past performance ≠ future results
- Cryptocurrency markets are highly volatile
- Do your own research (DYOR)
- Never invest more than you can afford to lose
- Consider your risk tolerance
- Consult with financial advisors

### Specific Limitations

**BTC Backtesting:**
- Analysis covers 2020-2025 bull market (may not apply in bear markets)
- Transaction fees of 0.1% included
- No slippage or liquidity constraints modeled

**Crypto Market Analysis:**
- HYPE only 11 months of data (launched Nov 2024)
- Exit signal analysis limited to 310 days
- Simplified dominance (only BTC, ETH, SOL, HYPE)
- Market conditions change rapidly

---

## 📧 Contributing

To add new analyses:

1. Choose appropriate topic folder
2. Create script in `scripts/`
3. Save data to `data/raw/` or `data/processed/`
4. Generate report in `reports/`
5. Create dashboard in `dashboards/`
6. Update topic README with findings
7. Update this README if it's a major contribution

---

## 📝 License

MIT License - Free to use and modify

---

## 🔗 Links

- **Repository**: https://github.com/yongkangc/btc-trading-strategy-analysis
- **BTC Strategy Analysis**: [1_btc_strategy_backtesting/README.md](1_btc_strategy_backtesting/README.md)
- **Crypto Market Analysis**: [2_crypto_market_analysis/README.md](2_crypto_market_analysis/README.md)

---

**Created with**: Python, YFinance, Pandas, NumPy, Plotly, SciPy
**Data Source**: Yahoo Finance (Live data)
**Last Updated**: October 5, 2025
**Total Strategies Analyzed**: 15 (BTC) + 4 (Crypto Markets)
