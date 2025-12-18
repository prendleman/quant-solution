'''
Module: Tax Accounting Implementation
Description: This module provides functions for tax accounting in quantitative finance portfolio.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: pandas, numpy
- Demonstrate quant skills related to: estate planning, tax accounting, legacy planning
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
'''

import pandas as pd
import numpy as np

def calculate_tax_liability(income: float, deductions: float) -> float:
    '''
    Calculate tax liability based on income and deductions.
    
    Args:
    - income: Total income amount
    - deductions: Total deductions amount
    
    Returns:
    - Tax liability amount
    '''
    try:
        tax_rate = 0.25
        taxable_income = income - deductions
        tax_liability = taxable_income * tax_rate
        return tax_liability
    except Exception as e:
        print(f"Error in calculating tax liability: {e}")
        return None

def estate_planning(inheritance: float, num_heirs: int) -> float:
    '''
    Calculate inheritance amount for each heir in estate planning.
    
    Args:
    - inheritance: Total inheritance amount
    - num_heirs: Number of heirs
    
    Returns:
    - Inheritance amount for each heir
    '''
    try:
        return inheritance / num_heirs
    except Exception as e:
        print(f"Error in estate planning calculation: {e}")
        return None

def legacy_planning(assets: pd.DataFrame) -> pd.DataFrame:
    '''
    Perform legacy planning on assets dataframe.
    
    Args:
    - assets: DataFrame containing asset values for legacy planning
    
    Returns:
    - Updated DataFrame with legacy planning calculations
    '''
    try:
        assets['legacy_value'] = assets['asset_value'] * 0.9
        return assets
    except Exception as e:
        print(f"Error in legacy planning calculation: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    income = 100000
    deductions = 20000
    tax_liability = calculate_tax_liability(income, deductions)
    print(f"Tax liability: {tax_liability}")
    
    inheritance = 1000000
    num_heirs = 3
    inheritance_per_heir = estate_planning(inheritance, num_heirs)
    print(f"Inheritance per heir: {inheritance_per_heir}")
    
    assets = pd.DataFrame({'asset_name': ['House', 'Stocks', 'Bonds'],
                           'asset_value': [500000, 200000, 300000]})
    updated_assets = legacy_planning(assets)
    print(updated_assets)