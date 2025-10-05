# Cryptocurrency Market Analysis and Trading Signals

Comprehensive quantitative analysis of cryptocurrency markets focusing on capital rotation dynamics, correlation patterns, and systematic trading signal generation. Employs live data from Yahoo Finance to analyze BTC, ETH, SOL, and HYPE across multiple analytical frameworks.

![3-Year Correlation Dashboard](reports/images/crypto_correlation_dashboard.png)

---

## Research Overview

This research provides quantitative analysis of cryptocurrency market dynamics through four complementary analytical frameworks:

1. **Capital Rotation Exit Signals** - Systematic exit timing for altcoin positions
2. **BTC Capital Flow Analysis** - Entry timing based on Bitcoin dominance patterns
3. **Alpha/Beta Risk Assessment** - Asset characterization and position sizing guidance
4. **3-Year Correlation Analysis** - Long-term performance and diversification metrics

**Primary Research Question**: When should traders optimally enter and exit ETH/SOL positions based on observable market dynamics?

**Methodology**: Statistical analysis of capital rotation, correlation dynamics, and dominance metrics using daily price data. Includes linear regression for alpha/beta calculations and peak detection algorithms for signal generation.

---

## Analysis Reports

### 1. Capital Rotation Exit Signals

**Research Question**: After BTC dominance drops and capital flows to ETH/SOL, how long does capital remain before rotating to smaller market cap assets?

**Trading Application**: Exit signal generation for ETH/SOL positions

**Key Findings**:
- Average hold duration: Approximately 22 days from BTC dominance peak to ETH dominance peak
- Average ETH return during rotation period: 69.66%
- Exit signal criteria: ETH.D/SOL.D decline exceeding 0.3% over 7-day period, or BTC.D increase exceeding 0.3%
- Current market status (October 5, 2025): Exit signals inactive, positions may be maintained

**Documentation**: [Full Report](reports/CAPITAL_ROTATION_EXIT_SIGNALS.md) | [Interactive Dashboard](dashboards/capital_rotation_exit_signals_dashboard.html)

---

### 2. BTC Capital Flow Analysis

**Research Question**: After Bitcoin dominance reaches local peaks, where does capital flow and what is the timing?

**Trading Application**: Entry timing for ETH/SOL positions based on BTC dominance reversals

**Key Findings**:
- Capital flows to ETH and SOL occur same-day when BTC dominance peaks (77% correlation)
- No exploitable time lag exists (2-week and 1-month lag strategies destroy correlation)
- When BTC.D declines: ETH +6.77% average, SOL +4.86% average, BTC +1.30% average
- ETH outperforms BTC by 5.5x during BTC dominance decline periods

**Documentation**: [Full Report](reports/BTC_CAPITAL_FLOW_SUMMARY.md) | [Interactive Dashboard](dashboards/btc_capital_flow_1year_dashboard.html)

---

### 3. Alpha/Beta Risk Assessment

**Research Question**: Do ETH and SOL provide asymmetric upside/downside capture ratios relative to BTC?

**Trading Application**: Asset selection and position sizing based on risk tolerance and return objectives

**Key Findings**:
- **SOL**: 150% upside capture, 160% downside capture (amplifies movements in both directions, not defensive)
- **ETH**: 133% upside capture, 131% downside capture (more balanced risk profile, relatively defensive)
- **SOL Beta**: 1.578 (highest volatility among analyzed assets), Alpha: -25.4% (underperforms risk-adjusted)
- **ETH Beta**: 1.427 (lowest volatility among altcoins), Alpha: +3.5% (outperforms risk-adjusted)
- **HYPE**: Highest alpha (275.9% annually) with elevated volatility (beta: 1.536)

**Documentation**: [Full Report](reports/ALPHA_BETA_REPORT.md) | [Interactive Dashboard](dashboards/alpha_beta_dashboard.html)

---

### 4. 3-Year Correlation Analysis

**Analysis Period**: October 2022 - October 2025 (3 years)

**Trading Application**: Long-term performance comparison and portfolio diversification analysis

**Key Findings**:
- **SOL**: 598.81% total return, 901.42% annualized return, Sortino ratio 16.49
- **ETH**: 234.01% total return, 317.53% annualized return, Sortino ratio 6.37
- **HYPE**: 714.14% total return (11-month observation period only)
- **ETH-SOL correlation**: 76% (high co-movement, limited diversification benefit)

**Documentation**: [Full Report](reports/CRYPTO_CORRELATION_3YEAR.md) | [Interactive Dashboard](dashboards/crypto_correlation_dashboard.html)

---

## Integrated Trading Strategy

### Entry Phase (BTC Capital Flow Analysis)

1. Monitor Bitcoin Dominance (BTC.D) in real-time using market data
2. Identify BTC.D peaks and trend reversals
3. Enter ETH/SOL positions immediately upon BTC.D decline (same-day execution critical, 77% correlation)

**Rationale**: Capital flows occur same-day with no exploitable time lag. Delayed entry (2-week or 1-month lag) destroys correlation and reduces expected returns.

### Hold Phase (Capital Rotation Analysis)

1. Monitor ETH dominance (ETH.D) and SOL dominance (SOL.D) for approximately 22 days following entry
2. Track for dominance metric peaks and reversals
3. Expected return during hold period: 50-70% (based on historical 69.66% average for ETH)

### Exit Phase (Capital Rotation Exit Signals)

1. Exit positions when ETH.D or SOL.D decline exceeds 0.3% over 7-day measurement period
2. Alternative exit trigger: BTC.D begins rising by more than 0.3% (indicating capital return to Bitcoin)
3. Current market status (October 5, 2025): Exit signals inactive, positions may be maintained

### Asset Selection Criteria (Alpha/Beta Analysis)

- **Maximum return objective**: HYPE (alpha: 275.9% annually, elevated volatility)
- **Defensive positioning**: ETH (beta: 1.427, balanced upside 133% / downside 131% capture)
- **Aggressive positioning**: SOL (beta: 1.578, amplifies both upside 150% and downside 160%)

**Risk Consideration**: SOL provides 160% downside capture, making it unsuitable for defensive portfolios despite higher upside potential.

---

## Project Structure

```
2_crypto_market_analysis/
├── README.md                    # This file (navigation hub)
├── reports/                     # Detailed analysis reports
│   ├── CAPITAL_ROTATION_EXIT_SIGNALS.md
│   ├── BTC_CAPITAL_FLOW_SUMMARY.md
│   ├── ALPHA_BETA_REPORT.md
│   ├── CRYPTO_CORRELATION_3YEAR.md
│   └── images/                  # Report visualizations
├── dashboards/                  # Interactive HTML dashboards
│   ├── capital_rotation_exit_signals_dashboard.html
│   ├── btc_capital_flow_1year_dashboard.html
│   ├── alpha_beta_dashboard.html
│   └── crypto_correlation_dashboard.html
├── scripts/                     # Python analysis scripts
│   ├── capital_rotation_exit_signals.py
│   ├── btc_lag_correlation_1year.py
│   ├── alpha_beta_analysis.py
│   └── crypto_correlation_analysis.py
├── data/                        # Data files
│   ├── raw/                     # Raw price data from Yahoo Finance
│   └── processed/               # Analysis results and metrics
└── requirements.txt             # Python dependencies
```

---

## Installation and Setup

### Using UV (Recommended)

```bash
cd 2_crypto_market_analysis
uv pip install -r requirements.txt
```

### Using pip

```bash
cd 2_crypto_market_analysis
pip install -r requirements.txt
```

---

## Running Analyses

### Capital Rotation Exit Signals (Live Trading Signals)

```bash
python scripts/capital_rotation_exit_signals.py
```

### BTC Capital Flow Analysis (Entry Timing)

```bash
python scripts/btc_lag_correlation_1year.py
```

### Alpha/Beta Risk Assessment

```bash
python scripts/alpha_beta_analysis.py
```

### 3-Year Correlation Analysis (Long-term Performance)

```bash
python scripts/crypto_correlation_analysis.py
```

---

## Key Metrics Explained

### Correlation

- **Range**: -1 to +1
- **Interpretation**: +1 indicates perfect positive correlation, 0 indicates independence, -1 indicates perfect negative correlation
- **Example**: ETH-SOL correlation of 76% indicates assets move together 76% of the time
- **Trading implication**: High correlation (>70%) suggests limited diversification benefit

### Beta (Market Sensitivity)

- **Beta > 1**: More volatile than BTC (amplifies price movements)
- **Beta = 1**: Equal volatility to BTC
- **Beta < 1**: Less volatile than BTC (dampens price movements)
- **Example**: SOL beta of 1.578 means SOL moves 1.58% when BTC moves 1%
- **Trading implication**: Higher beta increases both profit potential and loss risk

### Alpha (Excess Returns)

- **Positive alpha**: Outperforms BTC after adjusting for risk (beta-adjusted excess return)
- **Zero alpha**: Matches BTC risk-adjusted performance
- **Negative alpha**: Underperforms BTC after risk adjustment
- **Example**: HYPE alpha of 275.9% indicates 275.9% annual excess return versus BTC on risk-adjusted basis
- **Trading implication**: Positive alpha suggests skilled management or structural advantage

### Sortino Ratio (Downside Risk-Adjusted Returns)

- **Formula**: (Return - Risk_Free_Rate) / Downside_Deviation
- **Interpretation**: >3 considered excellent, 1-3 considered good, <1 considered poor
- **Example**: SOL Sortino ratio of 16.5 indicates generation of 16.5x the downside risk in excess returns
- **Advantage over Sharpe**: Only penalizes downside volatility, not upside volatility

### Upside/Downside Capture Ratios

- **Upside Capture**: Percentage of BTC gains captured when BTC rises
- **Downside Capture**: Percentage of BTC losses captured when BTC falls
- **Optimal profile**: High upside capture (>100%), low downside capture (<100%)
- **Example**: SOL shows 150% upside capture and 160% downside capture (amplifies movements in both directions, not defensive)
- **Trading implication**: Assets with >100% downside capture increase portfolio risk

### Dominance Metrics (BTC.D, ETH.D, SOL.D)

- **BTC.D**: Bitcoin market cap / Total analyzed market cap × 100%
- **ETH.D**: Ethereum market cap / Total analyzed market cap × 100%
- **SOL.D**: Solana market cap / Total analyzed market cap × 100%
- **Use**: Track capital rotation between major asset classes
- **Trading implication**: Dominance peaks often precede trend reversals

---

## Current Market Status

**As of October 5, 2025:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **BTC.D** | 96.26% | Below average (96.87%), alt-friendly environment |
| **ETH.D** | 3.51% | Stable, no exit signal |
| **SOL.D** | 0.039% | Stable, no exit signal |
| **ETH Exit Signal** | Inactive | Position may be maintained |
| **SOL Exit Signal** | Inactive | Position may be maintained |

**Recommendation**: Current market conditions do not trigger exit signals. Positions may be maintained based on exit signal framework.

---

## Data Sources

### Price Data

- **Source**: Yahoo Finance (yfinance API)
- **Update frequency**: Scripts fetch latest available data on execution
- **Assets analyzed**: BTC-USD, ETH-USD, SOL-USD, HYPE-USD

### Analysis Periods

- **3-year correlation analysis**: October 2022 - October 2025
- **Capital flow analysis**: October 2024 - October 2025 (1-year period)
- **Exit signal analysis**: November 2024 - October 2025 (constrained by HYPE launch date)

### Risk-Free Rate

- **Rate used**: 4% annually (10-year U.S. Treasury yield)
- **Application**: Sharpe ratio and Sortino ratio calculations

---

## Research Limitations

### Data Limitations

1. **Limited HYPE data**: Only 11 months of price data available (launched November 2024)
2. **Exit signal analysis period**: Constrained to 310 days by HYPE launch date
3. **Sample size**: Statistical significance affected by limited observation periods for newer assets

### Methodology Limitations

1. **Market efficiency**: High correlation (77% same-day) suggests limited arbitrage opportunities and efficient price discovery
2. **Fast capital flows**: Same-day capital rotation reduces exploitable timing advantages
3. **Simplified dominance calculation**: Analysis includes only BTC, ETH, SOL, HYPE; excludes broader cryptocurrency market
4. **Real-world dominance**: Actual BTC dominance includes entire cryptocurrency market cap (thousands of assets)

### Market Dynamics

1. **Changing correlations**: Cryptocurrency market relationships evolve over time
2. **Regulatory impact**: New regulations (ETF approvals, restrictions) may alter capital flow patterns
3. **Technological changes**: Network upgrades, scaling solutions may affect relative performance
4. **Macroeconomic conditions**: Interest rate changes, risk-on/risk-off cycles influence correlations

---

## Disclaimer

This analysis is for educational and informational purposes only and does not constitute financial advice, investment advice, trading advice, or any other type of professional advice.

**Important Considerations**:
- Past performance does not guarantee future results
- Cryptocurrency markets exhibit extreme volatility and substantial risk
- Conduct independent research before making investment decisions
- Only invest capital you can afford to lose entirely
- Individual risk tolerance and investment objectives vary significantly
- Consult with qualified financial advisors before making investment decisions
- Market conditions change rapidly and historical patterns may not persist
- Regulatory changes may materially impact cryptocurrency markets

---

## Technical Stack

### Programming Language

Python 3.8+

### Data Acquisition

- yfinance library for Yahoo Finance API access
- Real-time price data retrieval

### Analysis Methods

- Linear regression for alpha/beta calculations
- Pearson correlation for asset relationships
- Peak detection algorithms (scipy.signal)
- Rolling window calculations for technical indicators
- Statistical analysis (pandas, numpy, scipy)

### Visualization

- Plotly for interactive dashboards
- HTML export for standalone visualizations

### Core Libraries

- pandas: Data manipulation and time series analysis
- numpy: Numerical computing and array operations
- scipy: Statistical calculations and optimization
- yfinance: Market data retrieval
- plotly: Interactive visualization

---

## Contributing

To add new analyses to this research framework:

1. Create analysis script in `scripts/` directory
2. Store raw data in `data/raw/` directory
3. Save processed results in `data/processed/` directory
4. Generate comprehensive report in `reports/` directory
5. Create interactive dashboard in `dashboards/` directory
6. Update this README with links to new analysis
7. Document methodology and limitations

---

## License

MIT License - Open source and free to use, modify, and distribute

---

## Repository Information

**Data Source**: Yahoo Finance (real-time market data via yfinance API)

**Analysis Period**: October 2022 - October 2025 (3 years for correlation analysis)

**Assets Analyzed**: BTC, ETH, SOL, HYPE

**Analytical Frameworks**: 4 (capital rotation exit, capital flow entry, alpha/beta risk, correlation)

**Libraries**: Python, yfinance, pandas, numpy, scipy, plotly

**Last Updated**: October 5, 2025
