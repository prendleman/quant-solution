"""
Module: nwp_portfolio_analysis

This module contains functions for analyzing a quantitative finance portfolio using Numerical Weather Prediction (NWP) data.
"""

from typing import List, Dict
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def calculate_portfolio_performance(portfolio_data: pd.DataFrame, nwp_data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate the performance of the portfolio using NWP data.

    Args:
    - portfolio_data: DataFrame containing historical portfolio data
    - nwp_data: DataFrame containing NWP data

    Returns:
    - Dictionary with performance metrics
    """
    # Merge portfolio and NWP data on common date column
    merged_data = pd.merge(portfolio_data, nwp_data, on='date')

    # Perform linear regression to predict portfolio returns based on NWP features
    X = merged_data.drop(columns=['date', 'portfolio_return'])
    y = merged_data['portfolio_return']

    model = LinearRegression()
    model.fit(X, y)

    predicted_returns = model.predict(X)

    # Calculate mean squared error
    mse = mean_squared_error(y, predicted_returns)

    return {'mean_squared_error': mse}

if __name__ == "__main__":
    # Example usage
    portfolio_data = pd.DataFrame({'date': ['2022-01-01', '2022-01-02'],
                                   'portfolio_return': [0.02, 0.01]})
    nwp_data = pd.DataFrame({'date': ['2022-01-01', '2022-01-02'],
                             'temperature': [25, 26],
                             'humidity': [0.5, 0.6]})

    performance_metrics = calculate_portfolio_performance(portfolio_data, nwp_data)
    print(performance_metrics)