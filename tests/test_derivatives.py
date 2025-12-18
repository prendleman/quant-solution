"""
Unit tests for derivatives pricing module.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.derivatives_ import black_scholes_price, calculate_greeks, monte_carlo_option_price


class TestDerivatives:
    """Test suite for derivatives pricing functions."""
    
    def test_black_scholes_call(self):
        """Test Black-Scholes call option pricing."""
        S = 100  # Stock price
        K = 100  # Strike price
        T = 1.0  # 1 year
        r = 0.05  # 5% risk-free rate
        sigma = 0.2  # 20% volatility
        
        price = black_scholes_price(S, K, T, r, sigma, option_type='call')
        
        # Call option should have positive value
        assert price > 0
        # At-the-money call with positive time value should be > intrinsic value
        assert price > max(S - K, 0)
    
    def test_black_scholes_put(self):
        """Test Black-Scholes put option pricing."""
        S = 100
        K = 100
        T = 1.0
        r = 0.05
        sigma = 0.2
        
        price = black_scholes_price(S, K, T, r, sigma, option_type='put')
        
        # Put option should have positive value
        assert price > 0
    
    def test_black_scholes_put_call_parity(self):
        """Test put-call parity."""
        S = 100
        K = 100
        T = 1.0
        r = 0.05
        sigma = 0.2
        
        call_price = black_scholes_price(S, K, T, r, sigma, option_type='call')
        put_price = black_scholes_price(S, K, T, r, sigma, option_type='put')
        
        # Put-call parity: C - P = S - K*exp(-r*T)
        lhs = call_price - put_price
        rhs = S - K * np.exp(-r * T)
        
        assert abs(lhs - rhs) < 1e-6
    
    def test_black_scholes_expired(self):
        """Test Black-Scholes with expired option (T=0)."""
        S = 100
        K = 90
        T = 0.0
        r = 0.05
        sigma = 0.2
        
        call_price = black_scholes_price(S, K, T, r, sigma, option_type='call')
        put_price = black_scholes_price(S, K, T, r, sigma, option_type='put')
        
        # Expired call should equal intrinsic value
        assert abs(call_price - max(S - K, 0)) < 1e-10
        # Expired put should equal intrinsic value
        assert abs(put_price - max(K - S, 0)) < 1e-10
    
    def test_calculate_greeks(self):
        """Test Greeks calculation."""
        S = 100
        K = 100
        T = 1.0
        r = 0.05
        sigma = 0.2
        
        greeks = calculate_greeks(S, K, T, r, sigma, option_type='call')
        
        # Check all Greeks are present
        assert 'delta' in greeks
        assert 'gamma' in greeks
        assert 'theta' in greeks
        assert 'vega' in greeks
        assert 'rho' in greeks
        
        # Delta for at-the-money call should be around 0.5
        assert 0 < greeks['delta'] < 1
        
        # Gamma should be positive
        assert greeks['gamma'] > 0
        
        # Vega should be positive
        assert greeks['vega'] > 0
    
    def test_monte_carlo_option_price(self):
        """Test Monte Carlo option pricing."""
        S = 100
        K = 100
        T = 1.0
        r = 0.05
        sigma = 0.2
        n_simulations = 10000
        
        price = monte_carlo_option_price(S, K, T, r, sigma, n_simulations, option_type='call')
        
        # Price should be positive
        assert price > 0
        
        # Should be reasonably close to Black-Scholes (within 5%)
        bs_price = black_scholes_price(S, K, T, r, sigma, option_type='call')
        assert abs(price - bs_price) / bs_price < 0.1  # Within 10% tolerance for MC


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
