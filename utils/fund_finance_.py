"""
Module: fund_finance_implementation

This module contains functions related to fund finance implementation for a quantitative finance portfolio.

Functions:
- calculate_nav: Calculate the Net Asset Value (NAV) of a fund
- calculate_irr: Calculate the Internal Rate of Return (IRR) of a fund
- calculate_moc: Calculate the Multiple on Capital (MOC) of a fund
"""

from typing import List
import numpy as np
import pandas as pd
import numpy_financial as npf

def calculate_nav(investments: List[float], distributions: List[float]) -> float:
    """
    Calculate the Net Asset Value (NAV) of a fund.

    Parameters:
    investments (List[float]): List of investment amounts
    distributions (List[float]): List of distribution amounts

    Returns:
    float: Net Asset Value (NAV) of the fund
    """
    total_investments = sum(investments)
    total_distributions = sum(distributions)
    nav = total_investments - total_distributions
    return nav

def calculate_irr(cash_flows: List[float]) -> float:
    """
    Calculate the Internal Rate of Return (IRR) of a fund.

    Parameters:
    cash_flows (List[float]): List of cash flows

    Returns:
    float: Internal Rate of Return (IRR) of the fund
    """
    irr = npf.irr(cash_flows)
    return irr

def calculate_moc(total_distributions: float, total_contributions: float) -> float:
    """
    Calculate the Multiple on Capital (MOC) of a fund.

    Parameters:
    total_distributions (float): Total distribution amount
    total_contributions (float): Total contribution amount

    Returns:
    float: Multiple on Capital (MOC) of the fund
    """
    moc = total_distributions / total_contributions
    return moc

if __name__ == "__main__":
    investments = [100000, 150000, 200000]
    distributions = [50000, 75000, 100000]
    cash_flows = [-100000, 20000, 30000, 40000, 50000]
    total_contributions = sum(investments)
    total_distributions = sum(distributions)

    nav = calculate_nav(investments, distributions)
    irr = calculate_irr(cash_flows)
    moc = calculate_moc(total_distributions, total_contributions)

    print(f"Net Asset Value (NAV): {nav}")
    print(f"Internal Rate of Return (IRR): {irr}")
    print(f"Multiple on Capital (MOC): {moc}")