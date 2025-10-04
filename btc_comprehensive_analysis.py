"""
Comprehensive BTC Trading Strategy Comparison
Fetches data using scry API and compares HODL vs various trading strategies
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# First, let's create sample BTC data for demonstration
# In production, this would come from the scry:get_historical_price API

def create_sample_btc_data():
    """Create sample BTC data for the last 5 years"""
    print("Creating sample BTC data...")
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Simulate realistic BTC price movement
    np.random.seed(42)
    
    # Start at ~$10,000 in 2020
    initial_price = 10000
    returns = np.random.normal(0.002, 0.04, len(dates))  # 0.2% daily return, 4% volatility
    
    # Add trend and cycles
    trend = np.linspace(0, 1.5, len(dates))  # Upward trend
    cycle = np.sin(np.linspace(0, 4*np.pi, len(dates))) * 0.2
    
    # Generate prices
    log_returns = returns + trend/len(dates) + cycle/len(dates)
    prices = initial_price * np.exp(np.cumsum(log_returns))
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'price': prices,
        'volume': np.random.uniform(20e9, 100e9, len(dates)),
        'market_cap': prices * 19e6  # Approximate BTC supply
    })
    
    return df


class BTCStrategyBacktest:
    def __init__(self, data: pd.DataFrame = None):
        """Initialize with data"""
        if data is None:
            self.data = create_sample_btc_data()
        else:
            self.data = data
        
        # Set date as index
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data = self.data.set_index('date')
        
        # Add OHLC columns if not present
        if 'Close' not in self.data.columns:
            self.data = self.data.rename(columns={'price': 'Close'})
        if 'Volume' not in self.data.columns and 'volume' in self.data.columns:
            self.data = self.data.rename(columns={'volume': 'Volume'})
        
        # Add missing OHLC using Close
        for col in ['Open', 'High', 'Low']:
            if col not in self.data.columns:
                self.data[col] = self.data['Close']
        
        self.results = {}
        
    def calculate_fibonacci_levels(self, prices: pd.Series, lookback: int = 90) -> pd.DataFrame:
        """Calculate Fibonacci retracement levels"""
        fib_levels = pd.DataFrame(index=prices.index)
        
        rolling_high = prices.rolling(window=lookback).max()
        rolling_low = prices.rolling(window=lookback).min()
        diff = rolling_high - rolling_low
        
        fib_levels['0.0'] = rolling_low
        fib_levels['0.236'] = rolling_low + 0.236 * diff
        fib_levels['0.382'] = rolling_low + 0.382 * diff
        fib_levels['0.5'] = rolling_low + 0.5 * diff
        fib_levels['0.618'] = rolling_low + 0.618 * diff
        fib_levels['0.786'] = rolling_low + 0.786 * diff
        fib_levels['1.0'] = rolling_high
        
        return fib_levels
    
    def strategy_hodl(self, initial_capital: float = 10000):
        """HODL Strategy: Buy and hold"""
        prices = self.data['Close']
        entry_price = prices.iloc[0]
        btc_amount = initial_capital / entry_price
        
        portfolio_value = btc_amount * prices
        returns = portfolio_value.pct_change().fillna(0)
        
        return {
            'name': 'HODL',
            'portfolio_value': portfolio_value,
            'returns': returns,
            'trades': 1,
            'entry_price': entry_price,
            'btc_held': btc_amount
        }
    
    def strategy_fibonacci_buy(self, initial_capital: float = 10000, 
                               buy_level: float = 0.382, 
                               lookback: int = 90):
        """Buy when price touches Fibonacci support"""
        prices = self.data['Close']
        fib_levels = self.calculate_fibonacci_levels(prices, lookback)
        
        cash = initial_capital
        btc_held = 0
        portfolio_values = []
        trades = 0
        buy_amount = initial_capital * 0.1
        
        for i, (date, price) in enumerate(prices.items()):
            if i >= lookback:
                fib_buy_level = fib_levels.iloc[i][str(buy_level)]
                
                if not pd.isna(fib_buy_level):
                    if price <= fib_buy_level * 1.02 and cash >= buy_amount:
                        btc_to_buy = buy_amount / price
                        btc_held += btc_to_buy
                        cash -= buy_amount
                        trades += 1
            
            portfolio_value = cash + (btc_held * price)
            portfolio_values.append(portfolio_value)
        
        portfolio_series = pd.Series(portfolio_values, index=prices.index)
        returns = portfolio_series.pct_change().fillna(0)
        
        return {
            'name': f'Fibonacci Buy (Lvl {buy_level})',
            'portfolio_value': portfolio_series,
            'returns': returns,
            'trades': trades
        }
    
    def strategy_dca(self, initial_capital: float = 10000, frequency: int = 30):
        """Dollar Cost Averaging"""
        prices = self.data['Close']
        
        total_periods = len(prices) // frequency
        buy_amount = initial_capital / total_periods if total_periods > 0 else initial_capital
        
        cash = initial_capital
        btc_held = 0
        portfolio_values = []
        trades = 0
        
        for i, (date, price) in enumerate(prices.items()):
            if i % frequency == 0 and cash >= buy_amount:
                btc_to_buy = buy_amount / price
                btc_held += btc_to_buy
                cash -= buy_amount
                trades += 1
            
            portfolio_value = cash + (btc_held * price)
            portfolio_values.append(portfolio_value)
        
        portfolio_series = pd.Series(portfolio_values, index=prices.index)
        returns = portfolio_series.pct_change().fillna(0)
        
        return {
            'name': f'DCA (Every {frequency} days)',
            'portfolio_value': portfolio_series,
            'returns': returns,
            'trades': trades
        }
    
    def calculate_metrics(self, strategy_result):
        """Calculate performance metrics"""
        portfolio_value = strategy_result['portfolio_value']
        returns = strategy_result['returns']
        
        total_return = (portfolio_value.iloc[-1] / portfolio_value.iloc[0] - 1) * 100
        
        days = (portfolio_value.index[-1] - portfolio_value.index[0]).days
        cagr = ((portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (365 / days) - 1) * 100
        
        volatility = returns.std() * np.sqrt(252) * 100
        sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        rolling_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        
        win_rate = (returns > 0).sum() / len(returns) * 100
        
        return {
            'Total Return (%)': round(total_return, 2),
            'CAGR (%)': round(cagr, 2),
            'Volatility (%)': round(volatility, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Max Drawdown (%)': round(max_drawdown, 2),
            'Win Rate (%)': round(win_rate, 2),
            'Number of Trades': strategy_result['trades'],
            'Final Value ($)': round(portfolio_value.iloc[-1], 2)
        }
    
    def run_all_strategies(self, initial_capital: float = 10000):
        """Run all strategies"""
        print("\n" + "="*60)
        print("RUNNING ALL STRATEGIES")
        print("="*60)
        
        strategies = [
            self.strategy_hodl(initial_capital),
            self.strategy_fibonacci_buy(initial_capital, buy_level=0.236),
            self.strategy_fibonacci_buy(initial_capital, buy_level=0.382),
            self.strategy_fibonacci_buy(initial_capital, buy_level=0.5),
            self.strategy_fibonacci_buy(initial_capital, buy_level=0.618),
            self.strategy_dca(initial_capital, frequency=7),
            self.strategy_dca(initial_capital, frequency=30),
        ]
        
        results = []
        for strategy in strategies:
            metrics = self.calculate_metrics(strategy)
            metrics['Strategy'] = strategy['name']
            results.append(metrics)
            self.results[strategy['name']] = strategy
            
            print(f"\n{strategy['name']}:")
            print(f"  Final Value: ${metrics['Final Value ($)']:,.2f}")
            print(f"  Total Return: {metrics['Total Return (%)']:.2f}%")
            print(f"  Trades: {metrics['Number of Trades']}")
        
        df_results = pd.DataFrame(results)
        df_results = df_results.set_index('Strategy')
        
        return df_results
    
    def create_dashboard(self, df_results: pd.DataFrame):
        """Create interactive dashboard"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Portfolio Value Over Time',
                'Strategy Performance Comparison',
                'Returns Distribution',
                'Risk-Return Profile'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'bar'}],
                [{'type': 'box'}, {'type': 'scatter'}]
            ]
        )
        
        colors = px.colors.qualitative.Set3
        
        # 1. Portfolio Value Over Time
        for i, (strategy_name, strategy_data) in enumerate(self.results.items()):
            fig.add_trace(
                go.Scatter(
                    x=strategy_data['portfolio_value'].index,
                    y=strategy_data['portfolio_value'],
                    name=strategy_name,
                    mode='lines',
                    line=dict(width=2, color=colors[i % len(colors)])
                ),
                row=1, col=1
            )
        
        # 2. Total Return Comparison
        sorted_results = df_results.sort_values('Total Return (%)', ascending=True)
        fig.add_trace(
            go.Bar(
                y=sorted_results.index,
                x=sorted_results['Total Return (%)'],
                orientation='h',
                marker=dict(color=sorted_results['Total Return (%)'], colorscale='RdYlGn'),
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. Returns Distribution
        for i, (strategy_name, strategy_data) in enumerate(self.results.items()):
            fig.add_trace(
                go.Box(
                    y=strategy_data['returns'] * 100,
                    name=strategy_name,
                    marker_color=colors[i % len(colors)],
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # 4. Risk-Return Profile
        fig.add_trace(
            go.Scatter(
                x=df_results['Volatility (%)'],
                y=df_results['Total Return (%)'],
                mode='markers+text',
                marker=dict(size=15, color=df_results['Sharpe Ratio'], colorscale='Viridis'),
                text=df_results.index,
                textposition='top center',
                showlegend=False
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=1000,
            title_text="<b>BTC Trading Strategies Dashboard</b>",
            showlegend=True,
            template='plotly_white'
        )
        
        return fig


def main():
    """Main execution"""
    
    # Create/load BTC data
    print("="*60)
    print("BTC STRATEGY COMPARISON")
    print("="*60)
    
    # Use sample data for demonstration
    btc_data = create_sample_btc_data()
    print(f"\nData Summary:")
    print(f"  Date range: {btc_data['date'].min().date()} to {btc_data['date'].max().date()}")
    print(f"  Total days: {len(btc_data)}")
    print(f"  Price range: ${btc_data['price'].min():.2f} - ${btc_data['price'].max():.2f}")
    
    # Initialize backtest
    backtest = BTCStrategyBacktest(btc_data)
    
    # Run strategies
    df_results = backtest.run_all_strategies(initial_capital=10000)
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(df_results.to_string())
    
    # Create dashboard
    print("\n" + "="*60)
    print("GENERATING DASHBOARD")
    print("="*60)
    
    fig = backtest.create_dashboard(df_results)
    
    output_file = '/mnt/user-data/outputs/btc_strategy_dashboard.html'
    fig.write_html(output_file)
    print(f"✓ Dashboard saved")
    
    # Save results
    csv_file = '/mnt/user-data/outputs/btc_strategy_results.csv'
    df_results.to_csv(csv_file)
    print(f"✓ Results saved")
    
    # Key insights
    print("\n" + "="*60)
    print("KEY INSIGHTS")
    print("="*60)
    
    best_strategy = df_results['Total Return (%)'].idxmax()
    best_return = df_results.loc[best_strategy, 'Total Return (%)']
    hodl_return = df_results.loc['HODL', 'Total Return (%)']
    
    print(f"\n🏆 Best Strategy: {best_strategy}")
    print(f"   Return: {best_return:.2f}%")
    print(f"   Sharpe: {df_results.loc[best_strategy, 'Sharpe Ratio']:.2f}")
    
    print(f"\n📊 HODL Baseline: {hodl_return:.2f}%")
    
    outperformance = best_return - hodl_return
    if outperformance > 0:
        print(f"\n💡 {best_strategy} outperformed HODL by {outperformance:.2f}%")
    else:
        print(f"\n💡 HODL outperformed active strategies by {abs(outperformance):.2f}%")
    
    return backtest, df_results


if __name__ == "__main__":
    backtest, results = main()
