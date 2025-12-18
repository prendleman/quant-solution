"""
Module: sst_portfolio

This module implements a quantitative finance portfolio using Solid-State Transformers (SST) and Battery Energy Storage Systems (BESS).

Requirements:
- Advanced power-conversion platforms
- SST technology
- BESS integration
- Quant skills in market development, commercial strategy, strategic partnerships

Example usage:
    # Create a portfolio with SST and BESS
    portfolio = Portfolio()
    portfolio.add_asset(SST('SST1', 1000000, '2023-01-01'))
    portfolio.add_asset(BESS('BESS1', 500000, '2023-01-01'))

    # Calculate portfolio value
    portfolio_value = portfolio.calculate_portfolio_value()
    print(f"Portfolio Value: ${portfolio_value}")
"""

from typing import List

class Asset:
    def __init__(self, name: str, value: float, start_date: str):
        self.name = name
        self.value = value
        self.start_date = start_date

    def __str__(self):
        return f"{self.name} - Value: ${self.value} - Start Date: {self.start_date}"

class SST(Asset):
    def __init__(self, name: str, value: float, start_date: str):
        super().__init__(name, value, start_date)

class BESS(Asset):
    def __init__(self, name: str, value: float, start_date: str):
        super().__init__(name, value, start_date)

class Portfolio:
    def __init__(self):
        self.assets = []

    def add_asset(self, asset: Asset):
        self.assets.append(asset)

    def calculate_portfolio_value(self) -> float:
        return sum(asset.value for asset in self.assets)

if __name__ == "__main__":
    portfolio = Portfolio()
    portfolio.add_asset(SST('SST1', 1000000, '2023-01-01'))
    portfolio.add_asset(BESS('BESS1', 500000, '2023-01-01'))

    portfolio_value = portfolio.calculate_portfolio_value()
    print(f"Portfolio Value: ${portfolio_value}")