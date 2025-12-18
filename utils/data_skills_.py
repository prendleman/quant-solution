"""
Module: data_skills_implementation

This module contains functions for implementing data skills in a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any quantitative finance portfolio
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: pandas, numpy, scikit-learn, sqlalchemy
- Demonstrate quant skills related to: Data skills, machine learning, Analytics
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine

def extract_data_from_database(database_url: str, table_name: str) -> pd.DataFrame:
    """
    Extracts data from a database table and returns it as a pandas DataFrame.

    Args:
    database_url (str): The URL of the database
    table_name (str): The name of the table to extract data from

    Returns:
    pd.DataFrame: The extracted data
    """
    engine = create_engine(database_url)
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql(query, engine)
    return data

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the data by handling missing values and encoding categorical variables.

    Args:
    data (pd.DataFrame): The input data

    Returns:
    pd.DataFrame: The preprocessed data
    """
    # Handle missing values
    data.fillna(data.mean(), inplace=True)

    # Encode categorical variables
    data = pd.get_dummies(data)

    return data

def train_model(data: pd.DataFrame) -> RandomForestRegressor:
    """
    Trains a random forest regression model on the input data.

    Args:
    data (pd.DataFrame): The training data

    Returns:
    RandomForestRegressor: The trained model
    """
    X = data.drop('target_variable', axis=1)
    y = data['target_variable']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    return model

def evaluate_model(model: RandomForestRegressor, X_test: pd.DataFrame, y_test: pd.Series) -> float:
    """
    Evaluates the trained model on the test data using mean squared error.

    Args:
    model (RandomForestRegressor): The trained model
    X_test (pd.DataFrame): The test features
    y_test (pd.Series): The test target variable

    Returns:
    float: The mean squared error of the model
    """
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return mse

if __name__ == "__main__":
    # Example usage
    database_url = "sqlite:///data.db"
    table_name = "portfolio_data"
    data = extract_data_from_database(database_url, table_name)
    preprocessed_data = preprocess_data(data)
    model = train_model(preprocessed_data)
    mse = evaluate_model(model, X_test, y_test)
    print(f"Mean Squared Error: {mse}")