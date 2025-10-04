"""
BTC Trading Strategy Analysis using YFinance
Compares HODL vs various trading strategies with real Bitcoin data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def fetch_btc_data(start_date='2020-01-01', end_date=None):
    """Fetch BTC-USD data from Yahoo Finance"""
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    print(f"Fetching BTC-USD data from {start_date} to {end_date}...")

    btc = yf.download('BTC-USD', start=start_date, end=end_date, progress=False, auto_adjust=False)

    # Flatten multi-index columns if present
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = btc.columns.get_level_values(0)

    print(f"✓ Downloaded {len(btc)} days of data")
    print(f"  Date range: {btc.index[0].date()} to {btc.index[-1].date()}")
    min_price = btc['Close'].min()
    max_price = btc['Close'].max()
    print(f"  Price range: ${min_price:.2f} - ${max_price:.2f}")

    return btc


class BTCBacktest:
    """Bitcoin strategy backtesting engine"""

    def __init__(self, data):
        self.data = data.copy()
        self.results = {}

    def calculate_fibonacci_levels(self, prices, lookback=90):
        """Calculate Fibonacci retracement levels"""
        rolling_high = prices.rolling(window=lookback).max()
        rolling_low = prices.rolling(window=lookback).min()
        diff = rolling_high - rolling_low

        fib_levels = pd.DataFrame(index=prices.index)
        fib_levels['0.236'] = rolling_low + 0.236 * diff
        fib_levels['0.382'] = rolling_low + 0.382 * diff
        fib_levels['0.5'] = rolling_low + 0.5 * diff
        fib_levels['0.618'] = rolling_low + 0.618 * diff

        return fib_levels

    def hodl(self, capital=10000):
        """Buy and hold strategy"""
        prices = self.data['Close']
        btc = capital / prices.iloc[0]
        portfolio = btc * prices

        return {
            'name': 'HODL',
            'portfolio': portfolio,
            'returns': portfolio.pct_change().fillna(0),
            'trades': 1,
            'btc_held': btc
        }

    def fibonacci_buy(self, capital=10000, fib_level=0.382, lookback=90):
        """Buy when price hits Fibonacci support level"""
        prices = self.data['Close']
        fib_levels = self.calculate_fibonacci_levels(prices, lookback)

        cash = capital
        btc = 0
        trades = 0
        buy_size = capital * 0.1  # 10% of capital per buy
        portfolio_values = []

        for i, (date, price) in enumerate(prices.items()):
            # Buy signal: price touches Fibonacci support
            if i >= lookback and not pd.isna(fib_levels.iloc[i][str(fib_level)]):
                fib_support = fib_levels.iloc[i][str(fib_level)]

                # Buy if price is within 2% of support level
                if price <= fib_support * 1.02 and cash >= buy_size:
                    btc_bought = buy_size / price
                    btc += btc_bought
                    cash -= buy_size
                    trades += 1

            portfolio_values.append(cash + btc * price)

        portfolio_series = pd.Series(portfolio_values, index=prices.index)

        return {
            'name': f'Fib {fib_level}',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }

    def dca(self, capital=10000, frequency=30):
        """Dollar Cost Averaging strategy"""
        prices = self.data['Close']

        # Calculate number of buys
        total_buys = len(prices) // frequency
        buy_amount = capital / total_buys if total_buys > 0 else capital

        cash = capital
        btc = 0
        trades = 0
        portfolio_values = []

        for i, (date, price) in enumerate(prices.items()):
            # Buy on schedule
            if i % frequency == 0 and cash >= buy_amount:
                btc += buy_amount / price
                cash -= buy_amount
                trades += 1

            portfolio_values.append(cash + btc * price)

        portfolio_series = pd.Series(portfolio_values, index=prices.index)

        return {
            'name': f'DCA {frequency}d',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }

    def calculate_metrics(self, result):
        """Calculate performance metrics"""
        pv = result['portfolio']
        ret = result['returns']

        # Total return
        total_return = (pv.iloc[-1] / pv.iloc[0] - 1) * 100

        # CAGR
        days = (pv.index[-1] - pv.index[0]).days
        years = days / 365.25
        cagr = ((pv.iloc[-1] / pv.iloc[0]) ** (1 / years) - 1) * 100 if years > 0 else 0

        # Volatility (annualized)
        volatility = ret.std() * np.sqrt(252) * 100

        # Sharpe Ratio (assuming 0% risk-free rate)
        sharpe = (ret.mean() * 252) / (ret.std() * np.sqrt(252)) if ret.std() > 0 else 0

        # Max Drawdown
        rolling_max = pv.expanding().max()
        drawdown = (pv - rolling_max) / rolling_max * 100
        max_dd = drawdown.min()

        # Win Rate
        win_rate = (ret > 0).sum() / len(ret) * 100

        return {
            'Strategy': result['name'],
            'Return (%)': round(total_return, 2),
            'CAGR (%)': round(cagr, 2),
            'Sharpe': round(sharpe, 2),
            'Volatility (%)': round(volatility, 2),
            'Max DD (%)': round(max_dd, 2),
            'Win Rate (%)': round(win_rate, 2),
            'Trades': result['trades'],
            'Final ($)': round(pv.iloc[-1], 2)
        }

    def run_all_strategies(self, capital=10000):
        """Run all trading strategies"""
        print("\n" + "="*70)
        print("RUNNING STRATEGIES")
        print("="*70)

        strategies = [
            self.hodl(capital),
            self.fibonacci_buy(capital, 0.236, 90),
            self.fibonacci_buy(capital, 0.382, 90),
            self.fibonacci_buy(capital, 0.5, 90),
            self.fibonacci_buy(capital, 0.618, 90),
            self.dca(capital, 7),   # Weekly
            self.dca(capital, 30),  # Monthly
        ]

        results = []
        for s in strategies:
            self.results[s['name']] = s
            metrics = self.calculate_metrics(s)
            results.append(metrics)

            print(f"\n{s['name']:20s} | Return: {metrics['Return (%)']:>10.2f}% | Trades: {metrics['Trades']:>3d}")

        df = pd.DataFrame(results).set_index('Strategy')
        return df

    def create_dashboard(self, df_results):
        """Create interactive Plotly dashboard"""

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Portfolio Value Over Time',
                'Total Return Comparison',
                'Risk-Return Profile',
                'Drawdown Analysis'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'bar'}],
                [{'type': 'scatter'}, {'type': 'scatter'}]
            ]
        )

        colors = px.colors.qualitative.Set2

        # 1. Portfolio value evolution
        for i, (name, data) in enumerate(self.results.items()):
            fig.add_trace(
                go.Scatter(
                    x=data['portfolio'].index,
                    y=data['portfolio'],
                    name=name,
                    line=dict(width=2, color=colors[i % len(colors)])
                ),
                row=1, col=1
            )

        # 2. Total return bars
        sorted_df = df_results.sort_values('Return (%)', ascending=True)
        fig.add_trace(
            go.Bar(
                y=sorted_df.index,
                x=sorted_df['Return (%)'],
                orientation='h',
                marker=dict(
                    color=sorted_df['Return (%)'],
                    colorscale='RdYlGn',
                    showscale=False
                ),
                text=[f"{x:.1f}%" for x in sorted_df['Return (%)']],
                textposition='auto',
                showlegend=False
            ),
            row=1, col=2
        )

        # 3. Risk-return scatter
        fig.add_trace(
            go.Scatter(
                x=df_results['Volatility (%)'],
                y=df_results['Return (%)'],
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=df_results['Sharpe'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Sharpe")
                ),
                text=df_results.index,
                textposition='top center',
                showlegend=False
            ),
            row=2, col=1
        )

        # 4. Drawdown chart
        for i, (name, data) in enumerate(self.results.items()):
            pv = data['portfolio']
            rolling_max = pv.expanding().max()
            drawdown = (pv - rolling_max) / rolling_max * 100

            fig.add_trace(
                go.Scatter(
                    x=drawdown.index,
                    y=drawdown,
                    name=name,
                    line=dict(width=1.5, color=colors[i % len(colors)]),
                    showlegend=False
                ),
                row=2, col=2
            )

        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=1)

        fig.update_xaxes(title_text="Return (%)", row=1, col=2)

        fig.update_xaxes(title_text="Volatility (%)", row=2, col=1)
        fig.update_yaxes(title_text="Return (%)", row=2, col=1)

        fig.update_xaxes(title_text="Date", row=2, col=2)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=2)

        fig.update_layout(
            height=900,
            title_text="<b>Bitcoin Trading Strategies Analysis (YFinance Real Data)</b>",
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5
            )
        )

        return fig


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("BITCOIN STRATEGY ANALYSIS - REAL DATA (YFINANCE)")
    print("="*70)

    # Fetch BTC data (5 years)
    btc_data = fetch_btc_data(start_date='2020-01-01')

    # Initialize backtest
    backtest = BTCBacktest(btc_data)

    # Run strategies
    results = backtest.run_all_strategies(capital=10000)

    # Display results
    print("\n" + "="*70)
    print("PERFORMANCE METRICS")
    print("="*70)
    print(results.to_string())

    # Key insights
    best = results['Return (%)'].idxmax()
    hodl_return = results.loc['HODL', 'Return (%)']
    best_return = results.loc[best, 'Return (%)']

    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print(f"\n🏆 Best Strategy: {best}")
    print(f"   └─ Return: {best_return:.2f}%")
    print(f"   └─ Sharpe: {results.loc[best, 'Sharpe']:.2f}")

    print(f"\n📊 HODL Baseline: {hodl_return:.2f}%")

    diff = best_return - hodl_return
    if diff > 0:
        print(f"\n💡 {best} outperformed HODL by {diff:.2f}%")
    else:
        print(f"\n💡 HODL outperformed by {abs(diff):.2f}%")

    # Risk analysis
    print(f"\n🛡️  Lowest Drawdown: {results['Max DD (%)'].idxmax()}")
    print(f"   └─ Max DD: {results['Max DD (%)'].max():.2f}%")

    # Create and save dashboard
    print("\n" + "="*70)
    print("GENERATING OUTPUTS")
    print("="*70)

    fig = backtest.create_dashboard(results)
    fig.write_html('btc_yfinance_dashboard.html')
    print("✓ Dashboard saved: btc_yfinance_dashboard.html")

    results.to_csv('btc_yfinance_results.csv')
    print("✓ Results saved: btc_yfinance_results.csv")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)

    return backtest, results


if __name__ == "__main__":
    backtest, results = main()
