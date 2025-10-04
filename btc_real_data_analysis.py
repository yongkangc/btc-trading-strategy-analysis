"""
BTC Strategy Analysis with Real Data from Scry API
This script expects btc_data.json to be created first using scry:get_historical_price
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def load_btc_data_from_json(json_file: str = 'btc_data.json'):
    """Load BTC data from JSON file (from scry API)"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract unified_data
        btc_list = data.get('unified_data', data)
        
        # Convert to DataFrame
        df = pd.DataFrame(btc_list)
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"✓ Loaded {len(df)} datapoints from {json_file}")
        print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"  Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        
        return df
        
    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        print("Please create this file using the scry:get_historical_price API")
        return None


class BTCBacktest:
    """Simplified backtesting class for real BTC data"""
    
    def __init__(self, df: pd.DataFrame):
        self.data = df.copy()
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.set_index('date')
        self.data = self.data.rename(columns={'price': 'Close'})
        self.results = {}
    
    def hodl(self, capital=10000):
        """Buy and hold strategy"""
        prices = self.data['Close']
        btc = capital / prices.iloc[0]
        portfolio = btc * prices
        
        return {
            'name': 'HODL',
            'portfolio': portfolio,
            'returns': portfolio.pct_change().fillna(0),
            'trades': 1
        }
    
    def fibonacci_dip_buy(self, capital=10000, fib_level=0.382, lookback=90):
        """Buy when price hits Fibonacci support level"""
        prices = self.data['Close']
        
        # Calculate Fibonacci levels
        high = prices.rolling(lookback).max()
        low = prices.rolling(lookback).min()
        fib_support = low + (high - low) * fib_level
        
        cash = capital
        btc = 0
        trades = 0
        buy_size = capital * 0.1  # 10% per buy
        portfolio = []
        
        for i, (date, price) in enumerate(prices.items()):
            # Buy signal: price near Fibonacci support
            if i >= lookback and not pd.isna(fib_support.iloc[i]):
                if price <= fib_support.iloc[i] * 1.03 and cash >= buy_size:  # Within 3% of support
                    btc_bought = buy_size / price
                    btc += btc_bought
                    cash -= buy_size
                    trades += 1
            
            portfolio.append(cash + btc * price)
        
        portfolio_series = pd.Series(portfolio, index=prices.index)
        
        return {
            'name': f'Fib {fib_level} Buy',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }
    
    def dca(self, capital=10000, frequency=30):
        """Dollar cost averaging"""
        prices = self.data['Close']
        periods = len(prices) // frequency
        buy_amount = capital / periods if periods > 0 else capital
        
        cash = capital
        btc = 0
        trades = 0
        portfolio = []
        
        for i, (date, price) in enumerate(prices.items()):
            if i % frequency == 0 and cash >= buy_amount:
                btc += buy_amount / price
                cash -= buy_amount
                trades += 1
            
            portfolio.append(cash + btc * price)
        
        portfolio_series = pd.Series(portfolio, index=prices.index)
        
        return {
            'name': f'DCA ({frequency}d)',
            'portfolio': portfolio_series,
            'returns': portfolio_series.pct_change().fillna(0),
            'trades': trades
        }
    
    def calculate_metrics(self, result):
        """Calculate performance metrics"""
        pv = result['portfolio']
        ret = result['returns']
        
        total_return = (pv.iloc[-1] / pv.iloc[0] - 1) * 100
        
        days = (pv.index[-1] - pv.index[0]).days
        cagr = ((pv.iloc[-1] / pv.iloc[0]) ** (365 / max(days, 1)) - 1) * 100
        
        vol = ret.std() * np.sqrt(252) * 100
        sharpe = (ret.mean() * 252) / (ret.std() * np.sqrt(252)) if ret.std() > 0 else 0
        
        dd = (pv - pv.expanding().max()) / pv.expanding().max() * 100
        max_dd = dd.min()
        
        return {
            'Strategy': result['name'],
            'Return (%)': round(total_return, 2),
            'CAGR (%)': round(cagr, 2),
            'Sharpe': round(sharpe, 2),
            'Max DD (%)': round(max_dd, 2),
            'Trades': result['trades'],
            'Final ($)': round(pv.iloc[-1], 2)
        }
    
    def run_comparison(self, capital=10000):
        """Run strategy comparison"""
        strategies = [
            self.hodl(capital),
            self.fibonacci_dip_buy(capital, 0.236, 90),
            self.fibonacci_dip_buy(capital, 0.382, 90),
            self.fibonacci_dip_buy(capital, 0.5, 90),
            self.dca(capital, 7),
            self.dca(capital, 30),
        ]
        
        results = []
        for s in strategies:
            self.results[s['name']] = s
            results.append(self.calculate_metrics(s))
        
        return pd.DataFrame(results).set_index('Strategy')
    
    def create_chart(self, df_results):
        """Create comparison chart"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Portfolio Value', 'Performance Comparison'),
            column_widths=[0.6, 0.4]
        )
        
        colors = px.colors.qualitative.Plotly
        
        # Portfolio values
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
        
        # Performance bars
        sorted_df = df_results.sort_values('Return (%)', ascending=True)
        fig.add_trace(
            go.Bar(
                y=sorted_df.index,
                x=sorted_df['Return (%)'],
                orientation='h',
                marker_color=sorted_df['Return (%)'],
                marker_colorscale='RdYlGn',
                showlegend=False,
                text=[f"{x:.1f}%" for x in sorted_df['Return (%)']],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="<b>BTC Strategy Comparison (Real Data)</b>",
            template='plotly_white'
        )
        
        return fig


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("BTC TRADING STRATEGY ANALYSIS - REAL DATA")
    print("="*70)
    
    # Load data
    df = load_btc_data_from_json('btc_data.json')
    
    if df is None:
        print("\n⚠️  No data file found. Using sample data instead...")
        # Create minimal sample data
        dates = pd.date_range('2020-01-01', '2025-01-01', freq='D')
        prices = 10000 * (1 + np.random.randn(len(dates)).cumsum() * 0.02)
        df = pd.DataFrame({'date': dates, 'price': prices})
    
    # Run backtest
    bt = BTCBacktest(df)
    results = bt.run_comparison(capital=10000)
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(results.to_string())
    
    # Insights
    best = results['Return (%)'].idxmax()
    hodl_return = results.loc['HODL', 'Return (%)']
    best_return = results.loc[best, 'Return (%)']
    
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print(f"\n🏆 Best: {best} ({best_return:.1f}%)")
    print(f"📊 HODL: {hodl_return:.1f}%")
    print(f"📈 Difference: {best_return - hodl_return:+.1f}%")
    
    # Save
    fig = bt.create_chart(results)
    fig.write_html('/mnt/user-data/outputs/btc_real_data_analysis.html')
    results.to_csv('/mnt/user-data/outputs/btc_real_data_results.csv')
    
    print("\n✓ Saved: btc_real_data_analysis.html")
    print("✓ Saved: btc_real_data_results.csv")
    
    return bt, results


if __name__ == "__main__":
    bt, results = main()
