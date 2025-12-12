"""
Event-driven backtesting engine.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from abc import ABC


class BacktestEngine:
    """Event-driven backtesting engine."""
    
    def __init__(self,
                 strategy,  # BaseStrategy type
                 initial_capital: float = 100000,
                 commission: float = 0.001,
                 slippage: float = 0.0005):
        """
        Initialize backtesting engine.
        
        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital
            commission: Commission per trade (fraction)
            slippage: Slippage per trade (fraction)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.positions = []
        self.trades = []
        self.equity_curve = pd.Series(dtype=float)
        self.returns = pd.Series(dtype=float)
    
    def run(self, data: pd.DataFrame) -> Dict:
        """
        Run backtest on historical data.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dictionary with backtest results
        """
        # Generate signals
        signals = self.strategy.generate_signals(data)
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0
        equity = [capital]
        
        prices = data['close'] if 'close' in data.columns else data.iloc[:, 0]
        
        for i in range(1, len(data)):
            current_price = prices.iloc[i]
            signal = signals.iloc[i]
            prev_signal = signals.iloc[i-1] if i > 0 else 0
            
            # Calculate position size
            if signal != prev_signal and signal != 0:
                position_size = self.strategy.calculate_position_size(
                    signal, current_price, capital
                )
                
                # Execute trade with slippage and commission
                execution_price = current_price * (1 + self.slippage * np.sign(position_size))
                trade_value = abs(position_size) * execution_price
                commission_cost = trade_value * self.commission
                
                # Update capital
                if position_size > 0:  # Buy
                    capital -= (trade_value + commission_cost)
                    position += position_size
                else:  # Sell
                    capital += (trade_value - commission_cost)
                    position += position_size  # position_size is negative
                
                self.trades.append({
                    'date': data.index[i],
                    'price': execution_price,
                    'shares': position_size,
                    'value': trade_value,
                    'commission': commission_cost
                })
            
            # Update equity
            current_value = capital + position * current_price
            equity.append(current_value)
        
        # Calculate metrics
        self.equity_curve = pd.Series(equity, index=data.index)
        self.returns = self.equity_curve.pct_change().dropna()
        
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics."""
        total_return = (self.equity_curve.iloc[-1] / self.initial_capital - 1) * 100
        annualized_return = (self.equity_curve.iloc[-1] / self.initial_capital) ** (252 / len(self.equity_curve)) - 1
        annualized_vol = self.returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0
        
        # Maximum drawdown
        running_max = self.equity_curve.expanding().max()
        drawdown = (self.equity_curve - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Win rate
        if len(self.trades) > 0:
            trade_returns = []
            for i in range(1, len(self.trades)):
                if self.trades[i]['shares'] * self.trades[i-1]['shares'] < 0:  # Position closed
                    entry_price = self.trades[i-1]['price']
                    exit_price = self.trades[i]['price']
                    trade_return = (exit_price - entry_price) / entry_price * np.sign(self.trades[i-1]['shares'])
                    trade_returns.append(trade_return)
            
            win_rate = sum(1 for r in trade_returns if r > 0) / len(trade_returns) * 100 if trade_returns else 0
        else:
            win_rate = 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return * 100,
            'annualized_volatility': annualized_vol * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(self.trades),
            'final_value': self.equity_curve.iloc[-1],
            'equity_curve': self.equity_curve,
            'returns': self.returns
        }
    
    def summary(self) -> str:
        """Get formatted summary of results."""
        metrics = self._calculate_metrics()
        return f"""
Backtest Results
================
Total Return: {metrics['total_return']:.2f}%
Annualized Return: {metrics['annualized_return']:.2f}%
Annualized Volatility: {metrics['annualized_volatility']:.2f}%
Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
Max Drawdown: {metrics['max_drawdown']:.2f}%
Win Rate: {metrics['win_rate']:.2f}%
Total Trades: {metrics['total_trades']}
Final Value: ${metrics['final_value']:,.2f}
"""

