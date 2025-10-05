"""
Alpha/Beta Analysis: ETH, SOL, HYPE vs BTC
Calculates alpha (excess returns) and beta (market sensitivity)
BTC treated as the "market" benchmark
"""

import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime


def calculate_alpha_beta(market_returns, asset_returns, risk_free_rate=0.04):
    """
    Calculate alpha and beta using linear regression

    Beta: Sensitivity to market (BTC) movements
    Alpha: Excess return beyond what beta predicts (annualized)

    Model: Asset_Return = Alpha + Beta * Market_Return + Error
    """

    # Daily risk-free rate
    daily_rf = (1 + risk_free_rate) ** (1/365) - 1

    # Excess returns (returns - risk-free rate)
    market_excess = market_returns - daily_rf
    asset_excess = asset_returns - daily_rf

    # Remove NaN values
    mask = ~(market_excess.isna() | asset_excess.isna())
    market_clean = market_excess[mask]
    asset_clean = asset_excess[mask]

    if len(market_clean) < 2:
        return None, None, None, None, None

    # Linear regression: y = alpha + beta * x
    slope, intercept, r_value, p_value, std_err = stats.linregress(market_clean, asset_clean)

    beta = slope
    alpha_daily = intercept
    alpha_annual = alpha_daily * 365 * 100  # Annualized as percentage
    r_squared = r_value ** 2

    return beta, alpha_annual, r_squared, p_value, std_err


def calculate_upside_downside_capture(market_returns, asset_returns):
    """
    Calculate upside and downside capture ratios

    Upside Capture: (Asset return when market up) / (Market return when market up) * 100
    Downside Capture: (Asset return when market down) / (Market return when market down) * 100

    Ideal defensive asset: Low downside capture, High upside capture
    """

    # Remove NaN values
    mask = ~(market_returns.isna() | asset_returns.isna())
    market_clean = market_returns[mask]
    asset_clean = asset_returns[mask]

    # Split into up days and down days
    up_days = market_clean > 0
    down_days = market_clean < 0

    # Calculate average returns on up/down days
    market_up_avg = market_clean[up_days].mean()
    asset_up_avg = asset_clean[up_days].mean()

    market_down_avg = market_clean[down_days].mean()
    asset_down_avg = asset_clean[down_days].mean()

    # Calculate capture ratios
    upside_capture = (asset_up_avg / market_up_avg * 100) if market_up_avg != 0 else 0
    downside_capture = (asset_down_avg / market_down_avg * 100) if market_down_avg != 0 else 0

    up_day_count = up_days.sum()
    down_day_count = down_days.sum()

    return upside_capture, downside_capture, up_day_count, down_day_count


def analyze_price_movements(data):
    """Analyze how prices move relative to each other"""

    print("="*70)
    print("PRICE MOVEMENT ANALYSIS")
    print("="*70)

    # Calculate daily returns
    returns = data.pct_change().dropna()

    # Summary statistics
    print("\nDaily Return Statistics:")
    print("-"*70)
    print(f"{'Asset':<10} {'Mean %':<12} {'Std %':<12} {'Min %':<12} {'Max %':<12}")
    print("-"*70)

    for col in data.columns:
        mean_ret = returns[col].mean() * 100
        std_ret = returns[col].std() * 100
        min_ret = returns[col].min() * 100
        max_ret = returns[col].max() * 100
        print(f"{col:<10} {mean_ret:>11.3f} {std_ret:>11.3f} {min_ret:>11.2f} {max_ret:>11.2f}")

    # Up/Down day analysis
    print("\n\nUp/Down Day Analysis:")
    print("-"*70)
    print(f"{'Asset':<10} {'Up Days':<12} {'Down Days':<12} {'Win Rate %':<12}")
    print("-"*70)

    for col in data.columns:
        up_days = (returns[col] > 0).sum()
        down_days = (returns[col] < 0).sum()
        win_rate = up_days / (up_days + down_days) * 100
        print(f"{col:<10} {up_days:<12} {down_days:<12} {win_rate:>11.1f}")

    return returns


def calculate_all_alpha_beta(data, risk_free_rate=0.04):
    """Calculate alpha and beta for all assets vs BTC"""

    print("\n" + "="*70)
    print("ALPHA/BETA ANALYSIS (vs BTC as Market)")
    print("="*70)

    returns = data.pct_change().dropna()
    btc_returns = returns['BTC']

    results = []

    for asset in ['ETH', 'SOL', 'HYPE']:
        if asset not in returns.columns:
            continue

        asset_returns = returns[asset]
        beta, alpha, r_squared, p_value, std_err = calculate_alpha_beta(
            btc_returns, asset_returns, risk_free_rate
        )

        # Calculate upside/downside capture
        upside, downside, up_days, down_days = calculate_upside_downside_capture(
            btc_returns, asset_returns
        )

        if beta is not None:
            results.append({
                'Asset': asset,
                'Beta': beta,
                'Alpha (% annual)': alpha,
                'R-squared': r_squared,
                'P-value': p_value,
                'Upside Capture %': upside,
                'Downside Capture %': downside,
                'BTC Up Days': up_days,
                'BTC Down Days': down_days
            })

    results_df = pd.DataFrame(results)

    # Print results
    print("\nRegression Results:")
    print("-"*70)
    print(f"{'Asset':<10} {'Beta':<10} {'Alpha %':<15} {'R²':<10} {'P-value':<10}")
    print("-"*70)

    for _, row in results_df.iterrows():
        print(f"{row['Asset']:<10} {row['Beta']:>9.3f} {row['Alpha (% annual)']:>14.2f} "
              f"{row['R-squared']:>9.3f} {row['P-value']:>9.4f}")

    # Interpretation
    print("\n\nBeta Interpretation:")
    print("-"*70)
    for _, row in results_df.iterrows():
        asset = row['Asset']
        beta = row['Beta']

        if beta > 1.2:
            volatility = "HIGH volatility (amplifies BTC moves)"
        elif beta > 0.8:
            volatility = "SIMILAR volatility to BTC"
        else:
            volatility = "LOW volatility (dampens BTC moves)"

        print(f"{asset}: Beta = {beta:.3f}")
        print(f"  → {volatility}")
        print(f"  → When BTC moves 1%, {asset} moves ~{beta:.2f}%")
        print()

    print("\nAlpha Interpretation:")
    print("-"*70)
    for _, row in results_df.iterrows():
        asset = row['Asset']
        alpha = row['Alpha (% annual)']

        if alpha > 5:
            performance = "OUTPERFORMS BTC (positive alpha)"
        elif alpha < -5:
            performance = "UNDERPERFORMS BTC (negative alpha)"
        else:
            performance = "MATCHES BTC performance"

        print(f"{asset}: Alpha = {alpha:.2f}% annually")
        print(f"  → {performance}")
        if alpha > 0:
            print(f"  → Generates {alpha:.1f}% extra return beyond what beta predicts")
        else:
            print(f"  → Underperforms by {abs(alpha):.1f}% vs beta prediction")
        print()

    # Upside/Downside Capture Analysis
    print("\nUpside/Downside Capture Ratios:")
    print("-"*70)
    print(f"{'Asset':<10} {'Upside %':<12} {'Downside %':<14} {'Interpretation'}")
    print("-"*70)

    for _, row in results_df.iterrows():
        asset = row['Asset']
        upside = row['Upside Capture %']
        downside = row['Downside Capture %']

        # Determine if defensive or aggressive
        if upside > 100 and downside < 100:
            interpretation = "Ideal (captures more upside, less downside)"
        elif upside > 100 and downside > 100:
            interpretation = "Aggressive (amplifies both up and down)"
        elif upside < 100 and downside < 100:
            interpretation = "Conservative (dampens both up and down)"
        else:
            interpretation = "Poor (captures less upside, more downside)"

        print(f"{asset:<10} {upside:>10.1f}% {downside:>12.1f}% {interpretation}")

    print("\nDetailed Capture Analysis:")
    print("-"*70)
    for _, row in results_df.iterrows():
        asset = row['Asset']
        upside = row['Upside Capture %']
        downside = row['Downside Capture %']

        print(f"\n{asset}:")
        print(f"  → Upside Capture: {upside:.1f}%")
        if upside > 100:
            print(f"    • Goes UP {upside-100:.1f}% MORE than BTC on up days")
        else:
            print(f"    • Goes UP {100-upside:.1f}% LESS than BTC on up days")

        print(f"  → Downside Capture: {downside:.1f}%")
        if downside > 100:
            print(f"    • Goes DOWN {downside-100:.1f}% MORE than BTC on down days")
        else:
            print(f"    • Goes DOWN {100-downside:.1f}% LESS than BTC on down days")

    # Save results
    results_df.to_csv('alpha_beta_results.csv', index=False)
    print(f"\n✓ Saved results to alpha_beta_results.csv")

    return results_df, returns


def analyze_directional_movement(data):
    """Analyze when assets move in same/opposite direction as BTC"""

    print("\n" + "="*70)
    print("DIRECTIONAL MOVEMENT ANALYSIS")
    print("="*70)

    returns = data.pct_change().dropna()
    btc_direction = np.sign(returns['BTC'])

    print("\nMovement Alignment with BTC:")
    print("-"*70)
    print(f"{'Asset':<10} {'Same Dir %':<15} {'Opposite Dir %':<15} {'Days':<10}")
    print("-"*70)

    for asset in ['ETH', 'SOL', 'HYPE']:
        if asset not in returns.columns:
            continue

        asset_direction = np.sign(returns[asset])

        # Count same direction days
        same_dir = (btc_direction == asset_direction).sum()
        opposite_dir = (btc_direction != asset_direction).sum()
        total_days = same_dir + opposite_dir

        same_pct = same_dir / total_days * 100
        opposite_pct = opposite_dir / total_days * 100

        print(f"{asset:<10} {same_pct:>14.1f} {opposite_pct:>14.1f} {total_days:>9}")

    print("\nInterpretation:")
    print("  → Same Dir %: How often asset moves in same direction as BTC")
    print("  → Higher % = More synchronized with BTC movements")


def create_alpha_beta_visualization(data, results_df, returns):
    """Create comprehensive alpha/beta visualization"""

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Beta Comparison (Sensitivity to BTC)',
            'Alpha Comparison (Excess Returns)',
            'ETH vs BTC Scatter (with regression)',
            'SOL vs BTC Scatter (with regression)',
            'Price Movements (Normalized)',
            'Cumulative Returns vs BTC'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # 1. Beta comparison
    fig.add_trace(
        go.Bar(
            x=results_df['Asset'],
            y=results_df['Beta'],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
            text=results_df['Beta'].round(3),
            textposition='outside'
        ),
        row=1, col=1
    )
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray", row=1, col=1,
                  annotation_text="BTC Beta = 1.0")

    # 2. Alpha comparison
    fig.add_trace(
        go.Bar(
            x=results_df['Asset'],
            y=results_df['Alpha (% annual)'],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
            text=results_df['Alpha (% annual)'].round(1),
            textposition='outside'
        ),
        row=1, col=2
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2,
                  annotation_text="Zero Alpha")

    # 3. ETH vs BTC scatter with regression
    btc_returns = returns['BTC'] * 100
    eth_returns = returns['ETH'] * 100

    fig.add_trace(
        go.Scatter(
            x=btc_returns,
            y=eth_returns,
            mode='markers',
            marker=dict(size=3, opacity=0.5),
            name='ETH',
            showlegend=False
        ),
        row=2, col=1
    )

    # Add regression line for ETH
    eth_beta = results_df[results_df['Asset'] == 'ETH']['Beta'].values[0]
    eth_alpha = results_df[results_df['Asset'] == 'ETH']['Alpha (% annual)'].values[0] / 365
    x_range = np.linspace(btc_returns.min(), btc_returns.max(), 100)
    y_pred = eth_alpha + eth_beta * x_range

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode='lines',
            line=dict(color='red', width=2),
            name=f'ETH: α={eth_alpha*365:.1f}%, β={eth_beta:.2f}',
            showlegend=False
        ),
        row=2, col=1
    )

    # 4. SOL vs BTC scatter with regression
    if 'SOL' in returns.columns:
        sol_returns = returns['SOL'] * 100

        fig.add_trace(
            go.Scatter(
                x=btc_returns,
                y=sol_returns,
                mode='markers',
                marker=dict(size=3, opacity=0.5, color='orange'),
                name='SOL',
                showlegend=False
            ),
            row=2, col=2
        )

        # Add regression line for SOL
        sol_beta = results_df[results_df['Asset'] == 'SOL']['Beta'].values[0]
        sol_alpha = results_df[results_df['Asset'] == 'SOL']['Alpha (% annual)'].values[0] / 365
        y_pred_sol = sol_alpha + sol_beta * x_range

        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=y_pred_sol,
                mode='lines',
                line=dict(color='red', width=2),
                name=f'SOL: α={sol_alpha*365:.1f}%, β={sol_beta:.2f}',
                showlegend=False
            ),
            row=2, col=2
        )

    # 5. Normalized prices
    normalized = (data / data.iloc[0]) * 100
    for col in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=normalized[col],
                name=col,
                mode='lines'
            ),
            row=3, col=1
        )

    # 6. Cumulative returns vs BTC
    cumulative = (1 + returns).cumprod() - 1
    for col in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=cumulative[col] * 100,
                name=col,
                mode='lines',
                showlegend=False
            ),
            row=3, col=2
        )

    # Update axes
    fig.update_xaxes(title_text="Asset", row=1, col=1)
    fig.update_yaxes(title_text="Beta", row=1, col=1)

    fig.update_xaxes(title_text="Asset", row=1, col=2)
    fig.update_yaxes(title_text="Alpha (% annual)", row=1, col=2)

    fig.update_xaxes(title_text="BTC Daily Return (%)", row=2, col=1)
    fig.update_yaxes(title_text="ETH Daily Return (%)", row=2, col=1)

    fig.update_xaxes(title_text="BTC Daily Return (%)", row=2, col=2)
    fig.update_yaxes(title_text="SOL Daily Return (%)", row=2, col=2)

    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Normalized Price", row=3, col=1)

    fig.update_xaxes(title_text="Date", row=3, col=2)
    fig.update_yaxes(title_text="Cumulative Return (%)", row=3, col=2)

    # Update layout
    fig.update_layout(
        height=1400,
        width=1600,
        title_text="Alpha/Beta Analysis: ETH, SOL, HYPE vs BTC",
        title_font_size=22,
        showlegend=True,
        hovermode='x unified'
    )

    fig.write_html('alpha_beta_dashboard.html')
    print(f"\n✓ Dashboard saved: alpha_beta_dashboard.html")

    return fig


def generate_report(data, results_df, returns):
    """Generate comprehensive markdown report"""

    report = []
    report.append("# Alpha/Beta Analysis Report")
    report.append("## Price Movement & Risk Analysis: ETH, SOL, HYPE vs BTC")
    report.append("")
    report.append("**Analysis Date**: October 5, 2025")
    report.append(f"**Period**: {data.index[0].date()} to {data.index[-1].date()}")
    report.append(f"**Total Days**: {len(data)}")
    report.append("")
    report.append("---")
    report.append("")

    # Executive Summary
    report.append("## Executive Summary")
    report.append("")

    # Find highest alpha and beta
    max_alpha_row = results_df.loc[results_df['Alpha (% annual)'].idxmax()]
    max_beta_row = results_df.loc[results_df['Beta'].idxmax()]

    report.append(f"**Highest Alpha**: {max_alpha_row['Asset']} ({max_alpha_row['Alpha (% annual)']:.2f}% annually)")
    report.append(f"**Highest Beta**: {max_beta_row['Asset']} ({max_beta_row['Beta']:.3f})")
    report.append("")

    # Alpha/Beta Table
    report.append("## Alpha/Beta Results")
    report.append("")
    report.append("| Asset | Beta | Alpha (% annual) | R² | Interpretation |")
    report.append("|-------|------|------------------|-----|----------------|")

    for _, row in results_df.iterrows():
        asset = row['Asset']
        beta = row['Beta']
        alpha = row['Alpha (% annual)']
        r2 = row['R-squared']

        if beta > 1.2:
            beta_interp = "High volatility"
        elif beta > 0.8:
            beta_interp = "Similar to BTC"
        else:
            beta_interp = "Low volatility"

        if alpha > 5:
            alpha_interp = "Outperforms"
        elif alpha < -5:
            alpha_interp = "Underperforms"
        else:
            alpha_interp = "Matches BTC"

        report.append(f"| {asset} | {beta:.3f} | {alpha:.2f} | {r2:.3f} | {beta_interp}, {alpha_interp} |")

    report.append("")
    report.append("### What is Beta?")
    report.append("")
    report.append("Beta measures an asset's sensitivity to BTC movements:")
    report.append("- **Beta > 1**: More volatile than BTC (amplifies moves)")
    report.append("- **Beta = 1**: Same volatility as BTC")
    report.append("- **Beta < 1**: Less volatile than BTC (dampens moves)")
    report.append("")
    report.append("### What is Alpha?")
    report.append("")
    report.append("Alpha measures excess returns beyond what beta predicts:")
    report.append("- **Positive Alpha**: Outperforms BTC (skill-based returns)")
    report.append("- **Zero Alpha**: Matches BTC performance")
    report.append("- **Negative Alpha**: Underperforms BTC")
    report.append("")

    # Detailed findings for each asset
    report.append("## Detailed Asset Analysis")
    report.append("")

    for _, row in results_df.iterrows():
        asset = row['Asset']
        beta = row['Beta']
        alpha = row['Alpha (% annual)']
        r2 = row['R-squared']

        report.append(f"### {asset}")
        report.append("")
        report.append(f"**Beta**: {beta:.3f}")
        report.append(f"- When BTC moves 1%, {asset} typically moves {beta:.2f}%")

        if beta > 1:
            report.append(f"- **{(beta-1)*100:.0f}% more volatile** than BTC")
        else:
            report.append(f"- **{(1-beta)*100:.0f}% less volatile** than BTC")

        report.append("")
        report.append(f"**Alpha**: {alpha:.2f}% annually")

        if alpha > 0:
            report.append(f"- Generates **{alpha:.1f}% extra return** per year beyond beta prediction")
            report.append(f"- Outperforms BTC by {alpha:.1f}% after adjusting for risk")
        else:
            report.append(f"- Underperforms by **{abs(alpha):.1f}%** per year vs beta prediction")

        report.append("")
        report.append(f"**R-squared**: {r2:.3f}")
        report.append(f"- {r2*100:.1f}% of {asset} price movements explained by BTC")
        report.append(f"- {(1-r2)*100:.1f}% due to asset-specific factors")
        report.append("")

    # Price movement stats
    report.append("## Price Movement Statistics")
    report.append("")
    report.append("| Asset | Avg Daily Return | Volatility | Best Day | Worst Day | Win Rate |")
    report.append("|-------|------------------|------------|----------|-----------|----------|")

    for col in data.columns:
        mean_ret = returns[col].mean() * 100
        std_ret = returns[col].std() * 100
        max_ret = returns[col].max() * 100
        min_ret = returns[col].min() * 100
        win_rate = (returns[col] > 0).sum() / len(returns[col]) * 100

        report.append(f"| {col} | {mean_ret:.3f}% | {std_ret:.2f}% | +{max_ret:.1f}% | {min_ret:.1f}% | {win_rate:.1f}% |")

    report.append("")

    # Directional alignment
    report.append("## Movement Synchronization with BTC")
    report.append("")
    report.append("| Asset | Same Direction | Opposite Direction |")
    report.append("|-------|----------------|-------------------|")

    btc_direction = np.sign(returns['BTC'])
    for asset in ['ETH', 'SOL', 'HYPE']:
        if asset in returns.columns:
            asset_direction = np.sign(returns[asset])
            same_dir = (btc_direction == asset_direction).sum()
            total = len(btc_direction)
            same_pct = same_dir / total * 100
            opposite_pct = 100 - same_pct

            report.append(f"| {asset} | {same_pct:.1f}% | {opposite_pct:.1f}% |")

    report.append("")

    # Upside/Downside Capture
    report.append("## Upside/Downside Capture Analysis")
    report.append("")
    report.append("**Question**: Does the asset \"go down less and go up more\" than BTC?")
    report.append("")
    report.append("| Asset | Upside Capture | Downside Capture | Verdict |")
    report.append("|-------|----------------|------------------|---------|")

    for _, row in results_df.iterrows():
        asset = row['Asset']
        upside = row['Upside Capture %']
        downside = row['Downside Capture %']

        # Determine verdict
        if upside > 100 and downside < 100:
            verdict = "✅ YES (ideal)"
        elif upside > 100 and downside > 100:
            verdict = "❌ NO (amplifies both)"
        elif upside < 100 and downside < 100:
            verdict = "⚠️ PARTIAL (dampens both)"
        else:
            verdict = "❌ NO (worst case)"

        report.append(f"| {asset} | {upside:.1f}% | {downside:.1f}% | {verdict} |")

    report.append("")
    report.append("### Interpretation:")
    report.append("")
    report.append("- **Upside Capture > 100%**: Goes up MORE than BTC on up days")
    report.append("- **Upside Capture < 100%**: Goes up LESS than BTC on up days")
    report.append("- **Downside Capture > 100%**: Goes down MORE than BTC on down days")
    report.append("- **Downside Capture < 100%**: Goes down LESS than BTC on down days")
    report.append("")
    report.append("**Ideal defensive asset**: Upside > 100%, Downside < 100%")
    report.append("")

    # Detailed capture analysis for each asset
    report.append("### Detailed Capture Analysis:")
    report.append("")

    for _, row in results_df.iterrows():
        asset = row['Asset']
        upside = row['Upside Capture %']
        downside = row['Downside Capture %']

        report.append(f"**{asset}**:")
        report.append(f"- Upside Capture: {upside:.1f}%")
        if upside > 100:
            report.append(f"  - Goes UP {upside-100:.1f}% MORE than BTC on up days")
        else:
            report.append(f"  - Goes UP {100-upside:.1f}% LESS than BTC on up days")

        report.append(f"- Downside Capture: {downside:.1f}%")
        if downside > 100:
            report.append(f"  - Goes DOWN {downside-100:.1f}% MORE than BTC on down days ⚠️")
        else:
            report.append(f"  - Goes DOWN {100-downside:.1f}% LESS than BTC on down days ✅")
        report.append("")

    # Special note for SOL
    sol_row = results_df[results_df['Asset'] == 'SOL']
    if not sol_row.empty:
        sol_upside = sol_row.iloc[0]['Upside Capture %']
        sol_downside = sol_row.iloc[0]['Downside Capture %']

        report.append("### Special Analysis: SOL (2024-2025)")
        report.append("")
        report.append(f"**Claim**: \"SOL goes down less and goes up more than BTC\"")
        report.append("")

        if sol_upside > 100 and sol_downside < 100:
            report.append(f"**Verdict**: ✅ TRUE")
            report.append(f"- SOL captures {sol_upside:.1f}% of BTC's upside (up {sol_upside-100:.1f}% more)")
            report.append(f"- SOL captures {sol_downside:.1f}% of BTC's downside (down {100-sol_downside:.1f}% less)")
        elif sol_upside > 100 and sol_downside > 100:
            report.append(f"**Verdict**: ❌ FALSE")
            report.append(f"- SOL goes up {sol_upside-100:.1f}% MORE than BTC ✅")
            report.append(f"- BUT SOL also goes down {sol_downside-100:.1f}% MORE than BTC ❌")
            report.append(f"- SOL amplifies BTC movements in BOTH directions (high beta = {sol_row.iloc[0]['Beta']:.2f})")
        else:
            report.append(f"**Verdict**: ❌ FALSE")
            report.append(f"- SOL's upside capture: {sol_upside:.1f}%")
            report.append(f"- SOL's downside capture: {sol_downside:.1f}%")

        report.append("")

    # Investment implications
    report.append("## Investment Implications")
    report.append("")
    report.append("### Portfolio Construction")
    report.append("")

    # Find best alpha
    best_alpha_asset = results_df.loc[results_df['Alpha (% annual)'].idxmax(), 'Asset']
    best_alpha_value = results_df['Alpha (% annual)'].max()

    report.append(f"**For Maximum Returns**: {best_alpha_asset}")
    report.append(f"- Highest alpha ({best_alpha_value:.2f}% annually)")
    report.append(f"- Generates consistent excess returns beyond market (BTC)")
    report.append("")

    # Find lowest beta
    low_beta_asset = results_df.loc[results_df['Beta'].idxmin(), 'Asset']
    low_beta_value = results_df['Beta'].min()

    report.append(f"**For Risk Management**: {low_beta_asset}")
    report.append(f"- Lowest beta ({low_beta_value:.3f})")
    report.append(f"- Less volatile than BTC, provides downside protection")
    report.append("")

    # Risk/Return tradeoff
    report.append("### Risk/Return Tradeoff")
    report.append("")
    report.append("```")
    for _, row in results_df.iterrows():
        sharpe_proxy = row['Alpha (% annual)'] / (row['Beta'] * 100) if row['Beta'] > 0 else 0
        report.append(f"{row['Asset']}: Alpha/Beta ratio = {sharpe_proxy:.3f}")
    report.append("```")
    report.append("")
    report.append("Higher Alpha/Beta ratio = Better risk-adjusted returns")
    report.append("")

    # Conclusion
    report.append("## Conclusion")
    report.append("")

    report.append("### Key Takeaways:")
    report.append("")
    report.append("1. **Beta Analysis**: All altcoins show positive beta, confirming they move with BTC")
    report.append("2. **Alpha Generation**: Positive alpha assets provide excess returns beyond market")
    report.append("3. **Diversification**: Lower beta assets reduce portfolio volatility")
    report.append("4. **Synchronization**: 70-80% same-direction movement suggests high market correlation")
    report.append("")

    report.append("### Recommended Strategy:")
    report.append("")
    report.append(f"- **Core holding (50%)**: BTC (market benchmark)")
    report.append(f"- **Alpha generator (30%)**: {best_alpha_asset} (highest excess returns)")
    report.append(f"- **Volatility reducer (20%)**: {low_beta_asset} (lowest beta)")
    report.append("")
    report.append("This mix balances market exposure, alpha generation, and risk management.")
    report.append("")

    report.append("---")
    report.append("")
    report.append("*Analysis uses linear regression with BTC as market benchmark*")
    report.append("*Risk-free rate: 4% annually*")
    report.append("*Data source: Yahoo Finance*")

    # Save report
    report_text = '\n'.join(report)
    with open('ALPHA_BETA_REPORT.md', 'w') as f:
        f.write(report_text)

    print(f"\n✓ Report saved: ALPHA_BETA_REPORT.md")

    return report_text


def fetch_2024_2025_data():
    """Fetch data from Jan 1, 2024 to present"""

    print("Fetching 2024-2025 data from Yahoo Finance...")

    tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'HYPE32196-USD']
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()

    # Download all tickers at once
    print("  Downloading all tickers...")
    data = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)

    # Extract Close prices
    if isinstance(data.columns, pd.MultiIndex):
        # Multi-ticker download returns MultiIndex columns
        close_data = data['Close']
    else:
        # Single ticker returns simple columns
        close_data = data

    # Rename columns to short names
    close_data.columns = ['BTC', 'ETH', 'HYPE', 'SOL']

    # Forward fill and drop NaN
    close_data = close_data.ffill()
    close_data = close_data.dropna()

    print(f"✓ Fetched {len(close_data)} days of data ({close_data.index[0].date()} to {close_data.index[-1].date()})")

    # Save to CSV
    close_data.to_csv('btc_eth_sol_hype_2024_2025.csv')
    print("✓ Saved to btc_eth_sol_hype_2024_2025.csv")

    return close_data


def main():
    """Main execution"""

    print("\n" + "="*70)
    print("ALPHA/BETA ANALYSIS")
    print("ETH, SOL, HYPE vs BTC (Market Benchmark)")
    print("="*70 + "\n")

    # Fetch 2024-2025 data
    data = fetch_2024_2025_data()

    # 1. Price movement analysis
    returns = analyze_price_movements(data)

    # 2. Alpha/Beta calculations
    results_df, returns = calculate_all_alpha_beta(data)

    # 3. Directional analysis
    analyze_directional_movement(data)

    # 4. Create visualization
    print("\n" + "="*70)
    print("CREATING VISUALIZATION")
    print("="*70)
    create_alpha_beta_visualization(data, results_df, returns)

    # 5. Generate report
    print("\n" + "="*70)
    print("GENERATING REPORT")
    print("="*70)
    generate_report(data, results_df, returns)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nOutput files:")
    print("  1. alpha_beta_results.csv - Numerical results")
    print("  2. alpha_beta_dashboard.html - Interactive visualization")
    print("  3. ALPHA_BETA_REPORT.md - Comprehensive report")
    print()


if __name__ == "__main__":
    main()
