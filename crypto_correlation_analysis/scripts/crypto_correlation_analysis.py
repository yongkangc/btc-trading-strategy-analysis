"""
Cryptocurrency Correlation Analysis: ETH, SOL, HYPE
Analyzes volatility, correlation, monthly returns, and Sortino ratios
Using Yahoo Finance for historical data (past 3 years)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Use Yahoo Finance for more reliable data
# Ticker mappings
TICKERS = {
    'ETH': 'ETH-USD',
    'SOL': 'SOL-USD',
    'HYPE': 'HYPE32196-USD'  # Hyperliquid on Yahoo Finance
}


def fetch_yfinance_data(ticker, start_date=None, end_date=None):
    """
    Fetch historical price data from Yahoo Finance

    Args:
        ticker: Yahoo Finance ticker symbol (e.g., 'ETH-USD')
        start_date: Start date (default: 3 years ago)
        end_date: End date (default: today)

    Returns:
        DataFrame with Date index and Close price column
    """
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=1095)  # 3 years

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    print(f"Fetching data for {ticker} from {start_str} to {end_str}...")

    try:
        data = yf.download(ticker, start=start_str, end=end_str, progress=False, auto_adjust=False)

        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if len(data) == 0:
            print(f"✗ No data returned for {ticker}")
            return None

        # Use Close price
        df = pd.DataFrame({'price': data['Close']})

        print(f"✓ Fetched {len(df)} days for {ticker}")
        print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"  Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")

        return df

    except Exception as e:
        print(f"✗ Error fetching {ticker}: {e}")
        return None


def get_all_crypto_data():
    """Fetch data for ETH, SOL, and HYPE using Yahoo Finance"""

    data = {}

    for symbol, ticker in TICKERS.items():
        df = fetch_yfinance_data(ticker)
        if df is not None:
            data[symbol] = df

    if not data:
        print("✗ No data fetched for any cryptocurrency")
        return pd.DataFrame()

    # Combine into single DataFrame
    combined = pd.DataFrame()
    for symbol, df in data.items():
        combined[symbol] = df['price']

    # Forward fill any missing data
    combined = combined.ffill()

    # Drop rows where all values are NaN
    combined = combined.dropna(how='all')

    if len(combined) == 0:
        print("✗ Combined dataframe is empty")
        return pd.DataFrame()

    print(f"\n{'='*70}")
    print("COMBINED DATA SUMMARY")
    print(f"{'='*70}")
    print(f"Total rows: {len(combined)}")
    print(f"Date range: {combined.index[0].date()} to {combined.index[-1].date()}")
    print(f"Columns: {list(combined.columns)}")
    print(f"\nFirst few rows:")
    print(combined.head())
    print(f"\nLast few rows:")
    print(combined.tail())

    # Save raw data
    combined.to_csv('crypto_raw_data.csv')
    print(f"✓ Saved raw data to crypto_raw_data.csv")

    return combined


def calculate_monthly_returns(data):
    """Calculate month-over-month returns for each cryptocurrency"""

    # Resample to monthly (last day of each month)
    monthly_prices = data.resample('ME').last()

    # Calculate percentage change
    monthly_returns = monthly_prices.pct_change() * 100  # Convert to percentage

    # Add month/year columns for readability
    monthly_returns['Month'] = monthly_returns.index.strftime('%Y-%m')

    print(f"\n{'='*70}")
    print("MONTHLY RETURNS CALCULATED")
    print(f"{'='*70}")
    print(f"Total months: {len(monthly_returns)}")
    print("\nFirst 5 months:")
    print(monthly_returns.head())

    # Save to CSV
    monthly_returns.to_csv('monthly_returns.csv')
    print(f"✓ Saved monthly returns to monthly_returns.csv")

    return monthly_returns


def calculate_correlation(data):
    """Calculate correlation matrix between cryptocurrencies"""

    # Daily returns
    daily_returns = data.pct_change().dropna()

    # Correlation matrix
    corr_matrix = daily_returns.corr()

    print(f"\n{'='*70}")
    print("CORRELATION MATRIX")
    print(f"{'='*70}")
    print(corr_matrix)

    # Save to CSV
    corr_matrix.to_csv('correlation_matrix.csv')
    print(f"✓ Saved correlation matrix to correlation_matrix.csv")

    return corr_matrix


def calculate_volatility(data):
    """Calculate annualized volatility (standard deviation of returns)"""

    # Daily returns
    daily_returns = data.pct_change().dropna()

    # Annualized volatility (crypto trades 365 days/year)
    volatility = daily_returns.std() * np.sqrt(365) * 100  # Convert to percentage

    print(f"\n{'='*70}")
    print("ANNUALIZED VOLATILITY")
    print(f"{'='*70}")
    for coin, vol in volatility.items():
        print(f"{coin}: {vol:.2f}%")

    # Create DataFrame
    vol_df = pd.DataFrame({'Cryptocurrency': volatility.index, 'Volatility (%)': volatility.values})
    vol_df.to_csv('volatility.csv', index=False)
    print(f"✓ Saved volatility to volatility.csv")

    return volatility


def calculate_sortino_ratio(data, risk_free_rate=0.04):
    """
    Calculate Sortino Ratio for each cryptocurrency

    Sortino Ratio = (Return - Risk Free Rate) / Downside Deviation
    Uses only negative returns for downside deviation calculation

    Args:
        data: DataFrame with price data
        risk_free_rate: Annual risk-free rate (default: 4%)
    """

    # Daily returns
    daily_returns = data.pct_change().dropna()

    # Annualized returns
    total_days = len(daily_returns)
    years = total_days / 365
    annualized_returns = ((data.iloc[-1] / data.iloc[0]) ** (1 / years) - 1)

    # Downside deviation (only negative returns)
    # Daily risk-free rate
    daily_rf = risk_free_rate / 365

    sortino_ratios = {}
    downside_devs = {}

    for coin in data.columns:
        # Calculate excess returns (return - risk free)
        excess_returns = daily_returns[coin] - daily_rf

        # Downside deviation: std of returns below risk-free rate
        downside_returns = excess_returns[excess_returns < 0]
        downside_dev = downside_returns.std() * np.sqrt(365)  # Annualized
        downside_devs[coin] = downside_dev

        # Sortino Ratio
        if downside_dev > 0:
            sortino = (annualized_returns[coin] - risk_free_rate) / downside_dev
            sortino_ratios[coin] = sortino
        else:
            sortino_ratios[coin] = np.nan

    print(f"\n{'='*70}")
    print("SORTINO RATIO (Risk-free rate: {:.1f}%)".format(risk_free_rate * 100))
    print(f"{'='*70}")

    for coin in data.columns:
        print(f"{coin}:")
        print(f"  Annualized Return: {annualized_returns[coin]*100:.2f}%")
        print(f"  Downside Deviation: {downside_devs[coin]*100:.2f}%")
        print(f"  Sortino Ratio: {sortino_ratios[coin]:.3f}")

    # Create DataFrame
    sortino_df = pd.DataFrame({
        'Cryptocurrency': data.columns,
        'Annualized Return (%)': [annualized_returns[c] * 100 for c in data.columns],
        'Downside Deviation (%)': [downside_devs[c] * 100 for c in data.columns],
        'Sortino Ratio': [sortino_ratios[c] for c in data.columns]
    })

    sortino_df.to_csv('sortino_ratios.csv', index=False)
    print(f"✓ Saved Sortino ratios to sortino_ratios.csv")

    return sortino_df


def create_dashboard(data, monthly_returns, corr_matrix, volatility, sortino_df):
    """Create interactive Plotly dashboard with all metrics"""

    # Create subplots: 2x3 grid
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Price History (3 Years)',
            'Correlation Heatmap',
            'Monthly Returns Comparison',
            'Annualized Volatility',
            'Sortino Ratios',
            'Cumulative Returns'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "heatmap"}],
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # 1. Price History (normalized to 100)
    normalized_prices = (data / data.iloc[0]) * 100
    for coin in data.columns:
        fig.add_trace(
            go.Scatter(x=data.index, y=normalized_prices[coin], name=coin,
                      mode='lines', showlegend=True),
            row=1, col=1
        )

    # 2. Correlation Heatmap
    fig.add_trace(
        go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 14},
            showscale=True
        ),
        row=1, col=2
    )

    # 3. Monthly Returns (last 12 months)
    recent_monthly = monthly_returns.dropna().tail(12)
    for coin in data.columns:
        fig.add_trace(
            go.Scatter(x=recent_monthly.index, y=recent_monthly[coin],
                      name=f'{coin} Returns', mode='lines+markers'),
            row=2, col=1
        )

    # 4. Volatility Bar Chart
    fig.add_trace(
        go.Bar(x=volatility.index, y=volatility.values,
               marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
               showlegend=False),
        row=2, col=2
    )

    # 5. Sortino Ratios Bar Chart
    fig.add_trace(
        go.Bar(x=sortino_df['Cryptocurrency'], y=sortino_df['Sortino Ratio'],
               marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
               showlegend=False),
        row=3, col=1
    )

    # 6. Cumulative Returns
    cumulative_returns = (data / data.iloc[0] - 1) * 100
    for coin in data.columns:
        fig.add_trace(
            go.Scatter(x=data.index, y=cumulative_returns[coin],
                      name=f'{coin} Cumulative', mode='lines'),
            row=3, col=2
        )

    # Update axes labels
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Normalized Price (Base=100)", row=1, col=1)

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Monthly Return (%)", row=2, col=1)

    fig.update_xaxes(title_text="Cryptocurrency", row=2, col=2)
    fig.update_yaxes(title_text="Volatility (%)", row=2, col=2)

    fig.update_xaxes(title_text="Cryptocurrency", row=3, col=1)
    fig.update_yaxes(title_text="Sortino Ratio", row=3, col=1)

    fig.update_xaxes(title_text="Date", row=3, col=2)
    fig.update_yaxes(title_text="Cumulative Return (%)", row=3, col=2)

    # Update layout
    fig.update_layout(
        height=1400,
        width=1600,
        title_text="Cryptocurrency Correlation Analysis: ETH, SOL, HYPE (3 Years)",
        title_font_size=22,
        showlegend=True,
        hovermode='x unified'
    )

    # Save dashboard
    fig.write_html('crypto_correlation_dashboard.html')
    print(f"\n{'='*70}")
    print("✓ Dashboard created: crypto_correlation_dashboard.html")
    print(f"{'='*70}")

    return fig


def generate_summary_report(data, monthly_returns, corr_matrix, volatility, sortino_df):
    """Generate text summary of key findings"""

    print(f"\n{'='*70}")
    print("SUMMARY REPORT: ETH, SOL, HYPE (3-Year Analysis)")
    print(f"{'='*70}")

    # Date range
    print(f"\nData Period: {data.index[0].date()} to {data.index[-1].date()}")
    print(f"Total Days: {len(data)}")

    # Price performance
    print(f"\n{'='*70}")
    print("PRICE PERFORMANCE")
    print(f"{'='*70}")
    for coin in data.columns:
        initial = data[coin].iloc[0]
        final = data[coin].iloc[-1]
        return_pct = ((final / initial) - 1) * 100
        print(f"{coin}:")
        print(f"  Initial: ${initial:.2f}")
        print(f"  Final: ${final:.2f}")
        print(f"  Total Return: {return_pct:.2f}%")

    # Monthly statistics
    print(f"\n{'='*70}")
    print("MONTHLY RETURN STATISTICS")
    print(f"{'='*70}")
    for coin in data.columns:
        returns = monthly_returns[coin].dropna()
        print(f"{coin}:")
        print(f"  Average Monthly Return: {returns.mean():.2f}%")
        print(f"  Best Month: {returns.max():.2f}%")
        print(f"  Worst Month: {returns.min():.2f}%")
        print(f"  Positive Months: {(returns > 0).sum()} / {len(returns)}")

    # Correlation insights
    print(f"\n{'='*70}")
    print("CORRELATION INSIGHTS")
    print(f"{'='*70}")
    print("Correlation Matrix:")
    print(corr_matrix)
    print("\nHighest Correlation: ", end="")

    # Find highest correlation (excluding diagonal)
    corr_values = []
    for i in range(len(corr_matrix)):
        for j in range(i+1, len(corr_matrix)):
            corr_values.append((corr_matrix.index[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))

    highest = max(corr_values, key=lambda x: x[2])
    print(f"{highest[0]} - {highest[1]}: {highest[2]:.3f}")

    # Volatility ranking
    print(f"\n{'='*70}")
    print("VOLATILITY RANKING (Highest to Lowest)")
    print(f"{'='*70}")
    vol_sorted = volatility.sort_values(ascending=False)
    for i, (coin, vol) in enumerate(vol_sorted.items(), 1):
        print(f"{i}. {coin}: {vol:.2f}%")

    # Sortino ranking
    print(f"\n{'='*70}")
    print("SORTINO RATIO RANKING (Best to Worst)")
    print(f"{'='*70}")
    sortino_sorted = sortino_df.sort_values('Sortino Ratio', ascending=False)
    for i, row in sortino_sorted.iterrows():
        print(f"{int(i)+1}. {row['Cryptocurrency']}: {row['Sortino Ratio']:.3f}")

    print(f"\n{'='*70}")
    print("Analysis Complete!")
    print(f"{'='*70}\n")


def main():
    """Main execution function"""

    print("="*70)
    print("CRYPTOCURRENCY CORRELATION ANALYSIS")
    print("ETH, SOL, HYPE - 3 Year Analysis")
    print("="*70)

    # 1. Fetch data
    print("\n[1/6] Fetching cryptocurrency data...")
    data = get_all_crypto_data()

    if data.empty:
        print("✗ No data fetched. Exiting.")
        return

    # 2. Calculate monthly returns
    print("\n[2/6] Calculating monthly returns...")
    monthly_returns = calculate_monthly_returns(data)

    # 3. Calculate correlation
    print("\n[3/6] Calculating correlation matrix...")
    corr_matrix = calculate_correlation(data)

    # 4. Calculate volatility
    print("\n[4/6] Calculating volatility...")
    volatility = calculate_volatility(data)

    # 5. Calculate Sortino ratios
    print("\n[5/6] Calculating Sortino ratios...")
    sortino_df = calculate_sortino_ratio(data)

    # 6. Create dashboard
    print("\n[6/6] Creating interactive dashboard...")
    create_dashboard(data, monthly_returns, corr_matrix, volatility, sortino_df)

    # Generate summary report
    generate_summary_report(data, monthly_returns, corr_matrix, volatility, sortino_df)

    print("All outputs saved to current directory:")
    print("  - crypto_raw_data.csv")
    print("  - monthly_returns.csv")
    print("  - correlation_matrix.csv")
    print("  - volatility.csv")
    print("  - sortino_ratios.csv")
    print("  - crypto_correlation_dashboard.html")


if __name__ == "__main__":
    main()
