"""
Module: digital_product_portfolio

This module implements a digital product portfolio for quantitative finance. It includes functions for analyzing and optimizing the portfolio using machine learning and product strategy techniques.

Requirements:
- Python 3.6+
- Libraries: numpy, pandas, scikit-learn, matplotlib
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def optimize_portfolio(data: pd.DataFrame, target_return: float) -> pd.DataFrame:
    """
    Optimize the portfolio allocation based on the target return using linear regression.

    Args:
    - data: DataFrame with historical returns of assets
    - target_return: Target return for the portfolio

    Returns:
    - DataFrame with optimized portfolio allocation
    """
    X = data.drop('Date', axis=1)
    y = data['Return']

    model = LinearRegression()
    model.fit(X, y)

    weights = model.coef_ / np.sum(model.coef_)
    return pd.DataFrame({'Asset': X.columns, 'Weight': weights})

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'Date': ['2022-01-01', '2022-01-02', '2022-01-03'],
        'Asset1': [0.01, 0.02, 0.03],
        'Asset2': [0.02, 0.03, 0.04],
        'Return': [0.015, 0.025, 0.035]
    })

    target_return = 0.03
    optimized_portfolio = optimize_portfolio(data, target_return)
    print(optimized_portfolio)