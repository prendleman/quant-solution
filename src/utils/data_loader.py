"""
Data loading utilities for fetching market data from various sources.
"""

import pandas as pd
import yfinance as yf
from typing import List, Optional
from datetime import datetime


class DataLoader:
    """Load financial data from multiple sources."""
    
    def __init__(self, source: str = 'yfinance'):
        """
        Initialize data loader.
        
        Args:
            source: Data source ('yfinance', 'alpha_vantage')
        """
        self.source = source
    
    def fetch_data(self, 
                   symbol: str, 
                   start: str, 
                   end: str,
                   interval: str = '1d') -> pd.DataFrame:
        """
        Fetch historical price data.
        
        Args:
            symbol: Stock ticker symbol
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            interval: Data interval ('1d', '1h', '1m')
            
        Returns:
            DataFrame with OHLCV data
        """
        if self.source == 'yfinance':
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start, end=end, interval=interval)
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            return data
        else:
            raise ValueError(f"Unsupported data source: {self.source}")
    
    def fetch_multiple(self, 
                      symbols: List[str], 
                      start: str, 
                      end: str) -> pd.DataFrame:
        """
        Fetch data for multiple symbols.
        
        Args:
            symbols: List of ticker symbols
            start: Start date
            end: End date
            
        Returns:
            DataFrame with multi-index columns
        """
        data_dict = {}
        for symbol in symbols:
            data_dict[symbol] = self.fetch_data(symbol, start, end)
        
        return pd.concat(data_dict, axis=1)

