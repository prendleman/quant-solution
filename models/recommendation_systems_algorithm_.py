"""
Module: Recommendation Systems Algorithm Implementation
Description: This module contains a recommendation system algorithm implementation for a quantitative finance portfolio.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: r, NLP, AI, tensorflow, ML
- Demonstrate quant skills related to: machine learning, team leadership, strategic planning
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity

def recommendation_system(data: pd.DataFrame) -> pd.DataFrame:
    """
    Implement a recommendation system algorithm using collaborative filtering.
    
    Args:
    - data: pandas DataFrame containing user-item interactions
    
    Returns:
    - recommendations: pandas DataFrame containing recommended items for each user
    """
    # Split data into train and test sets
    train_data, test_data = train_test_split(data, test_size=0.2)
    
    # Create user-item matrix
    user_item_matrix = train_data.pivot(index='user_id', columns='item_id', values='rating').fillna(0)
    
    # Calculate item-item similarity matrix using cosine similarity
    item_similarity = cosine_similarity(user_item_matrix.T)
    
    # Generate recommendations for each user
    recommendations = pd.DataFrame(index=user_item_matrix.index, columns=user_item_matrix.columns)
    
    for user_id in user_item_matrix.index:
        user_ratings = user_item_matrix.loc[user_id]
        weighted_sum = np.dot(item_similarity, user_ratings)
        normalized_sum = weighted_sum / np.sum(np.abs(item_similarity), axis=1)
        recommendations.loc[user_id] = normalized_sum
    
    return recommendations

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'user_id': [1, 1, 2, 2, 3, 3],
        'item_id': [1, 2, 2, 3, 1, 3],
        'rating': [5, 4, 3, 2, 1, 5]
    })
    
    recommendations = recommendation_system(data)
    print(recommendations)