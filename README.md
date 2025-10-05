# Bitcoin and Cryptocurrency Quantitative Research

Comprehensive quantitative analysis of Bitcoin trading strategies and cryptocurrency market dynamics. Two independent research studies providing data-driven insights for cryptocurrency trading and investment decisions.

---

## Research Overview

This repository contains two major research areas focused on cryptocurrency markets:

**1. Bitcoin Strategy Backtesting (2020-2025)**
Empirical analysis of 15+ Bitcoin accumulation strategies over five years using historical price data. Evaluates passive strategies (HODL, DCA) against active trading approaches (dip buying, technical indicators, profit-taking rules) to determine optimal risk-adjusted returns.

**2. Crypto Market Analysis and Trading Signals (2022-2025)**
Quantitative analysis of capital rotation patterns, asset correlations, and trading signal generation for major cryptocurrencies (BTC, ETH, SOL, HYPE). Includes alpha/beta analysis, upside/downside capture ratios, and Bitcoin dominance tracking for entry and exit timing.

---

## Research Topics

### Topic 1: Bitcoin Strategy Backtesting

**Research Question**: Should investors ever sell Bitcoin, or is buy-and-hold optimal?

**Methodology**: Backtesting of 15+ accumulation strategies using real Yahoo Finance data from January 2020 to October 2025. All strategies include 0.1% transaction fees.

**Key Findings**:
- Buy Dip 30% (no sell): 2,100% total return
- Buy Dip 30% (with best sell rule): 232% total return (89% reduction)
- HODL baseline: 1,576% total return
- Sharpe ratios favor never-sell strategies: 1.21 vs 0.72

**Conclusion**: Buy-and-hold strategies significantly outperform active trading strategies with sell rules during bull market periods, even after optimizing exit signals.

[View detailed analysis →](1_btc_strategy_backtesting/README.md)

---

### Topic 2: Crypto Market Analysis and Trading Signals

**Research Question**: When should traders enter and exit ETH/SOL positions based on market dynamics?

**Methodology**: Statistical analysis of capital rotation, correlation dynamics, and dominance metrics using daily price data. Includes linear regression for alpha/beta calculations and peak detection algorithms for signal generation.

**Key Findings**:
- Entry timing: Immediate capital flow when BTC dominance peaks (77% same-day correlation)
- Hold duration: Approximately 22 days from BTC dominance peak to ETH dominance peak
- Exit timing: When ETH/SOL dominance declines >0.3% over 7 days
- Average ETH return during rotation period: 69.66%

**Current Market Status** (October 5, 2025):
- Exit signals: Inactive (safe to hold)
- BTC dominance: 96.26% (below average)
- Market phase: Alt-friendly environment

**Asset Characteristics**:
- SOL: High volatility (beta 1.578), amplifies both upside and downside movements
- ETH: Moderate volatility (beta 1.427), more defensive characteristics
- HYPE: Highest alpha (275.9% annually) with highest volatility

[View detailed analysis →](2_crypto_market_analysis/README.md)

---

## Quick Comparison

| Aspect | Bitcoin Strategy Backtesting | Crypto Market Analysis |
|--------|------------------------------|------------------------|
| **Focus** | Optimal holding strategy | Entry/exit timing |
| **Period** | 2020-2025 (5 years) | 2022-2025 (3 years) |
| **Strategies** | 15+ backtested | 4 analytical frameworks |
| **Best Result** | Buy Dip 30% + Never Sell: 2,100% | Entry at BTC.D peak, Exit at ETH.D decline |
| **Key Metric** | Total Return, Sharpe Ratio | Alpha, Beta, Capture Ratios |

---

## Repository Structure

```
btc-trading-strategy-analysis/
├── README.md
├── 1_btc_strategy_backtesting/
│   ├── README.md
│   ├── scripts/
│   │   ├── btc_yfinance_analysis.py
│   │   ├── btc_yearly_analysis.py
│   │   └── create_yearly_report.py
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── dashboards/
│   ├── reports/
│   └── CLAUDE.md
├── 2_crypto_market_analysis/
│   ├── README.md
│   ├── scripts/
│   │   ├── capital_rotation_exit_signals.py
│   │   ├── btc_lag_correlation_1year.py
│   │   ├── alpha_beta_analysis.py
│   │   ├── crypto_correlation_analysis.py
│   │   └── btc_dominance_analysis.py
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── dashboards/
│   ├── reports/
│   │   ├── CAPITAL_ROTATION_EXIT_SIGNALS.md
│   │   ├── BTC_CAPITAL_FLOW_SUMMARY.md
│   │   ├── ALPHA_BETA_REPORT.md
│   │   └── CRYPTO_CORRELATION_3YEAR.md
│   └── requirements.txt
├── requirements.txt
└── .gitignore
```

---

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Installation with UV (recommended)

```bash
git clone https://github.com/yongkangc/btc-trading-strategy-analysis.git
cd btc-trading-strategy-analysis

uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

uv pip install -r requirements.txt
```

### Installation with pip

```bash
git clone https://github.com/yongkangc/btc-trading-strategy-analysis.git
cd btc-trading-strategy-analysis

pip install -r requirements.txt
```

---

## Running the Analyses

### Bitcoin Strategy Backtesting

Run the main backtesting analysis:
```bash
python 1_btc_strategy_backtesting/scripts/btc_yfinance_analysis.py
```

Generate yearly performance breakdown:
```bash
python 1_btc_strategy_backtesting/scripts/btc_yearly_analysis.py
```

### Crypto Market Analysis

Generate capital rotation exit signals:
```bash
python 2_crypto_market_analysis/scripts/capital_rotation_exit_signals.py
```

Analyze BTC dominance capital flow patterns:
```bash
python 2_crypto_market_analysis/scripts/btc_lag_correlation_1year.py
```

Calculate alpha and beta metrics:
```bash
python 2_crypto_market_analysis/scripts/alpha_beta_analysis.py
```

Run 3-year correlation analysis:
```bash
python 2_crypto_market_analysis/scripts/crypto_correlation_analysis.py
```

---

## Key Research Insights

### From Bitcoin Strategy Backtesting

1. **Never-sell strategies maximize returns**: Buy Dip 30% without selling outperforms the best sell-rule strategy by 1,868 percentage points (2,100% vs 232%)

2. **Deeper dips provide better entry points**: 30% dip outperforms 20% dip, which outperforms 10% dip

3. **Sell rules significantly reduce returns**: Even optimized crossover-based sell rules destroy 89% of potential gains

4. **Risk reduction requires substantial return sacrifice**: Reducing maximum drawdown by 28 percentage points (from -76.6% to -48.7%) costs 90% of total returns

5. **Sharpe ratios favor passive strategies**: No-sell strategies achieve Sharpe ratios of 1.11-1.21 versus 0.52-0.86 for sell-rule strategies

### From Crypto Market Analysis

1. **No exploitable time lag exists**: Capital flows to altcoins same-day when BTC dominance peaks (77% correlation), not after 2-week or 1-month delays

2. **BTC dominance is the primary signal**: Monitoring BTC.D peaks provides optimal entry timing for altcoin positions

3. **Dominance metrics indicate exits**: ETH.D and SOL.D declines signal capital rotation to smaller market cap altcoins

4. **SOL exhibits aggressive characteristics**: 150% upside capture and 160% downside capture versus BTC (amplifies movements in both directions)

5. **Average hold duration is 22 days**: From BTC dominance peak to ETH dominance peak, with 69.66% average return

---

## Trading Strategy Applications

### Long-term Bitcoin Accumulation

**Strategy**: Buy Dip 30% with No Sell Rule

**Implementation**:
1. Calculate Bitcoin all-time high (ATH) on a daily basis
2. When current price drops 30% below ATH, allocate 10% of available capital to purchase
3. Maintain position indefinitely without selling
4. Expected 5-year return: 2,100% (based on 2020-2025 backtest)

**Rationale**: Combines strategic entry timing (buying significant dips) with the HODL thesis (eliminating sell pressure and transaction costs)

### Short-term Altcoin Trading

**Strategy**: BTC Dominance Capital Rotation

**Entry Phase**:
1. Monitor BTC dominance (BTC.D) in real-time using market data
2. Identify BTC.D peaks and trend reversals
3. Enter ETH/SOL positions immediately upon BTC.D decline (same-day execution critical)

**Hold Phase**:
1. Monitor ETH dominance (ETH.D) and SOL dominance (SOL.D) for approximately 22 days
2. Track for dominance peaks and reversals
3. Expected return: 50-70% during rotation period

**Exit Phase**:
1. Exit positions when ETH.D or SOL.D decline >0.3% over 7-day period
2. Alternative exit: When BTC.D begins rising >0.3% (capital returning to Bitcoin)
3. As of October 5, 2025: Exit signals inactive (hold positions)

**Asset Selection Criteria**:
- Choose ETH for lower volatility exposure (beta 1.427)
- Choose SOL for higher return potential with increased volatility (beta 1.578)
- Avoid SOL if downside protection is priority (160% downside capture)

---

## Performance Summary

### Bitcoin Strategies (5-year period, 2020-2025)

| Strategy | Total Return | Sharpe Ratio | Max Drawdown | Trading Philosophy |
|----------|--------------|--------------|--------------|-------------------|
| Buy Dip 30% | 2,100% | 1.21 | -76.6% | Never sell |
| Buy Dip 20% | 1,891% | 1.18 | -76.6% | Never sell |
| HODL | 1,576% | 1.11 | -76.6% | Never sell |
| Buy Dip 30% + SMA Distance | 232% | 0.72 | -66.1% | Active sell rule |

### Cryptocurrency Assets (3-year period, 2022-2025)

| Asset | Total Return | Sortino Ratio | Beta vs BTC | Alpha vs BTC |
|-------|--------------|---------------|-------------|--------------|
| SOL | 598.81% | 16.49 | 1.578 | -25.4% |
| ETH | 234.01% | 6.37 | 1.427 | +3.5% |
| HYPE | 714.14% | N/A (11 months) | 1.536 | +275.9% |

---

## Technical Stack

**Programming Language**: Python 3.8+

**Data Sources**: Yahoo Finance API (yfinance library)

**Core Libraries**:
- pandas: Data manipulation and analysis
- numpy: Numerical computing
- scipy: Statistical calculations and optimization
- yfinance: Market data retrieval
- plotly: Interactive visualization

**Analysis Methods**:
- Linear regression for alpha/beta calculations
- Pearson correlation for asset relationships
- Peak detection algorithms (scipy.signal)
- Monte Carlo simulation for backtesting
- Rolling window calculations for technical indicators

---

## Limitations and Disclaimers

### General Disclaimers

This research is for educational and informational purposes only and does not constitute financial advice, investment advice, trading advice, or any other type of professional advice.

**Important Considerations**:
- Past performance does not guarantee future results
- Cryptocurrency markets exhibit high volatility and significant risk
- All investors should conduct independent research (DYOR)
- Only invest capital you can afford to lose entirely
- Individual risk tolerance varies significantly
- Consult with qualified financial advisors before making investment decisions

### Specific Research Limitations

**Bitcoin Strategy Backtesting**:
- Analysis covers 2020-2025 period, predominantly a bull market
- Transaction fees fixed at 0.1% (may vary by exchange and volume)
- No modeling of slippage, liquidity constraints, or market impact
- Assumes perfect execution at daily close prices
- Does not account for tax implications

**Crypto Market Analysis**:
- HYPE token limited to 11 months of data (launched November 2024)
- Exit signal analysis constrained to 310-day period
- Simplified dominance calculations (BTC, ETH, SOL, HYPE only; excludes broader market)
- Market dynamics subject to rapid changes due to regulatory developments, technological advances, and macroeconomic conditions
- Correlation patterns may shift in different market cycles

---

## Contributing

Contributions to expand or improve the research are welcome. To contribute:

1. Select appropriate topic folder for new analysis
2. Create analysis script in `scripts/` directory
3. Store raw data in `data/raw/` and processed results in `data/processed/`
4. Generate comprehensive report in `reports/` directory
5. Create interactive visualization in `dashboards/` directory
6. Update topic-specific README with findings
7. Update root README for significant contributions
8. Submit pull request with detailed description

---

## License

MIT License - Open source and free to use, modify, and distribute

---

## Repository Information

**Repository**: https://github.com/yongkangc/btc-trading-strategy-analysis
**Data Source**: Yahoo Finance (real-time market data)
**Analysis Period**: 2020-2025 (Bitcoin strategies), 2022-2025 (market analysis)
**Total Strategies Analyzed**: 15 (Bitcoin) + 4 (market frameworks)
**Last Updated**: October 5, 2025

---

## Contact and Further Reading

For detailed methodology, implementation notes, and extended analysis:
- Bitcoin Strategy Backtesting: [1_btc_strategy_backtesting/README.md](1_btc_strategy_backtesting/README.md)
- Crypto Market Analysis: [2_crypto_market_analysis/README.md](2_crypto_market_analysis/README.md)
- Developer Notes: [1_btc_strategy_backtesting/CLAUDE.md](1_btc_strategy_backtesting/CLAUDE.md)
