"""
Module: Regression Testing Implementation
Description: This module provides functions for regression testing in a quantitative finance portfolio.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def run_regression_test(data: pd.DataFrame) -> float:
    """
    Run regression test on the given data.
    
    Parameters:
    data (pd.DataFrame): Input data for regression testing
    
    Returns:
    float: Mean squared error of the regression model
    """
    X = data.drop(columns=['target'])
    y = data['target']
    
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    
    return mean_squared_error(y, y_pred)

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [2, 3, 4, 5, 6],
        'target': [3, 4, 5, 6, 7]
    })
    
    mse = run_regression_test(data)
    print(f"Mean Squared Error: {mse}")