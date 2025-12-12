"""
Base strategy class for all trading strategies.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Optional


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
        """
        self.name = name
        self.positions = {}
        self.signals = pd.Series(dtype=float)
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals from market data.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Series of signals (-1, 0, 1)
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, 
                               signal: float, 
                               price: float,
                               portfolio_value: float) -> int:
        """
        Calculate position size based on signal.
        
        Args:
            signal: Trading signal
            price: Current price
            portfolio_value: Total portfolio value
            
        Returns:
            Number of shares to trade
        """
        pass
    
    def get_parameters(self) -> Dict:
        """Get strategy parameters."""
        return {'name': self.name}

