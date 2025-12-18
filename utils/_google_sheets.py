"""
Module: google_sheets_portfolio

This module provides functions for managing a quantitative finance portfolio using Google Sheets.

Requirements:
- This is for a quantitative finance portfolio
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: Google Sheets, r, Excel
- Demonstrate quant skills related to: financial modeling, analytical skills
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def authenticate_google_sheets(credentials_file: str) -> gspread.Client:
    """
    Authenticate with Google Sheets API using credentials file.

    Args:
    - credentials_file: Path to the JSON file containing Google Sheets API credentials

    Returns:
    - gspread.Client: Authenticated client object for accessing Google Sheets
    """
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Sheets API: {str(e)}")

def read_portfolio_from_google_sheets(client: gspread.Client, sheet_name: str) -> pd.DataFrame:
    """
    Read portfolio data from a Google Sheets spreadsheet.

    Args:
    - client: Authenticated client object for accessing Google Sheets
    - sheet_name: Name of the Google Sheets spreadsheet containing portfolio data

    Returns:
    - pd.DataFrame: DataFrame containing portfolio data
    """
    try:
        sheet = client.open(sheet_name).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        raise Exception(f"Failed to read portfolio data from Google Sheets: {str(e)}")

if __name__ == "__main__":
    credentials_file = "path/to/credentials.json"
    sheet_name = "PortfolioData"

    client = authenticate_google_sheets(credentials_file)
    portfolio_data = read_portfolio_from_google_sheets(client, sheet_name)
    print(portfolio_data.head())