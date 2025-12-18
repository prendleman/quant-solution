"""
Module: BI_platforms_portfolio

This module contains functions for implementing a quantitative finance portfolio using BI platforms.

Requirements:
- Must be generic for a quantitative finance portfolio
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: BI platforms, sql, power bi, tableau, python
- Demonstrate quant skills related to: data analysis, problem-solving, communication
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pyodbc

def connect_to_database(server: str, database: str, username: str, password: str) -> pyodbc.Connection:
    """
    Connect to a SQL database using pyodbc.

    Args:
    server: str - the server name
    database: str - the database name
    username: str - the username for authentication
    password: str - the password for authentication

    Returns:
    pyodbc.Connection: a connection object to the database
    """
    conn_str = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    return conn

def fetch_data_from_database(conn: pyodbc.Connection, query: str) -> pd.DataFrame:
    """
    Fetch data from a SQL database using a given query.

    Args:
    conn: pyodbc.Connection - the connection object to the database
    query: str - the SQL query to fetch data

    Returns:
    pd.DataFrame: a DataFrame containing the fetched data
    """
    data = pd.read_sql(query, conn)
    return data

def visualize_data(data: pd.DataFrame):
    """
    Visualize the data using seaborn.

    Args:
    data: pd.DataFrame - the data to visualize
    """
    sns.pairplot(data)
    plt.show()

if __name__ == "__main__":
    # Example usage
    server = 'localhost'
    database = 'quant_portfolio'
    username = 'user'
    password = 'password'
    query = 'SELECT * FROM portfolio_data'

    conn = connect_to_database(server, database, username, password)
    portfolio_data = fetch_data_from_database(conn, query)
    visualize_data(portfolio_data)