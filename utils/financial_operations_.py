"""
Module: Financial Operations Implementation

This module contains functions for performing financial operations in a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any quantitative finance portfolio.
- Include proper docstrings, type hints, and error handling.
- Use appropriate libraries such as ERP systems, r, and NetSuite.
- Demonstrate quant skills related to product management and financial operations.
- Include example usage in the __main__ block.
- Code should be production-ready and portfolio-quality.
"""

from typing import List, Dict

def calculate_portfolio_value(portfolio: Dict[str, float]) -> float:
    """
    Calculate the total value of a portfolio.

    Args:
    - portfolio: A dictionary where keys are asset names and values are asset prices.

    Returns:
    - The total value of the portfolio.
    """
    total_value = sum(portfolio.values())
    return total_value

def update_portfolio_value(portfolio: Dict[str, float], asset: str, price: float) -> Dict[str, float]:
    """
    Update the price of a specific asset in the portfolio.

    Args:
    - portfolio: A dictionary where keys are asset names and values are asset prices.
    - asset: The name of the asset to update.
    - price: The new price of the asset.

    Returns:
    - The updated portfolio with the new asset price.
    """
    if asset in portfolio:
        portfolio[asset] = price
    else:
        raise ValueError(f"Asset '{asset}' not found in the portfolio.")
    
    return portfolio

if __name__ == "__main__":
    example_portfolio = {"AAPL": 150.0, "GOOGL": 2000.0, "MSFT": 300.0}
    
    print("Calculating portfolio value...")
    total_value = calculate_portfolio_value(example_portfolio)
    print(f"Total portfolio value: ${total_value}")
    
    print("\nUpdating asset price...")
    updated_portfolio = update_portfolio_value(example_portfolio, "AAPL", 160.0)
    print(f"Updated portfolio: {updated_portfolio}")