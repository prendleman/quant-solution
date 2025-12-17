"""
Module: Profitability Management Implementation

This module provides functions for managing profitability in a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any quantitative finance portfolio
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: numpy, pandas
- Demonstrate quant skills related to flawless creative execution, delivery excellence, operational discipline
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import numpy as np
import pandas as pd

def calculate_profitability(portfolio_returns: pd.Series, capital: float) -> float:
    """
    Calculate the profitability of a portfolio based on returns and initial capital.

    Args:
    - portfolio_returns: A pandas Series containing the returns of the portfolio
    - capital: Initial capital invested in the portfolio

    Returns:
    - profitability: The profitability of the portfolio as a percentage
    """
    if not isinstance(portfolio_returns, pd.Series):
        raise TypeError("portfolio_returns must be a pandas Series")
    
    if not isinstance(capital, (int, float)):
        raise TypeError("capital must be a numeric value")
    
    if capital <= 0:
        raise ValueError("capital must be greater than 0")
    
    total_return = (portfolio_returns + 1).prod()
    final_balance = capital * total_return
    profitability = ((final_balance - capital) / capital) * 100
    
    return profitability

if __name__ == "__main__":
    returns_data = pd.Series([0.05, 0.03, -0.02, 0.04, 0.01])
    initial_capital = 1000000
    
    profitability = calculate_profitability(returns_data, initial_capital)
    print(f"Portfolio profitability: {profitability:.2f}%")