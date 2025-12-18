"""
Module: Stressed Var algorithm implementation

This module contains a professional Python implementation of the Stressed Var algorithm for a quantitative finance portfolio.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: R, VBA, sql, c++, C#
- Demonstrate quant skills related to: financial markets knowledge, quantitative analysis, risk management
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

from typing import List, Dict
import numpy as np

def stressed_var(returns: List[float], confidence_level: float, stress_factor: float) -> float:
    """
    Calculate the Stressed Value at Risk (VaR) for a given portfolio.

    Args:
    - returns: List of historical returns for the portfolio
    - confidence_level: Confidence level for VaR calculation (e.g. 0.95 for 95% confidence)
    - stress_factor: Factor to stress the returns by

    Returns:
    - Stressed VaR value for the portfolio
    """
    if not returns:
        raise ValueError("Empty list of returns provided")

    returns = np.array(returns)
    stressed_returns = returns * stress_factor
    sorted_returns = np.sort(stressed_returns)
    var_index = int(np.floor((1 - confidence_level) * len(sorted_returns)))
    var = sorted_returns[var_index]
    
    return var

if __name__ == "__main__":
    portfolio_returns = [0.01, -0.02, 0.03, -0.01, 0.02]
    confidence_level = 0.95
    stress_factor = 2.0

    var = stressed_var(portfolio_returns, confidence_level, stress_factor)
    print(f"Stressed VaR for the portfolio: {var}")