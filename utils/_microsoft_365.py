"""
Module: microsoft_365_portfolio

This module provides functions for managing a quantitative finance portfolio using Microsoft 365.

Requirements:
- Quantitative finance portfolio
- Generic implementation
- Proper docstrings, type hints, and error handling
- Libraries: Microsoft 365, sql, AI, r, Aptify
- Quant skills: communication, data analysis
- Production-ready code

Example usage:
    # Initialize portfolio
    portfolio = Portfolio()
    
    # Add a new asset
    portfolio.add_asset('AAPL', 100, 150.0)
    
    # Update asset price
    portfolio.update_asset_price('AAPL', 160.0)
    
    # Calculate portfolio value
    value = portfolio.calculate_portfolio_value()
    print(f'Portfolio value: {value}')
"""

from typing import Dict

class Portfolio:
    def __init__(self):
        self.assets: Dict[str, Tuple[int, float]] = {}
    
    def add_asset(self, symbol: str, quantity: int, price: float) -> None:
        """Add a new asset to the portfolio."""
        self.assets[symbol] = (quantity, price)
    
    def update_asset_price(self, symbol: str, price: float) -> None:
        """Update the price of an existing asset."""
        if symbol in self.assets:
            quantity, _ = self.assets[symbol]
            self.assets[symbol] = (quantity, price)
        else:
            raise ValueError(f'Asset {symbol} not found in portfolio.')
    
    def calculate_portfolio_value(self) -> float:
        """Calculate the total value of the portfolio."""
        total_value = 0.0
        for symbol, (quantity, price) in self.assets.items():
            total_value += quantity * price
        return total_value

if __name__ == '__main__':
    # Initialize portfolio
    portfolio = Portfolio()
    
    # Add a new asset
    portfolio.add_asset('AAPL', 100, 150.0)
    
    # Update asset price
    portfolio.update_asset_price('AAPL', 160.0)
    
    # Calculate portfolio value
    value = portfolio.calculate_portfolio_value()
    print(f'Portfolio value: {value}')