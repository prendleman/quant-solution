"""
Foreign Exchange (FX) Models

Currency pair analysis, carry trade strategies, FX volatility modeling,
and exchange rate forecasting models.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def calculate_forward_rate(spot_rate: float, domestic_rate: float,
                           foreign_rate: float, time_to_maturity: float) -> float:
    """
    Calculate forward exchange rate using covered interest rate parity.
    
    Args:
        spot_rate: Current spot exchange rate
        domestic_rate: Domestic interest rate (annual, as decimal)
        foreign_rate: Foreign interest rate (annual, as decimal)
        time_to_maturity: Time to maturity in years
        
    Returns:
        Forward exchange rate
    """
    return spot_rate * np.exp((domestic_rate - foreign_rate) * time_to_maturity)


def carry_trade_return(spot_rate: float, forward_rate: float,
                      domestic_rate: float, foreign_rate: float,
                      time_to_maturity: float) -> Dict[str, float]:
    """
    Calculate carry trade returns and components.
    
    Args:
        spot_rate: Current spot exchange rate
        forward_rate: Forward exchange rate
        domestic_rate: Domestic interest rate
        foreign_rate: Foreign interest rate
        time_to_maturity: Time to maturity in years
        
    Returns:
        Dictionary with carry trade metrics
    """
    # Interest rate differential (carry)
    interest_differential = (foreign_rate - domestic_rate) * time_to_maturity
    
    # Currency appreciation/depreciation
    currency_return = (forward_rate - spot_rate) / spot_rate
    
    # Total return
    total_return = interest_differential + currency_return
    
    # Sharpe-like metric (simplified)
    sharpe_approx = total_return / abs(currency_return) if currency_return != 0 else 0
    
    return {
        'interest_carry': interest_differential,
        'currency_return': currency_return,
        'total_return': total_return,
        'carry_sharpe': sharpe_approx,
        'spot_rate': spot_rate,
        'forward_rate': forward_rate
    }


def fx_volatility_smile(strikes: np.ndarray, implied_vols: np.ndarray,
                       spot_rate: float) -> Dict[str, float]:
    """
    Analyze FX volatility smile/skew.
    
    Args:
        strikes: Array of strike prices
        implied_vols: Array of implied volatilities
        spot_rate: Current spot exchange rate
        
    Returns:
        Dictionary with volatility smile metrics
    """
    # Calculate moneyness (strike / spot)
    moneyness = strikes / spot_rate
    
    # Fit polynomial to volatility smile
    coeffs = np.polyfit(moneyness - 1, implied_vols, deg=2)
    
    # Calculate skew (slope at ATM)
    skew = coeffs[1]  # First derivative at ATM
    
    # Calculate kurtosis (curvature)
    kurtosis = coeffs[0] * 2  # Second derivative
    
    # ATM volatility
    atm_vol = np.polyval(coeffs, 0)
    
    return {
        'atm_volatility': atm_vol,
        'volatility_skew': skew,
        'volatility_kurtosis': kurtosis,
        'smile_coefficients': coeffs.tolist()
    }


def triangular_arbitrage(rate_ab: float, rate_bc: float, rate_ac: float) -> Dict[str, float]:
    """
    Detect triangular arbitrage opportunities in FX markets.
    
    Args:
        rate_ab: Exchange rate A/B
        rate_bc: Exchange rate B/C
        rate_ac: Exchange rate A/C
        
    Returns:
        Dictionary with arbitrage opportunity details
    """
    # Theoretical rate A/C from cross
    theoretical_ac = rate_ab * rate_bc
    
    # Arbitrage opportunity
    arbitrage_pct = (theoretical_ac - rate_ac) / rate_ac * 100
    
    # Profitability
    is_profitable = abs(arbitrage_pct) > 0.01  # 1 basis point threshold
    
    return {
        'theoretical_rate_ac': theoretical_ac,
        'actual_rate_ac': rate_ac,
        'arbitrage_pct': arbitrage_pct,
        'is_profitable': is_profitable,
        'profit_pct': abs(arbitrage_pct) if is_profitable else 0.0
    }


def fx_momentum_strategy(returns: pd.Series, lookback: int = 20,
                        threshold: float = 0.02) -> pd.Series:
    """
    Simple FX momentum strategy based on recent returns.
    
    Args:
        returns: Series of FX returns
        lookback: Lookback period for momentum calculation
        threshold: Minimum momentum threshold for signal
        
    Returns:
        Series of trading signals (-1, 0, 1)
    """
    momentum = returns.rolling(window=lookback).mean()
    signals = pd.Series(0, index=returns.index)
    
    signals[momentum > threshold] = 1   # Long signal
    signals[momentum < -threshold] = -1  # Short signal
    
    return signals


def purchasing_power_parity(domestic_price_level: float, foreign_price_level: float,
                           base_exchange_rate: float) -> Dict[str, float]:
    """
    Calculate Purchasing Power Parity (PPP) exchange rate.
    
    Args:
        domestic_price_level: Domestic price level index
        foreign_price_level: Foreign price level index
        base_exchange_rate: Base period exchange rate
        
    Returns:
        Dictionary with PPP metrics
    """
    # PPP exchange rate
    ppp_rate = base_exchange_rate * (domestic_price_level / foreign_price_level)
    
    # Deviation from PPP
    current_rate = ppp_rate  # Assuming current = PPP for calculation
    deviation = (current_rate - ppp_rate) / ppp_rate * 100
    
    return {
        'ppp_exchange_rate': ppp_rate,
        'deviation_from_ppp_pct': deviation,
        'domestic_price_level': domestic_price_level,
        'foreign_price_level': foreign_price_level
    }


def fx_correlation_matrix(currency_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple currency pairs.
    
    Args:
        currency_returns: DataFrame with currency returns (columns = currencies)
        
    Returns:
        Correlation matrix
    """
    return currency_returns.corr()


def currency_basket_hedge(portfolio_exposure: Dict[str, float],
                         currency_returns: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate optimal currency hedge ratios for a portfolio.
    
    Args:
        portfolio_exposure: Dictionary of currency exposures {currency: amount}
        currency_returns: DataFrame of historical currency returns
        
    Returns:
        Dictionary with optimal hedge ratios
    """
    # Calculate portfolio currency return
    currencies = list(portfolio_exposure.keys())
    portfolio_return = pd.Series(0.0, index=currency_returns.index)
    
    total_exposure = sum(abs(v) for v in portfolio_exposure.values())
    
    for currency in currencies:
        if currency in currency_returns.columns:
            weight = portfolio_exposure[currency] / total_exposure if total_exposure > 0 else 0
            portfolio_return += weight * currency_returns[currency]
    
    # Calculate hedge ratios (minimize variance)
    hedge_ratios = {}
    for currency in currencies:
        if currency in currency_returns.columns:
            # Simple hedge: negative correlation
            correlation = currency_returns[currency].corr(portfolio_return)
            hedge_ratios[currency] = -correlation
    
    return {
        'hedge_ratios': hedge_ratios,
        'portfolio_volatility': portfolio_return.std(),
        'hedged_volatility': (portfolio_return * (1 + sum(hedge_ratios.values()))).std()
    }


if __name__ == "__main__":
    # Example usage
    print("FX Models Demo")
    print("=" * 50)
    
    # Forward rate example
    forward = calculate_forward_rate(1.10, 0.03, 0.01, 0.25)
    print(f"\nForward Rate: {forward:.4f}")
    
    # Carry trade example
    carry = carry_trade_return(1.10, 1.12, 0.03, 0.01, 0.25)
    print("\nCarry Trade Metrics:")
    for key, value in carry.items():
        print(f"  {key}: {value:.4f}")
    
    # Triangular arbitrage example
    arb = triangular_arbitrage(1.10, 0.90, 0.99)
    print("\nTriangular Arbitrage:")
    for key, value in arb.items():
        print(f"  {key}: {value:.4f}")
