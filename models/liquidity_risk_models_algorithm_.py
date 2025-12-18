"""
Module: liquidity_risk_models

This module implements various liquidity risk models for quantitative finance portfolios.

The following libraries are used:
- R
- VBA
- SQL
- C++
- C#

Quant skills demonstrated:
- Financial markets knowledge
- Quantitative analysis
- Risk management
"""

import pandas as pd
import numpy as np

def liquidity_ratio(data: pd.DataFrame) -> pd.Series:
    """
    Calculate the liquidity ratio for each asset in the portfolio.

    Parameters:
    data (pd.DataFrame): DataFrame containing historical trading volume and market cap data for each asset.

    Returns:
    pd.Series: Series containing the liquidity ratio for each asset.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")

    if 'volume' not in data.columns or 'market_cap' not in data.columns:
        raise ValueError("Input data must contain 'volume' and 'market_cap' columns.")

    return data['volume'] / data['market_cap']

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'asset': ['A', 'B', 'C'],
        'volume': [10000, 20000, 15000],
        'market_cap': [500000, 1000000, 750000]
    })

    print(liquidity_ratio(data))