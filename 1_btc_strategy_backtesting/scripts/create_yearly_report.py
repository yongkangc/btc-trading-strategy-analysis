"""
Create consolidated yearly performance report
Generates clean HTML report for screenshot
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def create_consolidated_report():
    """Create consolidated yearly report HTML"""

    # Load data
    summary_df = pd.read_csv('reports/yearly_summary.csv')
    comparison_df = pd.read_csv('reports/strategy_comparison_by_year.csv')

    # Create figure with subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Best Strategy by Year',
            'HODL vs Best Strategy Comparison',
            'Top 5 Strategies - Average Annual Return',
            'Strategy Performance Heatmap',
            'Year-over-Year Performance Trends',
            'Win/Loss Summary by Year'
        ),
        specs=[
            [{'type': 'bar'}, {'type': 'bar'}],
            [{'type': 'bar'}, {'type': 'heatmap', 'rowspan': 2}],
            [{'type': 'scatter'}, None]
        ],
        row_heights=[0.3, 0.35, 0.35],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    colors_qual = px.colors.qualitative.Set2

    # 1. Best Strategy by Year (Bar chart)
    fig.add_trace(
        go.Bar(
            x=summary_df['Year'],
            y=summary_df['Return (%)'],
            name='Best Strategy',
            text=summary_df['Best Strategy'],
            textposition='outside',
            marker=dict(
                color=summary_df['Return (%)'],
                colorscale='RdYlGn',
                showscale=False,
                line=dict(color='rgb(50,50,50)', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>%{text}<br>Return: %{y:.1f}%<extra></extra>'
        ),
        row=1, col=1
    )

    # 2. HODL vs Best Strategy
    fig.add_trace(
        go.Bar(
            x=summary_df['Year'],
            y=summary_df['HODL Return (%)'],
            name='HODL',
            marker=dict(color='rgb(102,194,165)'),
            text=[f"{x:.1f}%" for x in summary_df['HODL Return (%)']],
            textposition='auto'
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(
            x=summary_df['Year'],
            y=summary_df['Return (%)'],
            name='Best Strategy',
            marker=dict(color='rgb(252,141,98)'),
            text=[f"{x:.1f}%" for x in summary_df['Return (%)']],
            textposition='auto'
        ),
        row=1, col=2
    )

    # 3. Top 5 Strategies - Average Return
    top_5 = comparison_df.head(5)
    fig.add_trace(
        go.Bar(
            y=top_5['Strategy'],
            x=top_5['Avg Return (%)'],
            orientation='h',
            marker=dict(
                color=top_5['Avg Return (%)'],
                colorscale='Viridis',
                showscale=False
            ),
            text=[f"{x:.1f}%" for x in top_5['Avg Return (%)']],
            textposition='auto',
            showlegend=False
        ),
        row=2, col=1
    )

    # 4. Heatmap - All strategies across years
    # Prepare heatmap data
    strategies = comparison_df['Strategy'].tolist()[:10]  # Top 10 for readability
    years = ['2020', '2021', '2022', '2023', '2024', '2025']

    z_data = []
    for strategy in strategies:
        row_data = comparison_df[comparison_df['Strategy'] == strategy]
        row = [row_data[f'{year} Return (%)'].values[0] for year in years]
        z_data.append(row)

    fig.add_trace(
        go.Heatmap(
            z=z_data,
            x=years,
            y=strategies,
            colorscale='RdYlGn',
            zmid=0,
            text=[[f"{val:.1f}%" for val in row] for row in z_data],
            texttemplate='%{text}',
            textfont={"size": 9},
            colorbar=dict(title="Return (%)", x=1.15),
            showlegend=False
        ),
        row=2, col=2
    )

    # 5. Trends - Key strategies over time
    key_strategies = ['HODL', 'Buy Dip 30%', 'Buy Dip 20%', 'DCA 30d']
    for i, strategy in enumerate(key_strategies):
        row_data = comparison_df[comparison_df['Strategy'] == strategy]
        returns = [row_data[f'{year} Return (%)'].values[0] for year in years]

        fig.add_trace(
            go.Scatter(
                x=years,
                y=returns,
                mode='lines+markers',
                name=strategy,
                line=dict(width=3, color=colors_qual[i]),
                marker=dict(size=10),
                showlegend=True
            ),
            row=3, col=1
        )

    # Update layout
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_yaxes(title_text="Return (%)", row=1, col=1)

    fig.update_xaxes(title_text="Year", row=1, col=2)
    fig.update_yaxes(title_text="Return (%)", row=1, col=2)

    fig.update_xaxes(title_text="Avg Return (%)", row=2, col=1)

    fig.update_xaxes(title_text="Year", row=2, col=2)
    fig.update_yaxes(title_text="Strategy", row=2, col=2)

    fig.update_xaxes(title_text="Year", row=3, col=1)
    fig.update_yaxes(title_text="Return (%)", row=3, col=1)

    fig.update_layout(
        height=1400,
        title_text="<b>Bitcoin Trading Strategies: Yearly Performance Report (2020-2025)</b><br><sub>Comprehensive year-by-year analysis of 15 trading strategies</sub>",
        title_font_size=20,
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.08,
            xanchor="center",
            x=0.5
        )
    )

    return fig


def create_summary_tables_html():
    """Create HTML with summary tables"""

    summary_df = pd.read_csv('reports/yearly_summary.csv')
    comparison_df = pd.read_csv('reports/strategy_comparison_by_year.csv')

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Bitcoin Yearly Performance Report</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            th {
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 10px 12px;
                border-bottom: 1px solid #ecf0f1;
            }
            tr:hover {
                background-color: #f8f9fa;
            }
            .positive {
                color: #27ae60;
                font-weight: bold;
            }
            .negative {
                color: #e74c3c;
                font-weight: bold;
            }
            .neutral {
                color: #95a5a6;
            }
            .highlight {
                background-color: #fff9e6;
            }
            .summary-box {
                background-color: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .summary-box h3 {
                margin-top: 0;
                color: #2c3e50;
            }
        </style>
    </head>
    <body>
        <h1>📊 Bitcoin Trading Strategies: Yearly Performance Report (2020-2025)</h1>

        <div class="summary-box">
            <h3>Executive Summary</h3>
            <p><strong>Analysis Period:</strong> 2020-2025 (6 years including partial 2025)</p>
            <p><strong>Strategies Tested:</strong> 15 different approaches</p>
            <p><strong>Key Finding:</strong> HODL achieves highest average annual return (98.1%), outperforming all active strategies</p>
        </div>

        <h2>🏆 Best Performing Strategy by Year</h2>
        <table>
            <thead>
                <tr>
                    <th>Year</th>
                    <th>Best Strategy</th>
                    <th>Return (%)</th>
                    <th>HODL Return (%)</th>
                    <th>Outperformance (%)</th>
                    <th>Sharpe Ratio</th>
                    <th>Max Drawdown (%)</th>
                </tr>
            </thead>
            <tbody>
    """

    for _, row in summary_df.iterrows():
        return_class = 'positive' if row['Return (%)'] > 0 else 'negative'
        out_class = 'positive' if row['Outperformance (%)'] > 0 else 'neutral'

        html += f"""
                <tr>
                    <td><strong>{row['Year']}</strong></td>
                    <td>{row['Best Strategy']}</td>
                    <td class="{return_class}">{row['Return (%)']:.2f}%</td>
                    <td class="{'positive' if row['HODL Return (%)'] > 0 else 'negative'}">{row['HODL Return (%)']:.2f}%</td>
                    <td class="{out_class}">{row['Outperformance (%)']:.2f}%</td>
                    <td>{row['Sharpe']:.2f}</td>
                    <td class="negative">{row['Max DD (%)']:.2f}%</td>
                </tr>
        """

    html += """
            </tbody>
        </table>

        <h2>📈 Top 10 Strategies Ranked by Average Annual Return</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Strategy</th>
                    <th>2020</th>
                    <th>2021</th>
                    <th>2022</th>
                    <th>2023</th>
                    <th>2024</th>
                    <th>2025</th>
                    <th>Avg Return (%)</th>
                </tr>
            </thead>
            <tbody>
    """

    for rank, (_, row) in enumerate(comparison_df.head(10).iterrows(), 1):
        highlight = 'highlight' if rank <= 3 else ''

        html += f"""
                <tr class="{highlight}">
                    <td><strong>{rank}</strong></td>
                    <td><strong>{row['Strategy']}</strong></td>
        """

        for year in ['2020', '2021', '2022', '2023', '2024', '2025']:
            val = row[f'{year} Return (%)']
            val_class = 'positive' if val > 0 else 'negative' if val < 0 else 'neutral'
            html += f'<td class="{val_class}">{val:.1f}%</td>'

        html += f'<td class="positive"><strong>{row["Avg Return (%)"]:.1f}%</strong></td>'
        html += """
                </tr>
        """

    html += """
            </tbody>
        </table>

        <div class="summary-box">
            <h3>Key Insights</h3>
            <ul>
                <li><strong>2020 (COVID Crash):</strong> Buy Dip 30% crushed it with 429% return - perfect year for dip buying</li>
                <li><strong>2021 (Bull Market):</strong> HODL won with 58% - steady uptrend favored holding</li>
                <li><strong>2022 (Bear Market):</strong> MA Cross 50/200 only strategy that didn't lose money (0% vs HODL -65%)</li>
                <li><strong>2023-2024 (Recovery):</strong> HODL and technical strategies dominated</li>
                <li><strong>Overall Winner:</strong> HODL with 98% average annual return beats all active strategies</li>
                <li><strong>Sell Rules:</strong> All profit-taking strategies underperformed significantly (3-16% avg vs 67-98% buy-only)</li>
            </ul>
        </div>

    </body>
    </html>
    """

    return html


def main():
    """Generate all report components"""
    import os

    # Create yearly_reports folder
    os.makedirs('yearly_reports', exist_ok=True)
    print("✓ Created folder: yearly_reports/")

    # Generate visualizations
    print("\nGenerating visualizations...")
    fig = create_consolidated_report()
    fig.write_html('yearly_reports/yearly_performance_charts.html')
    print("✓ Saved: yearly_reports/yearly_performance_charts.html")

    # Generate summary tables
    print("\nGenerating summary tables...")
    html = create_summary_tables_html()
    with open('yearly_reports/yearly_performance_summary.html', 'w') as f:
        f.write(html)
    print("✓ Saved: yearly_reports/yearly_performance_summary.html")

    print("\n✅ Report generation complete!")
    print("📁 Files in yearly_reports/:")
    print("   - yearly_performance_charts.html")
    print("   - yearly_performance_summary.html")


if __name__ == "__main__":
    main()
