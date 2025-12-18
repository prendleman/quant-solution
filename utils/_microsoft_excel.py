"""
Module: portfolio_quant_analysis

This module provides functions for quantitative analysis of a finance portfolio using Microsoft Excel.
"""

import pandas as pd
import xlwings as xw

def load_portfolio_data(file_path: str) -> pd.DataFrame:
    """
    Load portfolio data from an Excel file.

    Args:
    file_path (str): Path to the Excel file containing portfolio data.

    Returns:
    pd.DataFrame: DataFrame containing the portfolio data.
    """
    try:
        portfolio_data = pd.read_excel(file_path)
        return portfolio_data
    except Exception as e:
        print(f"Error loading portfolio data: {e}")

def calculate_portfolio_performance(portfolio_data: pd.DataFrame) -> float:
    """
    Calculate the overall performance of the portfolio.

    Args:
    portfolio_data (pd.DataFrame): DataFrame containing the portfolio data.

    Returns:
    float: Overall performance of the portfolio.
    """
    try:
        performance = portfolio_data['Returns'].sum()
        return performance
    except Exception as e:
        print(f"Error calculating portfolio performance: {e}")

if __name__ == "__main__":
    file_path = "portfolio_data.xlsx"
    portfolio_data = load_portfolio_data(file_path)
    
    if portfolio_data is not None:
        overall_performance = calculate_portfolio_performance(portfolio_data)
        print(f"Overall portfolio performance: {overall_performance}")