"""
Bitcoin Trading Strategy Yearly Analysis
Analyzes strategy performance year-by-year (2020-2025)
Generates detailed reports in reports/ folder
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os
from btc_yfinance_analysis import BTCBacktest, fetch_btc_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_reports_folder():
    """Create reports directory if it doesn't exist"""
    os.makedirs('reports', exist_ok=True)
    print("✓ Reports folder ready: reports/")


def run_yearly_analysis(btc_data, capital=10000):
    """Run all strategies for each year and aggregate results"""

    # Define year ranges
    years = {
        '2020': ('2020-01-01', '2020-12-31'),
        '2021': ('2021-01-01', '2021-12-31'),
        '2022': ('2022-01-01', '2022-12-31'),
        '2023': ('2023-01-01', '2023-12-31'),
        '2024': ('2024-01-01', '2024-12-31'),
        '2025': ('2025-01-01', '2025-12-31'),
    }

    yearly_results = {}

    for year, (start, end) in years.items():
        print(f"\n{'='*70}")
        print(f"ANALYZING YEAR: {year}")
        print(f"{'='*70}")

        # Filter data for this year
        year_data = btc_data[start:end]

        if len(year_data) == 0:
            print(f"⚠️  No data for {year}, skipping...")
            continue

        print(f"  Data points: {len(year_data)} days")
        print(f"  Price range: ${year_data['Close'].min():.2f} → ${year_data['Close'].max():.2f}")

        # Initialize backtest with year data
        backtest = BTCBacktest(year_data)

        # Run all strategies
        strategies = [
            backtest.hodl(capital),
            backtest.buy_the_dip(capital, 10),
            backtest.buy_the_dip(capital, 20),
            backtest.buy_the_dip(capital, 30),
            backtest.buy_the_dip(capital, 30, sell_rule='profit_25'),
            backtest.buy_the_dip(capital, 30, sell_rule='sma_50'),
            backtest.buy_the_dip(capital, 30, sell_rule='ema_21'),
            backtest.buy_the_dip(capital, 30, sell_rule='bb_middle'),
            backtest.buy_the_dip(capital, 30, sell_rule='ema_cross'),
            backtest.buy_the_dip(capital, 30, sell_rule='sma_distance'),
            backtest.rsi_strategy(capital, 30),
            backtest.ma_crossover(capital, 50, 200),
            backtest.bollinger_bands(capital, 20),
            backtest.dca(capital, 30),
            backtest.volatility_adjusted_dca(capital, 30),
        ]

        year_results = []
        for s in strategies:
            metrics = backtest.calculate_metrics(s)
            year_results.append(metrics)

        yearly_results[year] = pd.DataFrame(year_results).set_index('Strategy')

        # Show top 3 performers
        top_3 = yearly_results[year].nlargest(3, 'Return (%)')
        print(f"\n🏆 Top 3 Strategies in {year}:")
        for idx, (strategy, row) in enumerate(top_3.iterrows(), 1):
            print(f"  {idx}. {strategy:30s} | {row['Return (%)']:>8.2f}%")

    return yearly_results


def create_yearly_summary_table(yearly_results):
    """Create summary table showing best strategy per year"""
    summary_data = []

    for year, df in yearly_results.items():
        best_strategy = df['Return (%)'].idxmax()
        best_return = df.loc[best_strategy, 'Return (%)']
        hodl_return = df.loc['HODL', 'Return (%)']

        summary_data.append({
            'Year': year,
            'Best Strategy': best_strategy,
            'Return (%)': best_return,
            'HODL Return (%)': hodl_return,
            'Outperformance (%)': best_return - hodl_return,
            'Sharpe': df.loc[best_strategy, 'Sharpe'],
            'Max DD (%)': df.loc[best_strategy, 'Max DD (%)']
        })

    return pd.DataFrame(summary_data)


def create_strategy_comparison_table(yearly_results):
    """Create table comparing each strategy across all years"""

    # Get all strategy names from first year
    first_year = list(yearly_results.keys())[0]
    strategies = yearly_results[first_year].index.tolist()

    comparison_data = []

    for strategy in strategies:
        row = {'Strategy': strategy}

        for year, df in yearly_results.items():
            if strategy in df.index:
                row[f'{year} Return (%)'] = df.loc[strategy, 'Return (%)']
            else:
                row[f'{year} Return (%)'] = np.nan

        # Calculate average return across all years
        returns = [row[f'{year} Return (%)'] for year in yearly_results.keys()
                   if f'{year} Return (%)' in row and not pd.isna(row[f'{year} Return (%)'])]
        row['Avg Return (%)'] = np.mean(returns) if returns else np.nan

        comparison_data.append(row)

    df = pd.DataFrame(comparison_data)
    return df.sort_values('Avg Return (%)', ascending=False)


def create_yearly_heatmap(yearly_results):
    """Create heatmap visualization of strategy performance by year"""

    # Prepare data for heatmap
    first_year = list(yearly_results.keys())[0]
    strategies = yearly_results[first_year].index.tolist()
    years = list(yearly_results.keys())

    # Build matrix
    z_data = []
    for strategy in strategies:
        row = []
        for year in years:
            if strategy in yearly_results[year].index:
                row.append(yearly_results[year].loc[strategy, 'Return (%)'])
            else:
                row.append(np.nan)
        z_data.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=years,
        y=strategies,
        colorscale='RdYlGn',
        colorbar=dict(title="Return (%)"),
        text=[[f"{val:.1f}%" if not np.isnan(val) else "" for val in row] for row in z_data],
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))

    fig.update_layout(
        title="<b>Strategy Performance by Year (Return %)</b>",
        xaxis_title="Year",
        yaxis_title="Strategy",
        height=800,
        template='plotly_white'
    )

    return fig


def create_yearly_trends_chart(yearly_results):
    """Create line chart showing strategy trends over years"""

    # Select key strategies to track
    key_strategies = [
        'HODL',
        'Buy Dip 30%',
        'Buy Dip 30% (profit_25)',
        'RSI <30',
        'MA Cross 50/200',
        'DCA 30d'
    ]

    fig = go.Figure()

    years = list(yearly_results.keys())

    for strategy in key_strategies:
        returns = []
        for year in years:
            if strategy in yearly_results[year].index:
                returns.append(yearly_results[year].loc[strategy, 'Return (%)'])
            else:
                returns.append(None)

        fig.add_trace(go.Scatter(
            x=years,
            y=returns,
            mode='lines+markers',
            name=strategy,
            line=dict(width=2),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title="<b>Key Strategy Performance Trends (2020-2025)</b>",
        xaxis_title="Year",
        yaxis_title="Return (%)",
        height=600,
        template='plotly_white',
        hovermode='x unified'
    )

    return fig


def generate_html_report(yearly_results, summary_df, comparison_df):
    """Generate comprehensive HTML report"""

    fig_heatmap = create_yearly_heatmap(yearly_results)
    fig_trends = create_yearly_trends_chart(yearly_results)

    # Create combined dashboard
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Strategy Performance by Year', 'Performance Trends Over Time'),
        specs=[[{"type": "heatmap"}], [{"type": "scatter"}]],
        row_heights=[0.6, 0.4],
        vertical_spacing=0.12
    )

    # Add heatmap
    heatmap = fig_heatmap.data[0]
    fig.add_trace(heatmap, row=1, col=1)

    # Add trend lines
    for trace in fig_trends.data:
        fig.add_trace(trace, row=2, col=1)

    fig.update_layout(
        height=1200,
        title_text="<b>Bitcoin Strategy Analysis: Yearly Performance Report (2020-2025)</b>",
        template='plotly_white',
        showlegend=True
    )

    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_yaxes(title_text="Strategy", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Return (%)", row=2, col=1)

    return fig


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("BITCOIN YEARLY STRATEGY ANALYSIS (2020-2025)")
    print("="*70)

    # Create reports folder
    create_reports_folder()

    # Fetch data
    btc_data = fetch_btc_data(start_date='2020-01-01')

    # Run yearly analysis
    yearly_results = run_yearly_analysis(btc_data, capital=10000)

    # Generate summary tables
    print("\n" + "="*70)
    print("GENERATING REPORTS")
    print("="*70)

    summary_df = create_yearly_summary_table(yearly_results)
    comparison_df = create_strategy_comparison_table(yearly_results)

    # Save individual year results
    for year, df in yearly_results.items():
        filename = f'reports/yearly_performance_{year}.csv'
        df.to_csv(filename)
        print(f"✓ Saved: {filename}")

    # Save summary tables
    summary_df.to_csv('reports/yearly_summary.csv', index=False)
    print("✓ Saved: reports/yearly_summary.csv")

    comparison_df.to_csv('reports/strategy_comparison_by_year.csv', index=False)
    print("✓ Saved: reports/strategy_comparison_by_year.csv")

    # Generate HTML report
    html_fig = generate_html_report(yearly_results, summary_df, comparison_df)
    html_fig.write_html('reports/yearly_analysis_dashboard.html')
    print("✓ Saved: reports/yearly_analysis_dashboard.html")

    # Display summary
    print("\n" + "="*70)
    print("YEARLY SUMMARY")
    print("="*70)
    print(summary_df.to_string(index=False))

    print("\n" + "="*70)
    print("TOP 5 STRATEGIES (BY AVERAGE YEARLY RETURN)")
    print("="*70)
    print(comparison_df.head().to_string(index=False))

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print("\n📁 All reports saved to: reports/")
    print("   - yearly_performance_YYYY.csv (6 files)")
    print("   - yearly_summary.csv")
    print("   - strategy_comparison_by_year.csv")
    print("   - yearly_analysis_dashboard.html")

    return yearly_results, summary_df, comparison_df


if __name__ == "__main__":
    yearly_results, summary_df, comparison_df = main()
