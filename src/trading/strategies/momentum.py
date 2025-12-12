"""
Momentum trading strategy.
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """Momentum strategy using moving average crossover."""
    
    def __init__(self, 
                 short_window: int = 10,
                 long_window: int = 30,
                 rsi_period: int = 14,
                 rsi_oversold: float = 30,
                 rsi_overbought: float = 70):
        """
        Initialize momentum strategy.
        
        Args:
            short_window: Short moving average period
            long_window: Long moving average period
            rsi_period: RSI calculation period
            rsi_oversold: RSI oversold level
            rsi_overbought: RSI overbought level
        """
        super().__init__("Momentum")
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate momentum signals.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Series of signals
        """
        prices = data['close'] if 'close' in data.columns else data.iloc[:, 0]
        
        # Calculate moving averages
        short_ma = prices.rolling(window=self.short_window).mean()
        long_ma = prices.rolling(window=self.long_window).mean()
        
        # Calculate RSI
        rsi = self._calculate_rsi(prices, self.rsi_period)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy signal: short MA crosses above long MA and RSI not overbought
        buy_condition = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        buy_condition = buy_condition & (rsi < self.rsi_overbought)
        
        # Sell signal: short MA crosses below long MA and RSI not oversold
        sell_condition = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
        sell_condition = sell_condition & (rsi > self.rsi_oversold)
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        self.signals = signals
        return signals
    
    def calculate_position_size(self, 
                               signal: float, 
                               price: float,
                               portfolio_value: float,
                               risk_per_trade: float = 0.02) -> int:
        """Calculate position size."""
        if signal == 0:
            return 0
        
        risk_amount = portfolio_value * risk_per_trade
        stop_loss_pct = 0.02
        position_size = int(risk_amount / (price * stop_loss_pct))
        
        return position_size if signal > 0 else -position_size
    
    def get_parameters(self) -> dict:
        """Get strategy parameters."""
        params = super().get_parameters()
        params.update({
            'short_window': self.short_window,
            'long_window': self.long_window,
            'rsi_period': self.rsi_period
        })
        return params

