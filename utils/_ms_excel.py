"""
Module: excel_portfolio_management

This module contains functions for managing a quantitative finance portfolio using MS Excel.
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
        raise Exception(f"Error loading portfolio data: {str(e)}")

def update_portfolio_data(file_path: str, new_data: pd.DataFrame):
    """
    Update portfolio data in an Excel file.

    Args:
    file_path (str): Path to the Excel file containing portfolio data.
    new_data (pd.DataFrame): DataFrame containing the new portfolio data.
    """
    try:
        wb = xw.Book(file_path)
        sheet = wb.sheets[0]
        sheet.clear()
        sheet.range('A1').value = new_data
        wb.save()
        wb.close()
    except Exception as e:
        raise Exception(f"Error updating portfolio data: {str(e)}")

if __name__ == "__main__":
    file_path = "portfolio_data.xlsx"
    
    # Load portfolio data
    portfolio_data = load_portfolio_data(file_path)
    print("Portfolio Data:")
    print(portfolio_data)
    
    # Update portfolio data
    new_data = pd.DataFrame({'Symbol': ['AAPL', 'GOOGL'], 'Quantity': [100, 50]})
    update_portfolio_data(file_path, new_data)
    print("Portfolio Data Updated Successfully.")