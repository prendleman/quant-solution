"""
Module: data_science_portfolio

This module contains functions for implementing data science in a quantitative finance portfolio.

Requirements:
- Utilizes data science techniques for portfolio analysis
- Handles data from SQL databases, R scripts, and Kafka streams
- Demonstrates quantitative skills for operating and strategizing in finance
"""

import pandas as pd
import numpy as np
import sqlalchemy
from kafka import KafkaConsumer
from rpy2 import robjects
from typing import List, Dict, Any

def fetch_data_from_sql(sql_query: str, connection_str: str) -> pd.DataFrame:
    """
    Fetches data from a SQL database using the provided query and connection string.

    Args:
    - sql_query: SQL query to fetch data
    - connection_str: Connection string to the SQL database

    Returns:
    - Pandas DataFrame containing the fetched data
    """
    try:
        engine = sqlalchemy.create_engine(connection_str)
        data = pd.read_sql(sql_query, engine)
        return data
    except Exception as e:
        raise Exception(f"Error fetching data from SQL: {str(e)}")

def run_r_script(r_script_path: str, args: List[Any]) -> Any:
    """
    Runs an R script with the provided arguments.

    Args:
    - r_script_path: Path to the R script
    - args: List of arguments to pass to the R script

    Returns:
    - Result of running the R script
    """
    try:
        r = robjects.r
        r.source(r_script_path)
        result = r.function_name(*args)
        return result
    except Exception as e:
        raise Exception(f"Error running R script: {str(e)}")

def consume_kafka_stream(topic: str) -> List[Dict[str, Any]]:
    """
    Consumes messages from a Kafka stream with the provided topic.

    Args:
    - topic: Kafka topic to consume messages from

    Returns:
    - List of dictionaries containing the consumed messages
    """
    try:
        consumer = KafkaConsumer(topic)
        messages = []
        for message in consumer:
            messages.append(message.value)
        return messages
    except Exception as e:
        raise Exception(f"Error consuming Kafka stream: {str(e)}")

if __name__ == "__main__":
    # Example usage
    sql_query = "SELECT * FROM portfolio_data"
    connection_str = "postgresql://user:password@localhost:5432/database"
    data = fetch_data_from_sql(sql_query, connection_str)
    
    r_script_path = "path/to/script.R"
    args = [1, 2, 3]
    result = run_r_script(r_script_path, args)
    
    kafka_topic = "portfolio_updates"
    messages = consume_kafka_stream(kafka_topic)
    print(messages)