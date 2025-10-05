"""
BTC Capital Flow Analysis (1 Year) - Focused Study
Research Question: After BTC Dominance peaks, where does capital flow?

Tests:
1. BTC <> ETH/SOL correlation (no delay)
2. BTC <> ETH/SOL correlation with 2-week, 1-month, 2-month delays

Timeframe: 1 year (most recent data)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def fetch_1year_data():
    """Fetch last 1 year of BTC, ETH, SOL data from Yahoo Finance (LIVE DATA)"""

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    tickers = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'SOL': 'SOL-USD',
        'HYPE': 'HYPE32196-USD'  # Hyperliquid (launched Nov 2024)
    }

    data = {}

    print("="*70)
    print("FETCHING LIVE DATA (1 YEAR) FROM YAHOO FINANCE")
    print(f"Period: {start_str} to {end_str}")
    print("="*70 + "\n")

    for symbol, ticker in tickers.items():
        print(f"Fetching {ticker}...")
        try:
            df = yf.download(ticker, start=start_str, end=end_str, progress=False, auto_adjust=False)

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if len(df) > 0:
                data[symbol] = df['Close']
                print(f"✓ {symbol}: {len(df)} days | ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
            else:
                print(f"✗ No data for {ticker}")

        except Exception as e:
            print(f"✗ Error: {e}")

    # Combine into DataFrame
    combined = pd.DataFrame(data)
    combined = combined.ffill().dropna(how='all')

    print(f"\n{'='*70}")
    print(f"✓ LIVE DATA LOADED: {len(combined)} days")
    print(f"  Date range: {combined.index[0].date()} to {combined.index[-1].date()}")
    print(f"  Columns: {list(combined.columns)}")
    print(f"{'='*70}\n")

    # Save raw data
    combined.to_csv('btc_eth_sol_1year_raw.csv')
    print("✓ Saved: btc_eth_sol_1year_raw.csv\n")

    return combined


def calculate_simple_correlation(data):
    """
    TEST 1: Simple BTC <> ETH/SOL/HYPE correlation (no delay)
    """

    print("="*70)
    print("TEST 1: BTC <> ETH/SOL/HYPE CORRELATION (NO DELAY)")
    print("="*70 + "\n")

    # Daily returns
    returns = data.pct_change().dropna()

    # Correlations
    btc_eth_corr = returns['BTC'].corr(returns['ETH'])
    btc_sol_corr = returns['BTC'].corr(returns['SOL'])
    btc_hype_corr = returns['BTC'].corr(returns['HYPE']) if 'HYPE' in returns.columns else np.nan
    eth_sol_corr = returns['ETH'].corr(returns['SOL'])

    print("Correlation Matrix (Daily Returns):")
    print(returns.corr())
    print("\nKey Correlations:")
    print(f"  BTC <> ETH: {btc_eth_corr:.4f}")
    print(f"  BTC <> SOL: {btc_sol_corr:.4f}")
    if not np.isnan(btc_hype_corr):
        print(f"  BTC <> HYPE: {btc_hype_corr:.4f}")
    print(f"  ETH <> SOL: {eth_sol_corr:.4f}")
    print()

    # Interpretation
    print("Interpretation:")
    print(f"  - BTC-ETH move together {btc_eth_corr*100:.1f}% of the time")
    print(f"  - BTC-SOL move together {btc_sol_corr*100:.1f}% of the time")
    if not np.isnan(btc_hype_corr):
        print(f"  - BTC-HYPE move together {btc_hype_corr*100:.1f}% of the time")
    print(f"  - ETH-SOL move together {eth_sol_corr*100:.1f}% of the time")
    print()

    return {
        'BTC_ETH': btc_eth_corr,
        'BTC_SOL': btc_sol_corr,
        'BTC_HYPE': btc_hype_corr,
        'ETH_SOL': eth_sol_corr
    }


def calculate_lagged_correlations(data, lags=[14, 30, 60]):
    """
    TEST 2: BTC <> ETH/SOL correlation with time delays

    lags: List of lag periods in days
          [14, 30, 60] = [2 weeks, 1 month, 2 months]

    Returns:
        DataFrame with correlations at each lag
    """

    print("="*70)
    print("TEST 2: BTC <> ETH/SOL/HYPE CORRELATION WITH TIME DELAYS")
    print("Lags: 2 weeks (14d), 1 month (30d), 2 months (60d)")
    print("="*70 + "\n")

    # Daily returns
    returns = data.pct_change().dropna()

    results = []

    for lag in lags:
        # BTC leads (BTC movement → wait lag days → check ETH/SOL/HYPE)
        btc_lead_eth = returns['BTC'].corr(returns['ETH'].shift(-lag))
        btc_lead_sol = returns['BTC'].corr(returns['SOL'].shift(-lag))
        btc_lead_hype = returns['BTC'].corr(returns['HYPE'].shift(-lag)) if 'HYPE' in returns.columns else np.nan

        # ETH/SOL/HYPE lead (movement → wait lag days → check BTC)
        eth_lead_btc = returns['ETH'].shift(lag).corr(returns['BTC'])
        sol_lead_btc = returns['SOL'].shift(lag).corr(returns['BTC'])
        hype_lead_btc = returns['HYPE'].shift(lag).corr(returns['BTC']) if 'HYPE' in returns.columns else np.nan

        result = {
            'Lag (days)': lag,
            'Lag (weeks)': lag / 7,
            'Lag (months)': lag / 30,
            'BTC → ETH (BTC leads)': btc_lead_eth,
            'ETH → BTC (ETH leads)': eth_lead_btc,
            'BTC → SOL (BTC leads)': btc_lead_sol,
            'SOL → BTC (SOL leads)': sol_lead_btc,
        }

        if not np.isnan(btc_lead_hype):
            result['BTC → HYPE (BTC leads)'] = btc_lead_hype
            result['HYPE → BTC (HYPE leads)'] = hype_lead_btc

        results.append(result)

    results_df = pd.DataFrame(results)

    print("Lagged Correlation Results:")
    print(results_df.to_string(index=False))
    print()

    # Save results
    results_df.to_csv('lagged_correlation_results.csv', index=False)
    print("✓ Saved: lagged_correlation_results.csv\n")

    # Interpretation
    print("="*70)
    print("INTERPRETATION")
    print("="*70 + "\n")

    for _, row in results_df.iterrows():
        lag_days = int(row['Lag (days)'])
        print(f"{'─'*70}")
        print(f"After {lag_days} days ({row['Lag (weeks)']:.1f} weeks / {row['Lag (months)']:.1f} months):")
        print(f"{'─'*70}")

        btc_eth_lead = row['BTC → ETH (BTC leads)']
        eth_btc_lead = row['ETH → BTC (ETH leads)']
        btc_sol_lead = row['BTC → SOL (BTC leads)']
        sol_btc_lead = row['SOL → BTC (SOL leads)']

        # BTC → ETH
        print(f"\nBTC → ETH:")
        print(f"  Correlation: {btc_eth_lead:.4f}")
        if abs(btc_eth_lead) > 0.5:
            print(f"  → STRONG: BTC movements predict ETH movements {lag_days} days later")
        elif abs(btc_eth_lead) > 0.3:
            print(f"  → MODERATE: BTC has some predictive power for ETH after {lag_days} days")
        else:
            print(f"  → WEAK: BTC movements don't strongly predict ETH after {lag_days} days")

        # ETH → BTC
        print(f"\nETH → BTC:")
        print(f"  Correlation: {eth_btc_lead:.4f}")
        if abs(eth_btc_lead) > 0.5:
            print(f"  → STRONG: ETH movements predict BTC movements {lag_days} days later")
        elif abs(eth_btc_lead) > 0.3:
            print(f"  → MODERATE: ETH has some predictive power for BTC after {lag_days} days")
        else:
            print(f"  → WEAK: ETH movements don't strongly predict BTC after {lag_days} days")

        # BTC → SOL
        print(f"\nBTC → SOL:")
        print(f"  Correlation: {btc_sol_lead:.4f}")
        if abs(btc_sol_lead) > 0.5:
            print(f"  → STRONG: BTC movements predict SOL movements {lag_days} days later")
        elif abs(btc_sol_lead) > 0.3:
            print(f"  → MODERATE: BTC has some predictive power for SOL after {lag_days} days")
        else:
            print(f"  → WEAK: BTC movements don't strongly predict SOL after {lag_days} days")

        # SOL → BTC
        print(f"\nSOL → BTC:")
        print(f"  Correlation: {sol_btc_lead:.4f}")
        if abs(sol_btc_lead) > 0.5:
            print(f"  → STRONG: SOL movements predict BTC movements {lag_days} days later")
        elif abs(sol_btc_lead) > 0.3:
            print(f"  → MODERATE: SOL has some predictive power for BTC after {lag_days} days")
        else:
            print(f"  → WEAK: SOL movements don't strongly predict BTC after {lag_days} days")

        print()

    return results_df


def analyze_btc_dominance_proxy(data):
    """
    Calculate BTC Dominance proxy and analyze capital flow patterns

    BTC.D ≈ BTC / (BTC + ETH + SOL)
    """

    print("="*70)
    print("BTC DOMINANCE ANALYSIS")
    print("="*70 + "\n")

    # Calculate BTC dominance proxy
    total_value = data.sum(axis=1)
    btc_dom = (data['BTC'] / total_value) * 100

    print(f"BTC Dominance Statistics (1 Year):")
    print(f"  Average: {btc_dom.mean():.2f}%")
    print(f"  Max: {btc_dom.max():.2f}% (Date: {btc_dom.idxmax().date()})")
    print(f"  Min: {btc_dom.min():.2f}% (Date: {btc_dom.idxmin().date()})")
    print(f"  Current: {btc_dom.iloc[-1]:.2f}%")
    print()

    # Find periods of declining BTC.D
    btc_dom_change = btc_dom.diff()
    declining_days = (btc_dom_change < 0).sum()
    total_days = len(btc_dom_change)

    print(f"BTC Dominance Trend:")
    print(f"  Declining days: {declining_days}/{total_days} ({declining_days/total_days*100:.1f}%)")
    print(f"  Rising days: {total_days - declining_days}/{total_days} ({(total_days-declining_days)/total_days*100:.1f}%)")
    print()

    # Capital flow when BTC.D drops
    print("Capital Flow Analysis:")
    print("When BTC Dominance DROPS (potential alt season):")

    btc_dom_drops = btc_dom_change < -0.1  # BTC.D drops by >0.1%
    alt_returns = data.pct_change()[btc_dom_drops]

    if len(alt_returns) > 0:
        print(f"  Average BTC return: {alt_returns['BTC'].mean()*100:.3f}%")
        print(f"  Average ETH return: {alt_returns['ETH'].mean()*100:.3f}%")
        print(f"  Average SOL return: {alt_returns['SOL'].mean()*100:.3f}%")
        print()

        # Who performs best?
        avg_returns = {
            'BTC': alt_returns['BTC'].mean(),
            'ETH': alt_returns['ETH'].mean(),
            'SOL': alt_returns['SOL'].mean()
        }
        best_performer = max(avg_returns, key=avg_returns.get)
        print(f"  → Best performer when BTC.D drops: {best_performer}")
    else:
        print("  No significant BTC.D drops in this period")

    print()

    # Save BTC dominance data
    btc_dom_df = pd.DataFrame({
        'Date': btc_dom.index,
        'BTC_Dominance_%': btc_dom.values,
        'BTC_Dom_Change': btc_dom_change.values
    })
    btc_dom_df.to_csv('btc_dominance_1year.csv', index=False)
    print("✓ Saved: btc_dominance_1year.csv\n")

    return btc_dom, btc_dom_change


def create_visualization(data, simple_corr, lagged_corr, btc_dom):
    """Create comprehensive visualization dashboard"""

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Price Movements (1 Year)',
            'BTC Dominance Over Time',
            'BTC vs ETH (Normalized)',
            'BTC vs SOL (Normalized)',
            'Lagged Correlation: BTC → ETH',
            'Lagged Correlation: BTC → SOL'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # 1. Price movements (normalized to 100)
    normalized = (data / data.iloc[0]) * 100
    for coin in data.columns:
        fig.add_trace(
            go.Scatter(x=data.index, y=normalized[coin], name=coin, mode='lines'),
            row=1, col=1
        )

    # 2. BTC Dominance
    fig.add_trace(
        go.Scatter(x=btc_dom.index, y=btc_dom, name='BTC Dominance',
                  mode='lines', line=dict(color='orange', width=2)),
        row=1, col=2
    )

    # 3. BTC vs ETH (normalized)
    btc_norm = (data['BTC'] / data['BTC'].iloc[0]) * 100
    eth_norm = (data['ETH'] / data['ETH'].iloc[0]) * 100

    fig.add_trace(
        go.Scatter(x=data.index, y=btc_norm, name='BTC', mode='lines'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=eth_norm, name='ETH', mode='lines'),
        row=2, col=1
    )

    # 4. BTC vs SOL (normalized)
    sol_norm = (data['SOL'] / data['SOL'].iloc[0]) * 100

    fig.add_trace(
        go.Scatter(x=data.index, y=btc_norm, name='BTC', mode='lines', showlegend=False),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=sol_norm, name='SOL', mode='lines'),
        row=2, col=2
    )

    # 5. Lagged correlation: BTC → ETH
    fig.add_trace(
        go.Bar(x=lagged_corr['Lag (days)'], y=lagged_corr['BTC → ETH (BTC leads)'],
               name='BTC → ETH', marker_color='blue'),
        row=3, col=1
    )

    # 6. Lagged correlation: BTC → SOL
    fig.add_trace(
        go.Bar(x=lagged_corr['Lag (days)'], y=lagged_corr['BTC → SOL (BTC leads)'],
               name='BTC → SOL', marker_color='purple'),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        height=1200,
        width=1600,
        title_text="BTC Capital Flow Analysis (1 Year) - Live Data",
        title_font_size=22,
        showlegend=True
    )

    # Axis labels
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Normalized Price (Base=100)", row=1, col=1)

    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="BTC Dominance (%)", row=1, col=2)

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Normalized Price", row=2, col=1)

    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_yaxes(title_text="Normalized Price", row=2, col=2)

    fig.update_xaxes(title_text="Lag (days)", row=3, col=1)
    fig.update_yaxes(title_text="Correlation", row=3, col=1)

    fig.update_xaxes(title_text="Lag (days)", row=3, col=2)
    fig.update_yaxes(title_text="Correlation", row=3, col=2)

    # Save
    fig.write_html('btc_capital_flow_1year_dashboard.html')
    print("="*70)
    print("✓ Dashboard saved: btc_capital_flow_1year_dashboard.html")
    print("="*70 + "\n")

    return fig


def generate_summary_report(simple_corr, lagged_corr, btc_dom, btc_dom_change):
    """Generate final summary report"""

    print("\n" + "="*70)
    print("FINAL SUMMARY REPORT")
    print("Research: Where does capital flow after BTC Dominance peaks?")
    print("="*70 + "\n")

    print("KEY FINDINGS:\n")

    # 1. Simple correlations
    print("1. IMMEDIATE CORRELATIONS (No Delay):")
    print(f"   BTC <> ETH: {simple_corr['BTC_ETH']:.4f}")
    print(f"   BTC <> SOL: {simple_corr['BTC_SOL']:.4f}")
    print(f"   → BTC and ETH/SOL move together {simple_corr['BTC_ETH']*100:.1f}% of the time\n")

    # 2. Lagged correlations
    print("2. LAGGED CORRELATIONS (BTC leads → capital flows to alts):")

    for _, row in lagged_corr.iterrows():
        lag = int(row['Lag (days)'])
        btc_eth = row['BTC → ETH (BTC leads)']
        btc_sol = row['BTC → SOL (BTC leads)']

        print(f"\n   After {lag} days ({row['Lag (weeks)']:.0f} weeks):")
        print(f"   BTC → ETH: {btc_eth:.4f}")
        print(f"   BTC → SOL: {btc_sol:.4f}")

        if btc_eth > simple_corr['BTC_ETH']:
            print(f"   → ETH correlation INCREASES with {lag}d delay (+{(btc_eth - simple_corr['BTC_ETH'])*100:.1f}%)")
        else:
            print(f"   → ETH correlation DECREASES with {lag}d delay ({(btc_eth - simple_corr['BTC_ETH'])*100:.1f}%)")

        if btc_sol > simple_corr['BTC_SOL']:
            print(f"   → SOL correlation INCREASES with {lag}d delay (+{(btc_sol - simple_corr['BTC_SOL'])*100:.1f}%)")
        else:
            print(f"   → SOL correlation DECREASES with {lag}d delay ({(btc_sol - simple_corr['BTC_SOL'])*100:.1f}%)")

    # 3. Best lag period
    print("\n3. OPTIMAL LAG PERIOD FOR CAPITAL FLOW:")
    best_eth_lag = lagged_corr.loc[lagged_corr['BTC → ETH (BTC leads)'].idxmax()]
    best_sol_lag = lagged_corr.loc[lagged_corr['BTC → SOL (BTC leads)'].idxmax()]

    print(f"\n   Best BTC → ETH lag: {int(best_eth_lag['Lag (days)'])} days")
    print(f"   Correlation: {best_eth_lag['BTC → ETH (BTC leads)']:.4f}")

    print(f"\n   Best BTC → SOL lag: {int(best_sol_lag['Lag (days)'])} days")
    print(f"   Correlation: {best_sol_lag['BTC → SOL (BTC leads)']:.4f}")

    # 4. BTC Dominance insights
    print("\n4. BTC DOMINANCE INSIGHTS:")
    print(f"   Current BTC.D: {btc_dom.iloc[-1]:.2f}%")
    print(f"   1-year average: {btc_dom.mean():.2f}%")

    if btc_dom.iloc[-1] > btc_dom.mean():
        print(f"   → BTC.D is ABOVE average (BTC strength)")
        print(f"   → Potential for capital rotation to alts if BTC.D peaks")
    else:
        print(f"   → BTC.D is BELOW average (Alt strength)")
        print(f"   → Capital may already be flowing to alts")

    # 5. Trading implications
    print("\n5. TRADING IMPLICATIONS:")

    # Check if any lagged correlation is significantly higher
    max_lagged_eth = lagged_corr['BTC → ETH (BTC leads)'].max()
    max_lagged_sol = lagged_corr['BTC → SOL (BTC leads)'].max()

    if max_lagged_eth > simple_corr['BTC_ETH'] + 0.05:
        best_lag = int(lagged_corr.loc[lagged_corr['BTC → ETH (BTC leads)'].idxmax(), 'Lag (days)'])
        print(f"   ✓ ETH shows delayed response to BTC ({best_lag} days)")
        print(f"   → Consider buying ETH {best_lag} days after BTC moves up")
    else:
        print(f"   ✗ ETH moves simultaneously with BTC (no clear lag benefit)")

    if max_lagged_sol > simple_corr['BTC_SOL'] + 0.05:
        best_lag = int(lagged_corr.loc[lagged_corr['BTC → SOL (BTC leads)'].idxmax(), 'Lag (days)'])
        print(f"   ✓ SOL shows delayed response to BTC ({best_lag} days)")
        print(f"   → Consider buying SOL {best_lag} days after BTC moves up")
    else:
        print(f"   ✗ SOL moves simultaneously with BTC (no clear lag benefit)")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE - All results saved to CSV and HTML")
    print("="*70 + "\n")


def main():
    """Main execution"""

    print("\n" + "="*70)
    print("BTC CAPITAL FLOW ANALYSIS (1 YEAR)")
    print("Using LIVE DATA from Yahoo Finance")
    print("="*70 + "\n")

    # 1. Fetch live data (1 year)
    data = fetch_1year_data()

    if data.empty:
        print("✗ No data available")
        return

    # 2. Test 1: Simple correlations
    simple_corr = calculate_simple_correlation(data)

    # 3. Test 2: Lagged correlations (2 weeks, 1 month, 2 months)
    lagged_corr = calculate_lagged_correlations(data, lags=[14, 30, 60])

    # 4. BTC Dominance analysis
    btc_dom, btc_dom_change = analyze_btc_dominance_proxy(data)

    # 5. Create visualization
    create_visualization(data, simple_corr, lagged_corr, btc_dom)

    # 6. Generate summary report
    generate_summary_report(simple_corr, lagged_corr, btc_dom, btc_dom_change)

    print("Output files:")
    print("  1. btc_eth_sol_1year_raw.csv - Raw price data")
    print("  2. lagged_correlation_results.csv - Lagged correlation table")
    print("  3. btc_dominance_1year.csv - BTC dominance time series")
    print("  4. btc_capital_flow_1year_dashboard.html - Interactive dashboard")
    print()


if __name__ == "__main__":
    main()
