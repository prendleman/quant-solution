"""
Module: portfolio_quant_analysis

This module contains functions for quantitative analysis of a finance portfolio using SQL Server.
"""

import pyodbc
import numpy as np

def fetch_data_from_sql_server(server: str, database: str, query: str) -> np.ndarray:
    """
    Fetches data from SQL Server using the provided query.
    
    Args:
    server: str - the server name
    database: str - the database name
    query: str - the SQL query to execute
    
    Returns:
    np.ndarray - a numpy array containing the fetched data
    """
    try:
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection=yes;')
        cursor = conn.cursor()
        cursor.execute(query)
        data = np.array(cursor.fetchall())
        conn.close()
        return data
    except pyodbc.Error as e:
        print(f"Error fetching data from SQL Server: {e}")
        return np.array([])

def clean_data(data: np.ndarray) -> np.ndarray:
    """
    Cleans the fetched data by removing any null values or duplicates.
    
    Args:
    data: np.ndarray - the data to clean
    
    Returns:
    np.ndarray - the cleaned data
    """
    cleaned_data = np.unique(data[~np.isnan(data).any(axis=1)], axis=0)
    return cleaned_data

if __name__ == "__main__":
    server = 'your_server_name'
    database = 'your_database_name'
    query = 'SELECT * FROM your_table'
    
    data = fetch_data_from_sql_server(server, database, query)
    cleaned_data = clean_data(data)
    
    print(cleaned_data)