"""
Pytest configuration and shared fixtures.
"""

import pytest
import numpy as np
import pandas as pd


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    return pd.Series(prices, index=dates, name='Close')


@pytest.fixture
def sample_returns_data():
    """Create sample returns data for testing."""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    returns = pd.Series(np.random.randn(100) * 0.01, index=dates, name='Returns')
    return returns


@pytest.fixture
def sample_returns_dataframe():
    """Create sample returns DataFrame for testing."""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    returns = pd.DataFrame({
        'Asset1': np.random.randn(100) * 0.01,
        'Asset2': np.random.randn(100) * 0.015,
        'Asset3': np.random.randn(100) * 0.02,
    }, index=dates)
    return returns
