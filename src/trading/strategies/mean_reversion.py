"""
Mean reversion trading strategy.
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using z-score."""
    
    def __init__(self, 
                 lookback: int = 20,
                 threshold: float = 2.0,
                 exit_threshold: float = 0.5):
        """
        Initialize mean reversion strategy.
        
        Args:
            lookback: Lookback period for moving average
            threshold: Z-score threshold for entry
            exit_threshold: Z-score threshold for exit
        """
        super().__init__("Mean Reversion")
        self.lookback = lookback
        self.threshold = threshold
        self.exit_threshold = exit_threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate mean reversion signals.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Series of signals
        """
        prices = data['close'] if 'close' in data.columns else data.iloc[:, 0]
        
        # Calculate moving average and standard deviation
        ma = prices.rolling(window=self.lookback).mean()
        std = prices.rolling(window=self.lookback).std()
        
        # Calculate z-score
        z_score = (prices - ma) / std
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[z_score < -self.threshold] = 1  # Buy when oversold
        signals[z_score > self.threshold] = -1   # Sell when overbought
        signals[(z_score.abs() < self.exit_threshold) & (signals.shift(1) != 0)] = 0  # Exit
        
        self.signals = signals
        return signals
    
    def calculate_position_size(self, 
                               signal: float, 
                               price: float,
                               portfolio_value: float,
                               risk_per_trade: float = 0.02) -> int:
        """
        Calculate position size based on risk.
        
        Args:
            signal: Trading signal
            price: Current price
            portfolio_value: Total portfolio value
            risk_per_trade: Risk per trade as fraction
            
        Returns:
            Number of shares
        """
        if signal == 0:
            return 0
        
        risk_amount = portfolio_value * risk_per_trade
        # Assume 2% stop loss
        stop_loss_pct = 0.02
        position_size = int(risk_amount / (price * stop_loss_pct))
        
        return position_size if signal > 0 else -position_size
    
    def get_parameters(self) -> dict:
        """Get strategy parameters."""
        params = super().get_parameters()
        params.update({
            'lookback': self.lookback,
            'threshold': self.threshold,
            'exit_threshold': self.exit_threshold
        })
        return params

