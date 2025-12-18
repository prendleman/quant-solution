"""
Module: Market Microstructure Algorithm Implementation

This module contains functions for implementing market microstructure algorithms in a quantitative finance portfolio.

Requirements:
- Python 3.6+
- Libraries: pandas, numpy, scipy

Author: Anonymous
"""

import pandas as pd
import numpy as np
from scipy import stats

def calculate_volume_weighted_average_price(data: pd.DataFrame) -> float:
    """
    Calculate the volume-weighted average price (VWAP) for a given dataset.

    Args:
    data (pd.DataFrame): DataFrame containing 'price' and 'volume' columns

    Returns:
    float: Volume-weighted average price
    """
    if 'price' not in data.columns or 'volume' not in data.columns:
        raise ValueError("Input data must contain 'price' and 'volume' columns")

    total_volume = data['volume'].sum()
    vwap = (data['price'] * data['volume']).sum() / total_volume

    return vwap

def calculate_bid_ask_spread(data: pd.DataFrame) -> float:
    """
    Calculate the bid-ask spread for a given dataset.

    Args:
    data (pd.DataFrame): DataFrame containing 'bid' and 'ask' columns

    Returns:
    float: Bid-ask spread
    """
    if 'bid' not in data.columns or 'ask' not in data.columns:
        raise ValueError("Input data must contain 'bid' and 'ask' columns")

    bid_ask_spread = data['ask'].mean() - data['bid'].mean()

    return bid_ask_spread

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({'price': [100, 101, 102, 103],
                         'volume': [1000, 2000, 1500, 3000]})
    
    vwap = calculate_volume_weighted_average_price(data)
    print(f"Volume-weighted average price: {vwap}")
    
    data = pd.DataFrame({'bid': [99.5, 100, 100.5],
                         'ask': [100.5, 101, 101.5]})
    
    spread = calculate_bid_ask_spread(data)
    print(f"Bid-ask spread: {spread}")