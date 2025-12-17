"""
Module: portfolio_analytics

This module contains functions for analyzing a quantitative finance portfolio using analytics software.
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
import pyodbc

def calculate_portfolio_beta(portfolio_returns: pd.DataFrame, market_returns: pd.DataFrame) -> float:
    """
    Calculate the beta of a portfolio using linear regression.
    
    Args:
    - portfolio_returns: DataFrame containing daily returns of the portfolio
    - market_returns: DataFrame containing daily returns of the market
    
    Returns:
    - beta: float value representing the beta of the portfolio
    """
    model = LinearRegression()
    model.fit(market_returns.values.reshape(-1, 1), portfolio_returns)
    beta = model.coef_[0]
    
    return beta

def fetch_portfolio_data_from_database(database: str, table: str) -> pd.DataFrame:
    """
    Fetch portfolio data from a SQL database.
    
    Args:
    - database: str representing the name of the database
    - table: str representing the name of the table containing portfolio data
    
    Returns:
    - portfolio_data: DataFrame containing portfolio data
    """
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=server_name;DATABASE=' + database)
    query = f"SELECT * FROM {table}"
    portfolio_data = pd.read_sql(query, conn)
    
    return portfolio_data

if __name__ == "__main__":
    # Example usage
    portfolio_returns = pd.DataFrame({'date': ['2022-01-01', '2022-01-02', '2022-01-03'],
                                      'return': [0.01, 0.02, -0.005]})
    
    market_returns = pd.DataFrame({'date': ['2022-01-01', '2022-01-02', '2022-01-03'],
                                    'return': [0.015, 0.025, -0.01]})
    
    beta = calculate_portfolio_beta(portfolio_returns['return'], market_returns['return'])
    print(f"Portfolio beta: {beta}")