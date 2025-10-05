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

    # Save raw data to CSV
    btc.to_csv('btc_raw_data.csv')
    print(f"✓ Saved raw price data to btc_raw_data.csv")

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

    def hodl(self, capital=10000, fee=0.001):
        """Buy and hold strategy"""
        prices = self.data['Close']
        # Deduct 0.1% fee on purchase
        btc = (capital * (1 - fee)) / prices.iloc[0]
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

    def dca(self, capital=10000, frequency=30, fee=0.001):
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
                # Deduct 0.1% fee
                btc += (buy_amount * (1 - fee)) / price
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

    def buy_the_dip(self, capital=10000, dip_percent=10, fee=0.001, sell_rule=None):
        """Buy the Dip strategy - buy when price drops X% from recent high

        sell_rule options:
        - None: Never sell (default)
        - 'profit_25': Sell at +25% profit
        - 'sma_50': Sell when price crosses above 50-day SMA
        - 'ema_21': Sell when price crosses above 21-day EMA
        - 'bb_middle': Sell when price reaches middle Bollinger Band
        - 'ema_cross': Sell when 9-EMA crosses above 21-EMA
        - 'sma_distance': Sell when price > 20% above 200-day SMA
        """
        prices = self.data['Close']

        # Pre-calculate indicators for sell rules
        sma_50 = prices.rolling(window=50).mean() if sell_rule == 'sma_50' else None
        ema_21 = prices.ewm(span=21, adjust=False).mean() if sell_rule == 'ema_21' else None
        ema_9 = prices.ewm(span=9, adjust=False).mean() if sell_rule == 'ema_cross' else None
        ema_21_cross = prices.ewm(span=21, adjust=False).mean() if sell_rule == 'ema_cross' else None
        sma_200 = prices.rolling(window=200).mean() if sell_rule == 'sma_distance' else None

        if sell_rule == 'bb_middle':
            bb_ma = prices.rolling(window=20).mean()
        else:
            bb_ma = None

        cash = capital
        btc = 0
        trades = 0
        buy_amount = capital * 0.1  # 10% of capital per dip
        buy_prices = []  # Track purchase prices for profit target

        # Track rolling high
        rolling_high = prices.expanding().max()
        portfolio_values = []

        for i, (date, price) in enumerate(prices.items()):
            # SELL LOGIC - Use crossover detection to avoid excessive trading
            if btc > 0 and sell_rule:
                should_sell = False

                if sell_rule == 'profit_25' and len(buy_prices) > 0:
                    avg_buy_price = np.mean(buy_prices)
                    if price >= avg_buy_price * 1.25:  # +25% profit
                        should_sell = True

                elif sell_rule == 'sma_50' and i >= 51 and sma_50 is not None:
                    # Crossover detection: was below, now above
                    prev_price = prices.iloc[i-1]
                    prev_sma = sma_50.iloc[i-1]
                    if prev_price <= prev_sma and price > sma_50.iloc[i]:
                        should_sell = True

                elif sell_rule == 'ema_21' and i >= 22 and ema_21 is not None:
                    # Crossover detection: was below, now above
                    prev_price = prices.iloc[i-1]
                    prev_ema = ema_21.iloc[i-1]
                    if prev_price <= prev_ema and price > ema_21.iloc[i]:
                        should_sell = True

                elif sell_rule == 'bb_middle' and i >= 21 and bb_ma is not None:
                    # Crossover detection: was below, now above
                    prev_price = prices.iloc[i-1]
                    prev_bb = bb_ma.iloc[i-1]
                    if prev_price <= prev_bb and price >= bb_ma.iloc[i]:
                        should_sell = True

                elif sell_rule == 'ema_cross' and i >= 22:
                    # Crossover detection: 9-EMA crosses above 21-EMA
                    prev_ema9 = ema_9.iloc[i-1]
                    prev_ema21 = ema_21_cross.iloc[i-1]
                    if prev_ema9 <= prev_ema21 and ema_9.iloc[i] > ema_21_cross.iloc[i]:
                        should_sell = True

                elif sell_rule == 'sma_distance' and i >= 201 and sma_200 is not None:
                    # Crossover detection: crosses above 120% of 200 SMA
                    prev_price = prices.iloc[i-1]
                    prev_threshold = sma_200.iloc[i-1] * 1.20
                    curr_threshold = sma_200.iloc[i] * 1.20
                    if prev_price <= prev_threshold and price > curr_threshold:
                        should_sell = True

                if should_sell:
                    # Sell all BTC
                    cash += btc * price * (1 - fee)
                    btc = 0
                    buy_prices = []
                    trades += 1

            # BUY LOGIC
            if i > 0:
                # Calculate drawdown from rolling high
                drawdown_pct = ((price - rolling_high.iloc[i]) / rolling_high.iloc[i]) * 100

                # Buy if price dropped by target percentage
                if drawdown_pct <= -dip_percent and cash >= buy_amount:
                    # Deduct 0.1% fee
                    btc_bought = (buy_amount * (1 - fee)) / price
                    btc += btc_bought
                    cash -= buy_amount
                    buy_prices.append(price)
                    trades += 1

            portfolio_values.append(cash + btc * price)

        portfolio_series = pd.Series(portfolio_values, index=prices.index)

        sell_suffix = f" ({sell_rule})" if sell_rule else ""
        return {
            'name': f'Buy Dip {dip_percent}%{sell_suffix}',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }

    def rsi_strategy(self, capital=10000, rsi_threshold=30, period=14, fee=0.001):
        """RSI Oversold strategy - buy when RSI < threshold"""
        prices = self.data['Close']

        # Calculate RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        cash = capital
        btc = 0
        trades = 0
        buy_amount = capital * 0.1  # 10% per signal
        portfolio_values = []

        for i, (date, price) in enumerate(prices.items()):
            if i >= period:
                # Buy when RSI is oversold
                if rsi.iloc[i] < rsi_threshold and cash >= buy_amount:
                    # Deduct 0.1% fee
                    btc += (buy_amount * (1 - fee)) / price
                    cash -= buy_amount
                    trades += 1

            portfolio_values.append(cash + btc * price)

        portfolio_series = pd.Series(portfolio_values, index=prices.index)

        return {
            'name': f'RSI <{rsi_threshold}',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }

    def ma_crossover(self, capital=10000, short_window=50, long_window=200, fee=0.001):
        """Moving Average Crossover - Golden Cross/Death Cross"""
        prices = self.data['Close']

        # Calculate moving averages
        ma_short = prices.rolling(window=short_window).mean()
        ma_long = prices.rolling(window=long_window).mean()

        cash = capital
        btc = 0
        trades = 0
        portfolio_values = []
        position = False  # Track if we're holding BTC

        for i, (date, price) in enumerate(prices.items()):
            if i >= long_window:
                # Golden Cross - buy signal
                if ma_short.iloc[i] > ma_long.iloc[i] and not position and cash > 0:
                    # Deduct 0.1% fee on buy
                    btc = (cash * (1 - fee)) / price
                    cash = 0
                    position = True
                    trades += 1

                # Death Cross - sell signal (convert back to cash)
                elif ma_short.iloc[i] < ma_long.iloc[i] and position and btc > 0:
                    # Deduct 0.1% fee on sell
                    cash = btc * price * (1 - fee)
                    btc = 0
                    position = False
                    trades += 1

            portfolio_values.append(cash + btc * price)

        portfolio_series = pd.Series(portfolio_values, index=prices.index)

        return {
            'name': f'MA Cross {short_window}/{long_window}',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }

    def bollinger_bands(self, capital=10000, period=20, num_std=2, fee=0.001):
        """Bollinger Bands - buy at lower band (mean reversion)"""
        prices = self.data['Close']

        # Calculate Bollinger Bands
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        lower_band = ma - (num_std * std)
        upper_band = ma + (num_std * std)

        cash = capital
        btc = 0
        trades = 0
        buy_amount = capital * 0.1
        portfolio_values = []

        for i, (date, price) in enumerate(prices.items()):
            if i >= period:
                # Buy when price touches lower band
                if price <= lower_band.iloc[i] and cash >= buy_amount:
                    # Deduct 0.1% fee
                    btc += (buy_amount * (1 - fee)) / price
                    cash -= buy_amount
                    trades += 1

            portfolio_values.append(cash + btc * price)

        portfolio_series = pd.Series(portfolio_values, index=prices.index)

        return {
            'name': f'Bollinger {period}d',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }

    def volatility_adjusted_dca(self, capital=10000, base_frequency=30, fee=0.001):
        """Volatility-Adjusted DCA - buy more when volatility is high"""
        prices = self.data['Close']
        returns = prices.pct_change()

        # Calculate rolling volatility (30-day)
        volatility = returns.rolling(window=30).std()

        cash = capital
        btc = 0
        trades = 0
        portfolio_values = []

        # Base buy amount
        total_buys = len(prices) // base_frequency
        base_buy_amount = capital / total_buys if total_buys > 0 else capital

        for i, (date, price) in enumerate(prices.items()):
            if i % base_frequency == 0 and i >= 30:
                # Adjust buy amount based on volatility
                # Higher volatility = buy more (when cheap)
                current_vol = volatility.iloc[i]
                avg_vol = volatility.iloc[:i].mean()

                if pd.notna(current_vol) and pd.notna(avg_vol) and avg_vol > 0:
                    vol_multiplier = current_vol / avg_vol
                    # Cap multiplier between 0.5x and 2x
                    vol_multiplier = min(max(vol_multiplier, 0.5), 2.0)
                    buy_amount = base_buy_amount * vol_multiplier
                else:
                    buy_amount = base_buy_amount

                if cash >= buy_amount:
                    # Deduct 0.1% fee
                    btc += (buy_amount * (1 - fee)) / price
                    cash -= buy_amount
                    trades += 1

            portfolio_values.append(cash + btc * price)

        portfolio_series = pd.Series(portfolio_values, index=prices.index)

        return {
            'name': f'Vol-Adjusted DCA',
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

        # Volatility (annualized) - Bitcoin trades 365 days/year
        volatility = ret.std() * np.sqrt(365) * 100

        # Sharpe Ratio (assuming 0% risk-free rate) - Bitcoin trades 365 days/year
        sharpe = (ret.mean() * 365) / (ret.std() * np.sqrt(365)) if ret.std() > 0 else 0

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
            # Baseline
            self.hodl(capital),

            # Buy the Dip strategies (no sell)
            self.buy_the_dip(capital, 10),   # -10%
            self.buy_the_dip(capital, 20),   # -20%
            self.buy_the_dip(capital, 30),   # -30%

            # Buy Dip 30% with different SELL rules
            self.buy_the_dip(capital, 30, sell_rule='profit_25'),    # Sell at +25%
            self.buy_the_dip(capital, 30, sell_rule='sma_50'),       # Sell above 50 SMA
            self.buy_the_dip(capital, 30, sell_rule='ema_21'),       # Sell above 21 EMA
            self.buy_the_dip(capital, 30, sell_rule='bb_middle'),    # Sell at BB middle
            self.buy_the_dip(capital, 30, sell_rule='ema_cross'),    # Sell on 9/21 EMA cross
            self.buy_the_dip(capital, 30, sell_rule='sma_distance'), # Sell 20% above 200 SMA

            # Technical indicators
            self.rsi_strategy(capital, 30),  # RSI < 30
            self.ma_crossover(capital, 50, 200),  # Golden Cross
            self.bollinger_bands(capital, 20),  # Bollinger Bands

            # DCA variants
            self.dca(capital, 30),  # Standard Monthly DCA
            self.volatility_adjusted_dca(capital, 30),  # Vol-Adjusted DCA
        ]

        results = []
        for s in strategies:
            self.results[s['name']] = s
            metrics = self.calculate_metrics(s)
            results.append(metrics)

            print(f"\n{s['name']:35s} | Return: {metrics['Return (%)']:>10.2f}% | Trades: {metrics['Trades']:>3d}")

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
