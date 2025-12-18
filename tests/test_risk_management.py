"""
Unit tests for risk management module.
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.risk_management_ import calculate_var, calculate_cvar, calculate_max_drawdown


class TestRiskManagement:
    """Test suite for risk management functions."""
    
    def test_calculate_var(self):
        """Test Value at Risk calculation."""
        # Create sample returns
        returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.005, -0.03, 0.02, -0.015])
        
        # Calculate VaR at 5% confidence level
        var_95 = calculate_var(returns, confidence_level=0.05)
        
        # VaR should be the 5th percentile
        assert var_95 <= 0
        assert var_95 == returns.quantile(0.05)
    
    def test_calculate_cvar(self):
        """Test Conditional Value at Risk calculation."""
        returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.005, -0.03, 0.02, -0.015])
        
        cvar_95 = calculate_cvar(returns, confidence_level=0.05)
        var_95 = calculate_var(returns, confidence_level=0.05)
        
        # CVaR should be less than or equal to VaR (more negative)
        assert cvar_95 <= var_95
        # CVaR should be the mean of returns below VaR
        assert abs(cvar_95 - returns[returns <= var_95].mean()) < 1e-10
    
    def test_calculate_max_drawdown(self):
        """Test maximum drawdown calculation."""
        # Create price series with known drawdown
        prices = pd.Series([100, 110, 105, 120, 90, 95, 100])
        
        max_dd = calculate_max_drawdown(prices)
        
        # Maximum drawdown should be negative
        assert max_dd < 0
        # In this case, peak is 120, trough is 90, so drawdown is (90-120)/120 = -0.25
        expected_dd = (90 - 120) / 120
        assert abs(max_dd - expected_dd) < 1e-10
    
    def test_calculate_max_drawdown_monotonic(self):
        """Test max drawdown with monotonically increasing prices."""
        prices = pd.Series([100, 110, 120, 130, 140])
        
        max_dd = calculate_max_drawdown(prices)
        
        # No drawdown, should be 0 or very close
        assert max_dd == 0.0
    
    def test_calculate_var_empty_series(self):
        """Test VaR with empty series."""
        returns = pd.Series([])
        
        with pytest.raises(ValueError):
            calculate_var(returns, confidence_level=0.05)
    
    def test_calculate_cvar_empty_series(self):
        """Test CVaR with empty series."""
        returns = pd.Series([])
        
        with pytest.raises(ValueError):
            calculate_cvar(returns, confidence_level=0.05)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
