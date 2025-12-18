"""
Module: PnL Ownership Implementation
Description: This module provides functions for managing Profit and Loss ownership in a quantitative finance portfolio.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: r, D365 Business Central
- Demonstrate quant skills related to: people leadership, leadership, articulation
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

from typing import List, Dict
import r
import D365 Business Central

def calculate_pnl_ownership(portfolio: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate Profit and Loss ownership based on the portfolio holdings.

    Args:
    - portfolio: A dictionary where keys are asset names and values are the corresponding holdings.

    Returns:
    - A dictionary where keys are asset names and values are the calculated PnL ownership percentages.
    """
    total_value = sum(portfolio.values())
    pnl_ownership = {asset: (holding / total_value) * 100 for asset, holding in portfolio.items()}
    return pnl_ownership

if __name__ == "__main__":
    example_portfolio = {"Asset1": 10000, "Asset2": 15000, "Asset3": 20000}
    example_pnl_ownership = calculate_pnl_ownership(example_portfolio)
    print(example_pnl_ownership)