"""
Pairs trading strategy.
"""

import pandas as pd
import numpy as np
from scipy.stats import linregress
from .base_strategy import BaseStrategy


class PairsTradingStrategy(BaseStrategy):
    """Pairs trading strategy using cointegration."""
    
    def __init__(self, 
                 lookback: int = 60,
                 entry_threshold: float = 2.0,
                 exit_threshold: float = 0.5):
        """
        Initialize pairs trading strategy.
        
        Args:
            lookback: Lookback period for spread calculation
            entry_threshold: Z-score threshold for entry
            exit_threshold: Z-score threshold for exit
        """
        super().__init__("Pairs Trading")
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.hedge_ratio = None
    
    def _calculate_hedge_ratio(self, price1: pd.Series, price2: pd.Series) -> float:
        """Calculate hedge ratio using linear regression."""
        result = linregress(price1.values, price2.values)
        return result.slope
    
    def _calculate_spread(self, price1: pd.Series, price2: pd.Series) -> pd.Series:
        """Calculate spread between two prices."""
        if self.hedge_ratio is None:
            self.hedge_ratio = self._calculate_hedge_ratio(price1, price2)
        return price1 - self.hedge_ratio * price2
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate pairs trading signals.
        
        Args:
            data: DataFrame with two price series
            
        Returns:
            Series of signals (1 = long spread, -1 = short spread)
        """
        if data.shape[1] < 2:
            raise ValueError("Pairs trading requires at least 2 price series")
        
        price1 = data.iloc[:, 0]
        price2 = data.iloc[:, 1]
        
        # Calculate spread
        spread = self._calculate_spread(price1, price2)
        
        # Calculate z-score of spread
        spread_ma = spread.rolling(window=self.lookback).mean()
        spread_std = spread.rolling(window=self.lookback).std()
        z_score = (spread - spread_ma) / spread_std
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[z_score < -self.entry_threshold] = 1   # Long spread (buy asset1, sell asset2)
        signals[z_score > self.entry_threshold] = -1    # Short spread (sell asset1, buy asset2)
        signals[z_score.abs() < self.exit_threshold] = 0  # Exit
        
        self.signals = signals
        return signals
    
    def calculate_position_size(self, 
                               signal: float, 
                               price: float,
                               portfolio_value: float,
                               risk_per_trade: float = 0.02) -> int:
        """Calculate position size for pairs trade."""
        if signal == 0:
            return 0
        
        # For pairs trading, split capital between two positions
        risk_amount = portfolio_value * risk_per_trade / 2
        stop_loss_pct = 0.02
        position_size = int(risk_amount / (price * stop_loss_pct))
        
        return position_size if signal > 0 else -position_size
    
    def get_parameters(self) -> dict:
        """Get strategy parameters."""
        params = super().get_parameters()
        params.update({
            'lookback': self.lookback,
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
            'hedge_ratio': self.hedge_ratio
        })
        return params

