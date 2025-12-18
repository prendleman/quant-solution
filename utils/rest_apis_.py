"""
Module: rest_apis_implementation
Description: This module provides a professional Python implementation for Rest APIs in a quantitative finance portfolio.
"""

from typing import List, Dict
import requests

class RestAPIs:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_data(self, endpoint: str, params: Dict[str, str]) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return []

if __name__ == "__main__":
    base_url = "https://api.quantitativefinance.com"
    rest_api = RestAPIs(base_url)
    
    endpoint = "portfolio"
    params = {"user_id": "12345"}
    data = rest_api.get_data(endpoint, params)
    print(data)