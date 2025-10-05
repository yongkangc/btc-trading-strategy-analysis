"""
Bitcoin Dominance Capital Flow Analysis
Research Question: After BTC Dominance peaks/declines, where does capital flow?

Analyzes:
1. BTC Dominance (BTC.D) trends over 3 years
2. Capital rotation patterns: BTC → ETH → SOL → HYPE
3. Correlation with time lags (leading/lagging indicators)
4. Alt season detection and performance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def fetch_crypto_data_with_btc(start_date=None, end_date=None):
    """Fetch BTC, ETH, SOL, HYPE and calculate BTC dominance proxy"""

    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=1095)  # 3 years

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    tickers = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'SOL': 'SOL-USD',
        'HYPE': 'HYPE32196-USD'
    }

    data = {}

    print("="*70)
    print("FETCHING CRYPTO DATA FOR DOMINANCE ANALYSIS")
    print("="*70)

    for symbol, ticker in tickers.items():
        print(f"\nFetching {ticker}...")
        try:
            df = yf.download(ticker, start=start_str, end=end_str, progress=False, auto_adjust=False)

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if len(df) > 0:
                # Store both Close and Volume
                data[symbol] = pd.DataFrame({
                    'price': df['Close'],
                    'volume': df['Volume']
                })
                print(f"✓ {symbol}: {len(df)} days | ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
            else:
                print(f"✗ No data for {ticker}")

        except Exception as e:
            print(f"✗ Error fetching {ticker}: {e}")

    if not data:
        print("✗ No data fetched")
        return pd.DataFrame()

    # Combine prices
    combined = pd.DataFrame()
    for symbol, df in data.items():
        combined[symbol] = df['price']

    # Forward fill missing data
    combined = combined.ffill().dropna(how='all')

    print(f"\n{'='*70}")
    print(f"✓ Combined data: {len(combined)} days | {combined.index[0].date()} to {combined.index[-1].date()}")
    print(f"{'='*70}\n")

    return combined


def calculate_btc_dominance_proxy(data):
    """
    Calculate BTC Dominance proxy
    BTC.D ≈ BTC_mcap / (BTC_mcap + ETH_mcap + SOL_mcap + HYPE_mcap)

    Note: Using price as proxy for market cap (assumes constant supply)
    This is a simplified approximation since we don't have real-time supply data
    """

    # Normalize prices to relative market cap proxy
    # BTC dominance = BTC / (BTC + ETH + SOL + HYPE)
    total_value = data.sum(axis=1)
    btc_dominance = (data['BTC'] / total_value) * 100

    print("BTC DOMINANCE PROXY CALCULATED")
    print(f"Average BTC.D: {btc_dominance.mean():.2f}%")
    print(f"Max BTC.D: {btc_dominance.max():.2f}%")
    print(f"Min BTC.D: {btc_dominance.min():.2f}%")

    return btc_dominance


def detect_btc_dominance_peaks(btc_dom, window=30):
    """
    Detect BTC dominance peaks (local maxima) and troughs (local minima)

    Args:
        btc_dom: BTC dominance time series
        window: Rolling window for peak detection (default: 30 days)
    """

    # Rolling max/min
    rolling_max = btc_dom.rolling(window=window, center=True).max()
    rolling_min = btc_dom.rolling(window=window, center=True).min()

    # Peaks: local maxima
    peaks = (btc_dom == rolling_max) & (btc_dom.shift(1) < btc_dom) & (btc_dom.shift(-1) < btc_dom)

    # Troughs: local minima
    troughs = (btc_dom == rolling_min) & (btc_dom.shift(1) > btc_dom) & (btc_dom.shift(-1) > btc_dom)

    print(f"\nBTC DOMINANCE PEAKS/TROUGHS ({window}-day window)")
    print(f"Peaks detected: {peaks.sum()}")
    print(f"Troughs detected: {troughs.sum()}")

    return peaks, troughs


def analyze_capital_flow_after_btc_peak(data, btc_dom, peaks, lookforward_days=60):
    """
    Analyze what happens to ETH, SOL, HYPE after BTC dominance peaks

    Args:
        data: Price data for all assets
        btc_dom: BTC dominance series
        peaks: Boolean series of BTC.D peaks
        lookforward_days: Days to analyze after each peak
    """

    peak_dates = btc_dom[peaks].index

    if len(peak_dates) == 0:
        print("No peaks detected")
        return pd.DataFrame()

    print(f"\n{'='*70}")
    print(f"CAPITAL FLOW ANALYSIS: {lookforward_days} days after BTC.D peaks")
    print(f"{'='*70}")
    print(f"Analyzing {len(peak_dates)} BTC dominance peaks\n")

    results = []

    for peak_date in peak_dates:
        # Get date range after peak
        end_date = peak_date + timedelta(days=lookforward_days)

        # Filter data
        after_peak = data[peak_date:end_date]

        if len(after_peak) < 2:
            continue

        # Calculate returns for each asset
        returns = {}
        for coin in data.columns:
            if coin in after_peak.columns and len(after_peak[coin].dropna()) > 1:
                initial = after_peak[coin].iloc[0]
                final = after_peak[coin].iloc[-1]
                ret = ((final / initial) - 1) * 100
                returns[coin] = ret
            else:
                returns[coin] = np.nan

        # BTC.D change
        btc_dom_change = btc_dom[end_date] - btc_dom[peak_date] if end_date in btc_dom.index else np.nan

        results.append({
            'Peak Date': peak_date.strftime('%Y-%m-%d'),
            'BTC.D at Peak': btc_dom[peak_date],
            'BTC.D Change': btc_dom_change,
            'BTC Return (%)': returns.get('BTC', np.nan),
            'ETH Return (%)': returns.get('ETH', np.nan),
            'SOL Return (%)': returns.get('SOL', np.nan),
            'HYPE Return (%)': returns.get('HYPE', np.nan),
        })

    results_df = pd.DataFrame(results)

    # Calculate averages
    print("AVERAGE PERFORMANCE AFTER BTC.D PEAKS:")
    print(f"BTC.D Change: {results_df['BTC.D Change'].mean():.2f}%")
    print(f"BTC Return: {results_df['BTC Return (%)'].mean():.2f}%")
    print(f"ETH Return: {results_df['ETH Return (%)'].mean():.2f}%")
    print(f"SOL Return: {results_df['SOL Return (%)'].mean():.2f}%")
    print(f"HYPE Return: {results_df['HYPE Return (%)'].mean():.2f}%")

    # Save results
    results_df.to_csv('capital_flow_after_btc_peaks.csv', index=False)
    print(f"\n✓ Saved to capital_flow_after_btc_peaks.csv")

    return results_df


def calculate_lagged_correlation(btc_returns, alt_returns, max_lag=30):
    """
    Calculate correlation between BTC and alts with time lags

    Args:
        btc_returns: BTC daily returns
        alt_returns: Alt coin daily returns (ETH, SOL, HYPE)
        max_lag: Maximum lag days to test

    Returns:
        DataFrame with correlations at different lags
    """

    print(f"\n{'='*70}")
    print(f"LAGGED CORRELATION ANALYSIS (max lag: {max_lag} days)")
    print(f"{'='*70}\n")

    results = {}

    for coin in alt_returns.columns:
        correlations = []

        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                # Alt leads BTC (alt moves first)
                corr = btc_returns.shift(-lag).corr(alt_returns[coin])
            else:
                # BTC leads Alt (BTC moves first)
                corr = btc_returns.corr(alt_returns[coin].shift(lag))

            correlations.append({
                'Lag (days)': lag,
                'Correlation': corr
            })

        results[coin] = pd.DataFrame(correlations)

        # Find optimal lag (highest correlation)
        optimal = results[coin].loc[results[coin]['Correlation'].abs().idxmax()]
        print(f"{coin}:")
        print(f"  Optimal lag: {optimal['Lag (days)']:.0f} days")
        print(f"  Correlation: {optimal['Correlation']:.3f}")

        if optimal['Lag (days)'] < 0:
            print(f"  → {coin} LEADS BTC by {abs(optimal['Lag (days)']):.0f} days")
        elif optimal['Lag (days)'] > 0:
            print(f"  → BTC LEADS {coin} by {optimal['Lag (days)']:.0f} days")
        else:
            print(f"  → {coin} moves SIMULTANEOUSLY with BTC")
        print()

    return results


def identify_alt_seasons(btc_dom, threshold=-5, min_duration=30):
    """
    Identify 'alt seasons' when BTC dominance drops significantly

    Alt Season = Period when BTC.D drops by threshold% over min_duration days

    Args:
        btc_dom: BTC dominance series
        threshold: BTC.D % drop to trigger alt season (default: -5%)
        min_duration: Minimum days for valid alt season
    """

    print(f"\n{'='*70}")
    print(f"ALT SEASON DETECTION (threshold: {threshold}%, min duration: {min_duration} days)")
    print(f"{'='*70}\n")

    # Calculate rolling change
    btc_dom_change = btc_dom - btc_dom.shift(min_duration)

    # Alt season = BTC.D dropped by threshold
    alt_season = btc_dom_change < threshold

    # Find continuous periods
    alt_season_periods = []
    in_alt_season = False
    start_date = None

    for date, is_alt in alt_season.items():
        if is_alt and not in_alt_season:
            # Start of alt season
            start_date = date
            in_alt_season = True
        elif not is_alt and in_alt_season:
            # End of alt season
            if start_date is not None:
                alt_season_periods.append((start_date, date))
            in_alt_season = False

    print(f"Alt Seasons Detected: {len(alt_season_periods)}\n")

    for i, (start, end) in enumerate(alt_season_periods, 1):
        duration = (end - start).days
        btc_dom_drop = btc_dom[end] - btc_dom[start]
        print(f"{i}. {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        print(f"   Duration: {duration} days | BTC.D change: {btc_dom_drop:.2f}%\n")

    return alt_season, alt_season_periods


def analyze_alt_season_performance(data, alt_season_periods):
    """
    Analyze asset performance during alt seasons vs non-alt seasons

    Args:
        data: Price data for all assets
        alt_season_periods: List of (start, end) tuples for alt seasons
    """

    if len(alt_season_periods) == 0:
        print("No alt seasons to analyze")
        return

    print(f"\n{'='*70}")
    print(f"PERFORMANCE DURING ALT SEASONS")
    print(f"{'='*70}\n")

    alt_season_returns = {coin: [] for coin in data.columns}
    non_alt_returns = {coin: [] for coin in data.columns}

    # Calculate returns for each period
    for start, end in alt_season_periods:
        period_data = data[start:end]

        for coin in data.columns:
            if coin in period_data.columns and len(period_data[coin].dropna()) > 1:
                ret = period_data[coin].pct_change().dropna()
                alt_season_returns[coin].extend(ret.values)

    # Calculate non-alt season returns
    all_dates = set(data.index)
    alt_dates = set()
    for start, end in alt_season_periods:
        alt_dates.update(data[start:end].index)

    non_alt_dates = sorted(all_dates - alt_dates)

    for coin in data.columns:
        non_alt_data = data.loc[non_alt_dates, coin]
        ret = non_alt_data.pct_change().dropna()
        non_alt_returns[coin].extend(ret.values)

    # Compare performance
    print("Average Daily Returns:\n")
    print(f"{'Asset':<8} {'Alt Season':<15} {'Non-Alt Season':<15} {'Difference':<15}")
    print("-" * 55)

    for coin in data.columns:
        alt_avg = np.mean(alt_season_returns[coin]) * 100 if alt_season_returns[coin] else np.nan
        non_alt_avg = np.mean(non_alt_returns[coin]) * 100 if non_alt_returns[coin] else np.nan
        diff = alt_avg - non_alt_avg if not np.isnan(alt_avg) and not np.isnan(non_alt_avg) else np.nan

        print(f"{coin:<8} {alt_avg:>13.3f}%  {non_alt_avg:>13.3f}%  {diff:>13.3f}%")

    print()


def create_dominance_dashboard(data, btc_dom, peaks, troughs, alt_season, lagged_corr):
    """Create comprehensive BTC dominance and capital flow dashboard"""

    fig = make_subplots(
        rows=4, cols=2,
        subplot_titles=(
            'BTC Dominance Over Time',
            'Asset Prices (Normalized to 100)',
            'BTC Dominance vs ETH Price',
            'BTC Dominance vs SOL Price',
            'Lagged Correlation: BTC vs ETH',
            'Lagged Correlation: BTC vs SOL',
            'Alt Season Detection',
            'Capital Flow Pattern'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.12
    )

    # 1. BTC Dominance with peaks/troughs
    fig.add_trace(
        go.Scatter(x=btc_dom.index, y=btc_dom, name='BTC Dominance',
                  mode='lines', line=dict(color='orange', width=2)),
        row=1, col=1
    )

    # Mark peaks
    peak_dates = btc_dom[peaks].index
    fig.add_trace(
        go.Scatter(x=peak_dates, y=btc_dom[peaks], name='BTC.D Peaks',
                  mode='markers', marker=dict(color='red', size=10, symbol='triangle-down')),
        row=1, col=1
    )

    # Mark troughs
    trough_dates = btc_dom[troughs].index
    fig.add_trace(
        go.Scatter(x=trough_dates, y=btc_dom[troughs], name='BTC.D Troughs',
                  mode='markers', marker=dict(color='green', size=10, symbol='triangle-up')),
        row=1, col=1
    )

    # 2. Normalized prices
    normalized = (data / data.iloc[0]) * 100
    for coin in data.columns:
        fig.add_trace(
            go.Scatter(x=data.index, y=normalized[coin], name=coin, mode='lines'),
            row=1, col=2
        )

    # 3. BTC.D vs ETH
    fig.add_trace(
        go.Scatter(x=btc_dom.index, y=btc_dom, name='BTC.D',
                  mode='lines', line=dict(color='orange')),
        row=2, col=1
    )
    # Add ETH on secondary axis (need to normalize)
    eth_norm = (data['ETH'] / data['ETH'].max()) * btc_dom.max()
    fig.add_trace(
        go.Scatter(x=data.index, y=eth_norm, name='ETH (scaled)',
                  mode='lines', line=dict(color='blue', dash='dot')),
        row=2, col=1
    )

    # 4. BTC.D vs SOL
    fig.add_trace(
        go.Scatter(x=btc_dom.index, y=btc_dom, name='BTC.D',
                  mode='lines', line=dict(color='orange'), showlegend=False),
        row=2, col=2
    )
    sol_norm = (data['SOL'] / data['SOL'].max()) * btc_dom.max()
    fig.add_trace(
        go.Scatter(x=data.index, y=sol_norm, name='SOL (scaled)',
                  mode='lines', line=dict(color='purple', dash='dot')),
        row=2, col=2
    )

    # 5 & 6. Lagged correlations
    if 'ETH' in lagged_corr:
        eth_lag = lagged_corr['ETH']
        fig.add_trace(
            go.Scatter(x=eth_lag['Lag (days)'], y=eth_lag['Correlation'],
                      name='BTC-ETH Correlation', mode='lines+markers'),
            row=3, col=1
        )

    if 'SOL' in lagged_corr:
        sol_lag = lagged_corr['SOL']
        fig.add_trace(
            go.Scatter(x=sol_lag['Lag (days)'], y=sol_lag['Correlation'],
                      name='BTC-SOL Correlation', mode='lines+markers'),
            row=3, col=2
        )

    # 7. Alt season indicator
    alt_season_binary = alt_season.astype(int)
    fig.add_trace(
        go.Scatter(x=alt_season.index, y=alt_season_binary,
                  name='Alt Season', mode='lines', fill='tozeroy',
                  line=dict(color='green')),
        row=4, col=1
    )

    # 8. Capital flow pattern (average returns after BTC.D peaks)
    # This would require the results from capital flow analysis
    # Placeholder for now
    fig.add_trace(
        go.Bar(x=['BTC', 'ETH', 'SOL', 'HYPE'], y=[0, 0, 0, 0],
               name='Avg Return After BTC.D Peak', marker_color='lightblue'),
        row=4, col=2
    )

    # Update layout
    fig.update_layout(
        height=1600,
        width=1600,
        title_text="Bitcoin Dominance & Capital Flow Analysis",
        title_font_size=22,
        showlegend=True,
        hovermode='x unified'
    )

    # Axis labels
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="BTC Dominance (%)", row=1, col=1)

    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="Price (Normalized)", row=1, col=2)

    fig.update_xaxes(title_text="Lag (days)", row=3, col=1)
    fig.update_yaxes(title_text="Correlation", row=3, col=1)

    fig.update_xaxes(title_text="Lag (days)", row=3, col=2)
    fig.update_yaxes(title_text="Correlation", row=3, col=2)

    fig.update_xaxes(title_text="Date", row=4, col=1)
    fig.update_yaxes(title_text="Alt Season (1=Yes)", row=4, col=1)

    # Save
    fig.write_html('btc_dominance_dashboard.html')
    print(f"\n{'='*70}")
    print("✓ Dashboard saved: btc_dominance_dashboard.html")
    print(f"{'='*70}\n")

    return fig


def main():
    """Main execution"""

    print("\n" + "="*70)
    print("BITCOIN DOMINANCE CAPITAL FLOW ANALYSIS")
    print("Research: Where does capital flow after BTC.D peaks?")
    print("="*70 + "\n")

    # 1. Fetch data
    data = fetch_crypto_data_with_btc()

    if data.empty:
        print("✗ No data available")
        return

    # 2. Calculate BTC dominance proxy
    btc_dom = calculate_btc_dominance_proxy(data)
    btc_dom.to_csv('btc_dominance.csv')

    # 3. Detect peaks and troughs
    peaks, troughs = detect_btc_dominance_peaks(btc_dom, window=30)

    # 4. Analyze capital flow after peaks
    capital_flow_results = analyze_capital_flow_after_btc_peak(data, btc_dom, peaks, lookforward_days=60)

    # 5. Lagged correlation analysis
    daily_returns = data.pct_change().dropna()
    btc_returns = daily_returns['BTC']
    alt_returns = daily_returns[['ETH', 'SOL', 'HYPE']]

    lagged_corr = calculate_lagged_correlation(btc_returns, alt_returns, max_lag=30)

    # 6. Identify alt seasons
    alt_season, alt_season_periods = identify_alt_seasons(btc_dom, threshold=-5, min_duration=30)

    # 7. Analyze alt season performance
    analyze_alt_season_performance(data, alt_season_periods)

    # 8. Create dashboard
    create_dominance_dashboard(data, btc_dom, peaks, troughs, alt_season, lagged_corr)

    # Final summary
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print("\nKey Outputs:")
    print("  1. btc_dominance.csv - BTC dominance time series")
    print("  2. capital_flow_after_btc_peaks.csv - Performance after BTC.D peaks")
    print("  3. btc_dominance_dashboard.html - Interactive dashboard")
    print("\nKey Findings:")
    print("  - Check dashboard for visual capital flow patterns")
    print("  - Review lagged correlations to identify lead/lag relationships")
    print("  - Analyze alt season performance for trading opportunities")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
