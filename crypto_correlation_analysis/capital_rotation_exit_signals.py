"""
Capital Rotation Exit Signal Analysis
======================================
Analyzes when capital rotates OUT of ETH/SOL to smaller caps
Provides exit signals for ETH/SOL positions

Research Question:
"After BTC.D drops and capital flows to ETH/SOL, how long does it stay
before rotating down the risk curve to smaller caps?"

Approach:
1. Track BTC Dominance (BTC.D)
2. Track ETH Dominance (ETH.D) and SOL Dominance (SOL.D)
3. Identify rotation sequence: BTC.D drop → ETH/SOL rally → ETH.D/SOL.D peak → decline
4. Measure time between BTC.D peak and ETH.D/SOL.D peak
5. Generate exit signals when ETH.D/SOL.D start declining
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import find_peaks


def fetch_market_data(start_date, end_date):
    """Fetch BTC, ETH, SOL, and smaller cap altcoins"""

    print("Fetching market data...")

    tickers = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'SOL': 'SOL-USD',
        'HYPE': 'HYPE32196-USD',
        # Add more smaller caps for better dominance calculation
        # 'AVAX': 'AVAX-USD',
        # 'MATIC': 'MATIC-USD',
    }

    ticker_list = list(tickers.values())

    print(f"  Downloading {len(tickers)} assets...")
    data = yf.download(ticker_list, start=start_date, end=end_date, progress=False, auto_adjust=True)

    # Extract Close prices
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data['Close']
        close_data.columns = list(tickers.keys())
    else:
        close_data = data
        close_data.columns = list(tickers.keys())

    close_data = close_data.ffill().dropna()

    print(f"✓ Fetched {len(close_data)} days ({close_data.index[0].date()} to {close_data.index[-1].date()})")

    return close_data


def calculate_dominance_metrics(data):
    """
    Calculate dominance metrics:
    - BTC.D = BTC / Total
    - ETH.D = ETH / Total
    - SOL.D = SOL / Total
    - Others.D = (Total - BTC - ETH - SOL) / Total
    """

    print("\nCalculating dominance metrics...")

    # Total market cap (sum of all assets)
    total_value = data.sum(axis=1)

    # Calculate dominance for each asset
    dominance = pd.DataFrame(index=data.index)

    for col in data.columns:
        dominance[f'{col}.D'] = (data[col] / total_value) * 100

    # Calculate "Others" dominance (smaller caps)
    if len(data.columns) > 3:
        others_value = total_value - data['BTC'] - data['ETH'] - data['SOL']
        dominance['OTHERS.D'] = (others_value / total_value) * 100

    print(f"✓ Calculated dominance for {len(dominance.columns)} metrics")

    return dominance


def detect_dominance_peaks(dominance, column, prominence_pct=1.0):
    """
    Detect peaks in dominance using scipy.signal.find_peaks

    prominence_pct: Minimum prominence in percentage points
    """

    series = dominance[column].values

    # Find peaks with minimum prominence
    peaks, properties = find_peaks(series, prominence=prominence_pct, distance=14)

    peak_dates = dominance.index[peaks]
    peak_values = series[peaks]

    return peak_dates, peak_values, properties


def detect_dominance_troughs(dominance, column, prominence_pct=1.0):
    """Detect troughs (valleys) in dominance"""

    # Invert the series to find troughs as peaks
    inverted_series = -dominance[column].values

    troughs, properties = find_peaks(inverted_series, prominence=prominence_pct, distance=14)

    trough_dates = dominance.index[troughs]
    trough_values = dominance[column].values[troughs]

    return trough_dates, trough_values, properties


def analyze_rotation_sequence(data, dominance):
    """
    Analyze the rotation sequence:
    1. BTC.D peaks
    2. Capital flows to ETH/SOL (prices rally)
    3. ETH.D/SOL.D peak
    4. ETH.D/SOL.D decline (capital rotates to smaller caps)

    Returns: DataFrame with rotation events
    """

    print("\n" + "="*70)
    print("ROTATION SEQUENCE ANALYSIS")
    print("="*70)

    # Detect BTC.D peaks
    btc_peaks, btc_peak_values, _ = detect_dominance_peaks(dominance, 'BTC.D', prominence_pct=0.5)
    print(f"\nDetected {len(btc_peaks)} BTC.D peaks")

    # Detect ETH.D peaks
    eth_peaks, eth_peak_values, _ = detect_dominance_peaks(dominance, 'ETH.D', prominence_pct=0.3)
    print(f"Detected {len(eth_peaks)} ETH.D peaks")

    # Detect SOL.D peaks
    sol_peaks, sol_peak_values, _ = detect_dominance_peaks(dominance, 'SOL.D', prominence_pct=0.2)
    print(f"Detected {len(sol_peaks)} SOL.D peaks")

    # Analyze rotation timing
    rotations = []

    for btc_peak_date in btc_peaks:
        # Find next ETH.D peak after BTC.D peak
        eth_peaks_after = eth_peaks[eth_peaks > btc_peak_date]

        if len(eth_peaks_after) > 0:
            eth_peak_date = eth_peaks_after[0]
            days_to_eth_peak = (eth_peak_date - btc_peak_date).days

            # Get ETH price performance
            eth_price_at_btc_peak = data.loc[btc_peak_date, 'ETH']
            eth_price_at_eth_peak = data.loc[eth_peak_date, 'ETH']
            eth_return = ((eth_price_at_eth_peak / eth_price_at_btc_peak) - 1) * 100

            rotations.append({
                'BTC.D Peak Date': btc_peak_date,
                'BTC.D Peak Value': dominance.loc[btc_peak_date, 'BTC.D'],
                'ETH.D Peak Date': eth_peak_date,
                'ETH.D Peak Value': dominance.loc[eth_peak_date, 'ETH.D'],
                'Days to ETH.D Peak': days_to_eth_peak,
                'ETH Return %': eth_return
            })

    # Same for SOL
    for btc_peak_date in btc_peaks:
        sol_peaks_after = sol_peaks[sol_peaks > btc_peak_date]

        if len(sol_peaks_after) > 0:
            sol_peak_date = sol_peaks_after[0]
            days_to_sol_peak = (sol_peak_date - btc_peak_date).days

            sol_price_at_btc_peak = data.loc[btc_peak_date, 'SOL']
            sol_price_at_sol_peak = data.loc[sol_peak_date, 'SOL']
            sol_return = ((sol_price_at_sol_peak / sol_price_at_btc_peak) - 1) * 100

    rotation_df = pd.DataFrame(rotations)

    if len(rotation_df) > 0:
        print("\n" + "-"*70)
        print("Rotation Timing Summary:")
        print("-"*70)
        print(f"Average days from BTC.D peak to ETH.D peak: {rotation_df['Days to ETH.D Peak'].mean():.1f}")
        print(f"Median days: {rotation_df['Days to ETH.D Peak'].median():.1f}")
        print(f"Min days: {rotation_df['Days to ETH.D Peak'].min():.0f}")
        print(f"Max days: {rotation_df['Days to ETH.D Peak'].max():.0f}")
        print(f"\nAverage ETH return during rotation: {rotation_df['ETH Return %'].mean():.2f}%")

    return rotation_df, btc_peaks, eth_peaks, sol_peaks


def generate_exit_signals(dominance, data):
    """
    Generate exit signals for ETH/SOL positions

    Exit Signal Rules:
    1. ETH.D starts declining (from recent peak)
    2. SOL.D starts declining (from recent peak)
    3. BTC.D starts rising (reversal)
    """

    print("\n" + "="*70)
    print("EXIT SIGNAL GENERATION")
    print("="*70)

    # Calculate rolling changes
    dominance['BTC.D_Change'] = dominance['BTC.D'].diff()
    dominance['ETH.D_Change'] = dominance['ETH.D'].diff()
    dominance['SOL.D_Change'] = dominance['SOL.D'].diff()

    # Calculate 7-day moving average of changes (smooth out noise)
    dominance['BTC.D_MA7_Change'] = dominance['BTC.D'].diff(7)
    dominance['ETH.D_MA7_Change'] = dominance['ETH.D'].diff(7)
    dominance['SOL.D_MA7_Change'] = dominance['SOL.D'].diff(7)

    # Exit signals
    signals = pd.DataFrame(index=dominance.index)

    # Signal 1: ETH.D declining (7-day change negative)
    signals['ETH_Exit_Signal'] = dominance['ETH.D_MA7_Change'] < -0.3

    # Signal 2: SOL.D declining (7-day change negative)
    signals['SOL_Exit_Signal'] = dominance['SOL.D_MA7_Change'] < -0.2

    # Signal 3: BTC.D rising (capital returning to BTC)
    signals['BTC_Rising_Signal'] = dominance['BTC.D_MA7_Change'] > 0.3

    # Combined exit signal (any of the above)
    signals['Exit_ETH'] = signals['ETH_Exit_Signal'] | signals['BTC_Rising_Signal']
    signals['Exit_SOL'] = signals['SOL_Exit_Signal'] | signals['BTC_Rising_Signal']

    # Count signals
    eth_exit_days = signals['Exit_ETH'].sum()
    sol_exit_days = signals['Exit_SOL'].sum()

    print(f"\nETH Exit Signal Days: {eth_exit_days} ({eth_exit_days/len(signals)*100:.1f}% of days)")
    print(f"SOL Exit Signal Days: {sol_exit_days} ({sol_exit_days/len(signals)*100:.1f}% of days)")

    # Most recent signal
    if signals['Exit_ETH'].iloc[-5:].any():
        print("\n⚠️  ETH Exit Signal: ACTIVE (last 5 days)")
    else:
        print("\n✅ ETH Exit Signal: INACTIVE")

    if signals['Exit_SOL'].iloc[-5:].any():
        print("⚠️  SOL Exit Signal: ACTIVE (last 5 days)")
    else:
        print("✅ SOL Exit Signal: INACTIVE")

    return signals


def create_visualization(data, dominance, signals, btc_peaks, eth_peaks, sol_peaks):
    """Create comprehensive visualization of rotation and exit signals"""

    print("\n" + "="*70)
    print("CREATING VISUALIZATION")
    print("="*70)

    fig = make_subplots(
        rows=4, cols=2,
        subplot_titles=(
            'BTC Dominance with Peaks',
            'ETH Dominance with Peaks',
            'SOL Dominance with Peaks',
            'ETH/SOL Price with Exit Signals',
            'Dominance Comparison',
            'ETH.D vs BTC.D (Inverse Relationship)',
            'Exit Signal Timeline',
            'Capital Rotation Flow'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.12
    )

    # 1. BTC.D with peaks
    fig.add_trace(
        go.Scatter(x=dominance.index, y=dominance['BTC.D'],
                   name='BTC.D', line=dict(color='orange')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=btc_peaks, y=dominance.loc[btc_peaks, 'BTC.D'],
                   mode='markers', name='BTC.D Peaks',
                   marker=dict(size=10, color='red', symbol='triangle-down')),
        row=1, col=1
    )

    # 2. ETH.D with peaks
    fig.add_trace(
        go.Scatter(x=dominance.index, y=dominance['ETH.D'],
                   name='ETH.D', line=dict(color='blue')),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=eth_peaks, y=dominance.loc[eth_peaks, 'ETH.D'],
                   mode='markers', name='ETH.D Peaks',
                   marker=dict(size=10, color='green', symbol='triangle-up')),
        row=1, col=2
    )

    # 3. SOL.D with peaks
    fig.add_trace(
        go.Scatter(x=dominance.index, y=dominance['SOL.D'],
                   name='SOL.D', line=dict(color='purple')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=sol_peaks, y=dominance.loc[sol_peaks, 'SOL.D'],
                   mode='markers', name='SOL.D Peaks',
                   marker=dict(size=10, color='green', symbol='triangle-up')),
        row=2, col=1
    )

    # 4. ETH/SOL prices with exit signals
    # Normalize prices for comparison
    eth_norm = (data['ETH'] / data['ETH'].iloc[0]) * 100
    sol_norm = (data['SOL'] / data['SOL'].iloc[0]) * 100

    fig.add_trace(
        go.Scatter(x=data.index, y=eth_norm,
                   name='ETH Price', line=dict(color='blue')),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=sol_norm,
                   name='SOL Price', line=dict(color='purple')),
        row=2, col=2
    )

    # Add exit signal markers
    eth_exit_dates = signals[signals['Exit_ETH']].index
    if len(eth_exit_dates) > 0:
        fig.add_trace(
            go.Scatter(x=eth_exit_dates, y=eth_norm.loc[eth_exit_dates],
                       mode='markers', name='ETH Exit Signal',
                       marker=dict(size=5, color='red', symbol='x')),
            row=2, col=2
        )

    # 5. All dominance comparison
    fig.add_trace(
        go.Scatter(x=dominance.index, y=dominance['BTC.D'],
                   name='BTC.D', line=dict(color='orange')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=dominance.index, y=dominance['ETH.D'],
                   name='ETH.D', line=dict(color='blue')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=dominance.index, y=dominance['SOL.D'],
                   name='SOL.D', line=dict(color='purple')),
        row=3, col=1
    )

    # 6. ETH.D vs BTC.D scatter (inverse relationship)
    fig.add_trace(
        go.Scatter(x=dominance['BTC.D'], y=dominance['ETH.D'],
                   mode='markers', name='ETH.D vs BTC.D',
                   marker=dict(size=3, color=dominance.index.astype('int64'), colorscale='Viridis'),
                   text=dominance.index.strftime('%Y-%m-%d'),
                   hovertemplate='BTC.D: %{x:.2f}%<br>ETH.D: %{y:.2f}%<br>%{text}'),
        row=3, col=2
    )

    # 7. Exit signal timeline
    exit_eth_binary = signals['Exit_ETH'].astype(int)
    exit_sol_binary = signals['Exit_SOL'].astype(int)

    fig.add_trace(
        go.Scatter(x=signals.index, y=exit_eth_binary,
                   name='ETH Exit Signal', fill='tozeroy',
                   line=dict(color='blue')),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=signals.index, y=exit_sol_binary,
                   name='SOL Exit Signal', fill='tozeroy',
                   line=dict(color='purple')),
        row=4, col=1
    )

    # 8. Capital rotation flow (stacked area)
    if 'OTHERS.D' in dominance.columns:
        fig.add_trace(
            go.Scatter(x=dominance.index, y=dominance['BTC.D'],
                       name='BTC', fill='tonexty', stackgroup='one'),
            row=4, col=2
        )
        fig.add_trace(
            go.Scatter(x=dominance.index, y=dominance['ETH.D'],
                       name='ETH', fill='tonexty', stackgroup='one'),
            row=4, col=2
        )
        fig.add_trace(
            go.Scatter(x=dominance.index, y=dominance['SOL.D'],
                       name='SOL', fill='tonexty', stackgroup='one'),
            row=4, col=2
        )
        fig.add_trace(
            go.Scatter(x=dominance.index, y=dominance['OTHERS.D'],
                       name='Others', fill='tonexty', stackgroup='one'),
            row=4, col=2
        )

    # Update layout
    fig.update_layout(
        title_text="Capital Rotation & Exit Signal Analysis",
        height=1400,
        showlegend=True,
        hovermode='x unified'
    )

    # Update axes labels
    fig.update_yaxes(title_text="BTC.D (%)", row=1, col=1)
    fig.update_yaxes(title_text="ETH.D (%)", row=1, col=2)
    fig.update_yaxes(title_text="SOL.D (%)", row=2, col=1)
    fig.update_yaxes(title_text="Normalized Price", row=2, col=2)
    fig.update_yaxes(title_text="Dominance (%)", row=3, col=1)
    fig.update_yaxes(title_text="ETH.D (%)", row=3, col=2)
    fig.update_xaxes(title_text="BTC.D (%)", row=3, col=2)
    fig.update_yaxes(title_text="Signal (0/1)", row=4, col=1)
    fig.update_yaxes(title_text="Dominance (%)", row=4, col=2)

    # Save
    fig.write_html('capital_rotation_exit_signals_dashboard.html')
    print("✓ Dashboard saved: capital_rotation_exit_signals_dashboard.html")


def generate_report(data, dominance, signals, rotation_df):
    """Generate comprehensive markdown report"""

    report = []

    report.append("# Capital Rotation Exit Signal Analysis")
    report.append("## When to Exit ETH/SOL: Detecting Rotation to Smaller Caps")
    report.append("")
    report.append("**Analysis Date**: " + datetime.now().strftime("%B %d, %Y"))
    report.append(f"**Period**: {data.index[0].date()} to {data.index[-1].date()}")
    report.append(f"**Total Days**: {len(data)}")
    report.append("")
    report.append("![Capital Rotation Dashboard](capital_rotation_exit_signals_dashboard.png)")
    report.append("")
    report.append("---")
    report.append("")

    # Research question
    report.append("## 🎯 Research Question")
    report.append("")
    report.append("**\"After BTC.D drops and capital flows to ETH/SOL, how long does it stay before rotating to smaller caps?\"**")
    report.append("")
    report.append("This analysis identifies:**exit signals** for ETH/SOL positions by detecting when capital rotates down the risk curve to smaller cap altcoins.")
    report.append("")
    report.append("---")
    report.append("")

    # Key findings
    report.append("## 📊 Key Findings")
    report.append("")

    if len(rotation_df) > 0:
        avg_days = rotation_df['Days to ETH.D Peak'].mean()
        median_days = rotation_df['Days to ETH.D Peak'].median()
        avg_return = rotation_df['ETH Return %'].mean()

        report.append(f"### Rotation Timing")
        report.append("")
        report.append(f"- **Average time from BTC.D peak to ETH.D peak**: {avg_days:.1f} days")
        report.append(f"- **Median time**: {median_days:.1f} days")
        report.append(f"- **Average ETH return during rotation**: {avg_return:.2f}%")
        report.append("")
        report.append("### Interpretation:")
        report.append("")
        report.append(f"> After BTC dominance peaks, it takes approximately **{median_days:.0f} days** for ETH dominance to peak.")
        report.append("> ")
        report.append("> **Exit signal**: When ETH.D starts declining from its peak, capital is rotating to smaller caps.")
        report.append("")

    # Current status
    report.append("---")
    report.append("")
    report.append("## 🚨 Current Status")
    report.append("")

    btc_d_current = dominance['BTC.D'].iloc[-1]
    eth_d_current = dominance['ETH.D'].iloc[-1]
    sol_d_current = dominance['SOL.D'].iloc[-1]

    btc_d_change_7d = dominance['BTC.D_MA7_Change'].iloc[-1]
    eth_d_change_7d = dominance['ETH.D_MA7_Change'].iloc[-1]
    sol_d_change_7d = dominance['SOL.D_MA7_Change'].iloc[-1]

    report.append(f"**Current Dominance** (as of {data.index[-1].date()}):")
    report.append("")
    report.append(f"- **BTC.D**: {btc_d_current:.2f}% ({btc_d_change_7d:+.2f}% last 7 days)")
    report.append(f"- **ETH.D**: {eth_d_current:.2f}% ({eth_d_change_7d:+.2f}% last 7 days)")
    report.append(f"- **SOL.D**: {sol_d_current:.2f}% ({sol_d_change_7d:+.2f}% last 7 days)")
    report.append("")

    # Exit signals
    eth_exit_active = signals['Exit_ETH'].iloc[-5:].any()
    sol_exit_active = signals['Exit_SOL'].iloc[-5:].any()

    report.append("**Exit Signals:**")
    report.append("")

    if eth_exit_active:
        report.append("- ⚠️ **ETH Exit Signal: ACTIVE**")
        report.append("  - ETH.D is declining or BTC.D is rising")
        report.append("  - Capital may be rotating to smaller caps or back to BTC")
        report.append("  - **Consider exiting ETH positions**")
    else:
        report.append("- ✅ **ETH Exit Signal: INACTIVE**")
        report.append("  - ETH.D is stable or rising")
        report.append("  - Safe to hold ETH positions")

    report.append("")

    if sol_exit_active:
        report.append("- ⚠️ **SOL Exit Signal: ACTIVE**")
        report.append("  - SOL.D is declining or BTC.D is rising")
        report.append("  - Capital may be rotating to smaller caps or back to BTC")
        report.append("  - **Consider exiting SOL positions**")
    else:
        report.append("- ✅ **SOL Exit Signal: INACTIVE**")
        report.append("  - SOL.D is stable or rising")
        report.append("  - Safe to hold SOL positions")

    report.append("")
    report.append("---")
    report.append("")

    # Methodology
    report.append("## 📐 Methodology")
    report.append("")
    report.append("### Dominance Calculation")
    report.append("")
    report.append("```")
    report.append("BTC.D = BTC / (BTC + ETH + SOL + Others) × 100%")
    report.append("ETH.D = ETH / (BTC + ETH + SOL + Others) × 100%")
    report.append("SOL.D = SOL / (BTC + ETH + SOL + Others) × 100%")
    report.append("```")
    report.append("")
    report.append("### Exit Signal Rules")
    report.append("")
    report.append("**ETH Exit Signal** triggers when:")
    report.append("1. ETH.D declines by >0.3% over 7 days, OR")
    report.append("2. BTC.D rises by >0.3% over 7 days")
    report.append("")
    report.append("**SOL Exit Signal** triggers when:")
    report.append("1. SOL.D declines by >0.2% over 7 days, OR")
    report.append("2. BTC.D rises by >0.3% over 7 days")
    report.append("")
    report.append("### Peak Detection")
    report.append("")
    report.append("- Uses scipy.signal.find_peaks with prominence thresholds")
    report.append("- BTC.D peaks: minimum prominence 0.5%")
    report.append("- ETH.D peaks: minimum prominence 0.3%")
    report.append("- SOL.D peaks: minimum prominence 0.2%")
    report.append("- Minimum distance between peaks: 14 days")
    report.append("")
    report.append("---")
    report.append("")

    # Trading strategy
    report.append("## 💡 Trading Strategy")
    report.append("")
    report.append("### Entry (from BTC Capital Flow Analysis)")
    report.append("")
    report.append("1. **Monitor BTC.D** for peaks and reversals")
    report.append("2. **Buy ETH/SOL immediately** when BTC.D starts declining")
    report.append("3. Capital flows to majors **same-day** (not with 2-week lag)")
    report.append("")
    report.append("### Exit (from this analysis)")
    report.append("")
    report.append("1. **Monitor ETH.D and SOL.D** after entering positions")
    report.append("2. **Exit when ETH.D/SOL.D peak and start declining**")
    report.append("3. Signals capital rotating to smaller caps or back to BTC")
    report.append(f"4. **Typical hold duration**: ~{rotation_df['Days to ETH.D Peak'].median():.0f} days after BTC.D peak" if len(rotation_df) > 0 else "")
    report.append("")
    report.append("### Risk Management")
    report.append("")
    report.append("- **Stop loss**: If BTC.D reverses and starts rising sharply")
    report.append("- **Take profit**: When ETH.D/SOL.D decline for 3+ consecutive days")
    report.append("- **Position sizing**: Reduce exposure as exit signals activate")
    report.append("")
    report.append("---")
    report.append("")

    # Limitations
    report.append("## ⚠️ Limitations")
    report.append("")
    report.append("1. **Simplified dominance**: Only includes BTC, ETH, SOL, HYPE (missing many alts)")
    report.append("2. **Market conditions**: Analysis based on recent market cycle")
    report.append("3. **False signals**: May trigger during short-term volatility")
    report.append("4. **Not financial advice**: Use with other indicators and risk management")
    report.append("")
    report.append("---")
    report.append("")

    # Data files
    report.append("## 📁 Output Files")
    report.append("")
    report.append("1. **CAPITAL_ROTATION_EXIT_SIGNALS.md** - This report")
    report.append("2. **capital_rotation_exit_signals_dashboard.html** - Interactive charts")
    report.append("3. **capital_rotation_exit_signals_dashboard.png** - Dashboard screenshot")
    report.append("4. **dominance_data.csv** - Dominance time series")
    report.append("5. **exit_signals.csv** - Exit signal timeline")
    report.append("6. **rotation_events.csv** - Historical rotation events")
    report.append("")
    report.append("---")
    report.append("")
    report.append("*Analysis by: capital_rotation_exit_signals.py*")
    report.append("*Data source: Yahoo Finance*")
    report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    # Save report
    report_text = '\n'.join(report)
    with open('CAPITAL_ROTATION_EXIT_SIGNALS.md', 'w') as f:
        f.write(report_text)

    print("\n✓ Report saved: CAPITAL_ROTATION_EXIT_SIGNALS.md")

    return report_text


def main():
    """Main execution"""

    print("\n" + "="*70)
    print("CAPITAL ROTATION EXIT SIGNAL ANALYSIS")
    print("="*70)
    print()
    print("Research Question:")
    print("After BTC.D drops and capital flows to ETH/SOL,")
    print("how long does it stay before rotating to smaller caps?")
    print("="*70 + "\n")

    # Fetch data from Jan 2024 to present
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()

    data = fetch_market_data(start_date, end_date)

    # Calculate dominance metrics
    dominance = calculate_dominance_metrics(data)

    # Analyze rotation sequence
    rotation_df, btc_peaks, eth_peaks, sol_peaks = analyze_rotation_sequence(data, dominance)

    # Generate exit signals
    signals = generate_exit_signals(dominance, data)

    # Create visualization
    create_visualization(data, dominance, signals, btc_peaks, eth_peaks, sol_peaks)

    # Generate report
    generate_report(data, dominance, signals, rotation_df)

    # Save data files
    dominance.to_csv('dominance_data.csv')
    signals.to_csv('exit_signals.csv')
    if len(rotation_df) > 0:
        rotation_df.to_csv('rotation_events.csv', index=False)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nOutput files:")
    print("  1. CAPITAL_ROTATION_EXIT_SIGNALS.md - Comprehensive report")
    print("  2. capital_rotation_exit_signals_dashboard.html - Interactive charts")
    print("  3. dominance_data.csv - Dominance time series")
    print("  4. exit_signals.csv - Exit signal timeline")
    if len(rotation_df) > 0:
        print("  5. rotation_events.csv - Historical rotation events")
    print()


if __name__ == "__main__":
    main()
