"""
Module: Graph Methods Algorithm Implementation
Description: This module contains functions for implementing graph methods algorithms for quantitative finance portfolios.
"""

import tensorflow as tf
import numpy as np
import networkx as nx

def calculate_centrality(graph: nx.Graph, centrality_type: str) -> dict:
    """
    Calculate centrality measures for nodes in a graph.

    Args:
    - graph: nx.Graph object representing the graph
    - centrality_type: str specifying the type of centrality measure to calculate

    Returns:
    - centrality_dict: dict containing node IDs as keys and centrality scores as values
    """
    if centrality_type == "degree":
        centrality_dict = nx.degree_centrality(graph)
    elif centrality_type == "betweenness":
        centrality_dict = nx.betweenness_centrality(graph)
    elif centrality_type == "closeness":
        centrality_dict = nx.closeness_centrality(graph)
    else:
        raise ValueError("Invalid centrality type. Please choose from 'degree', 'betweenness', or 'closeness'.")

    return centrality_dict

def detect_communities(graph: nx.Graph) -> list:
    """
    Detect communities in a graph using Louvain algorithm.

    Args:
    - graph: nx.Graph object representing the graph

    Returns:
    - communities: list of lists containing node IDs belonging to each community
    """
    communities = list(nx.algorithms.community.greedy_modularity_communities(graph))

    return communities

if __name__ == "__main__":
    # Example usage
    G = nx.karate_club_graph()
    
    centrality_degree = calculate_centrality(G, "degree")
    print("Degree Centrality:", centrality_degree)
    
    communities = detect_communities(G)
    print("Communities:", communities)