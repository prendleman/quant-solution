"""
Unit tests for portfolio optimization module.
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.portfolio_optimization import (
    mean_variance_optimization,
    risk_parity_optimization,
    minimum_variance_portfolio,
    efficient_frontier
)


class TestPortfolioOptimization:
    """Test suite for portfolio optimization functions."""
    
    @pytest.fixture
    def sample_returns(self):
        """Create sample returns data."""
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        np.random.seed(42)
        returns = pd.DataFrame({
            'Asset1': np.random.randn(100) * 0.01,
            'Asset2': np.random.randn(100) * 0.015,
            'Asset3': np.random.randn(100) * 0.02,
        }, index=dates)
        return returns
    
    def test_mean_variance_optimization(self, sample_returns):
        """Test mean-variance optimization."""
        result = mean_variance_optimization(sample_returns, risk_free_rate=0.02)
        
        # Check result structure
        assert 'weights' in result
        assert 'expected_return' in result
        assert 'volatility' in result
        assert 'sharpe_ratio' in result
        
        # Weights should sum to 1
        assert abs(result['weights'].sum() - 1.0) < 1e-6
        
        # All weights should be non-negative (long-only)
        assert (result['weights'] >= 0).all()
        
        # Sharpe ratio should be reasonable
        assert result['sharpe_ratio'] > -10  # Not too negative
    
    def test_risk_parity_optimization(self, sample_returns):
        """Test risk parity optimization."""
        result = risk_parity_optimization(sample_returns)
        
        # Check result structure
        assert 'weights' in result
        assert 'expected_return' in result
        assert 'volatility' in result
        
        # Weights should sum to 1
        assert abs(result['weights'].sum() - 1.0) < 1e-6
        
        # All weights should be non-negative
        assert (result['weights'] >= 0).all()
    
    def test_minimum_variance_portfolio(self, sample_returns):
        """Test minimum variance portfolio."""
        result = minimum_variance_portfolio(sample_returns)
        
        # Check result structure
        assert 'weights' in result
        assert 'expected_return' in result
        assert 'volatility' in result
        
        # Weights should sum to 1
        assert abs(result['weights'].sum() - 1.0) < 1e-6
        
        # All weights should be non-negative
        assert (result['weights'] >= 0).all()
        
        # Volatility should be positive
        assert result['volatility'] > 0
    
    def test_efficient_frontier(self, sample_returns):
        """Test efficient frontier generation."""
        frontier = efficient_frontier(sample_returns, n_points=10)
        
        # Should return a DataFrame
        assert isinstance(frontier, pd.DataFrame)
        
        # Should have expected columns
        assert 'return' in frontier.columns
        assert 'volatility' in frontier.columns
        
        # Should have n_points rows
        assert len(frontier) == 10
        
        # Returns should be increasing
        assert frontier['return'].is_monotonic_increasing or frontier['return'].is_monotonic_decreasing
        
        # Volatilities should be positive
        assert (frontier['volatility'] > 0).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
