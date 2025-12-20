"""
Fixed Income Models

Bond pricing, yield curve construction, duration, convexity, and other
fixed income analytics commonly used in quantitative finance.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Optional, Tuple, Dict
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.interpolate import interp1d


def bond_price(face_value: float, coupon_rate: float, years_to_maturity: float,
               yield_to_maturity: float, frequency: int = 2) -> float:
    """
    Calculate bond price using present value of cash flows.
    
    Args:
        face_value: Face value (par value) of the bond
        coupon_rate: Annual coupon rate (as decimal, e.g., 0.05 for 5%)
        years_to_maturity: Years until maturity
        yield_to_maturity: Yield to maturity (as decimal)
        frequency: Coupon payments per year (default: 2 for semi-annual)
        
    Returns:
        Bond price
    """
    periods = int(years_to_maturity * frequency)
    coupon_payment = (face_value * coupon_rate) / frequency
    period_yield = yield_to_maturity / frequency
    
    # Present value of coupon payments
    if period_yield > 0:
        pv_coupons = coupon_payment * (1 - (1 + period_yield) ** -periods) / period_yield
    else:
        pv_coupons = coupon_payment * periods
    
    # Present value of face value
    pv_face = face_value / ((1 + period_yield) ** periods)
    
    return pv_coupons + pv_face


def bond_yield_to_maturity(face_value: float, coupon_rate: float,
                           years_to_maturity: float, current_price: float,
                           frequency: int = 2) -> float:
    """
    Calculate yield to maturity using numerical optimization.
    
    Args:
        face_value: Face value of the bond
        coupon_rate: Annual coupon rate
        years_to_maturity: Years until maturity
        current_price: Current market price
        frequency: Coupon payments per year
        
    Returns:
        Yield to maturity (annualized)
    """
    def price_error(ytm):
        return abs(bond_price(face_value, coupon_rate, years_to_maturity, ytm, frequency) - current_price)
    
    result = minimize(price_error, x0=0.05, method='BFGS', bounds=[(0.0001, 1.0)])
    return result.x[0]


def macaulay_duration(face_value: float, coupon_rate: float,
                     years_to_maturity: float, yield_to_maturity: float,
                     frequency: int = 2) -> float:
    """
    Calculate Macaulay duration - weighted average time to receive cash flows.
    
    Args:
        face_value: Face value of the bond
        coupon_rate: Annual coupon rate
        years_to_maturity: Years until maturity
        yield_to_maturity: Yield to maturity
        frequency: Coupon payments per year
        
    Returns:
        Macaulay duration in years
    """
    periods = int(years_to_maturity * frequency)
    coupon_payment = (face_value * coupon_rate) / frequency
    period_yield = yield_to_maturity / frequency
    
    price = bond_price(face_value, coupon_rate, years_to_maturity, yield_to_maturity, frequency)
    
    duration = 0.0
    for t in range(1, periods + 1):
        if t < periods:
            cash_flow = coupon_payment
        else:
            cash_flow = coupon_payment + face_value
        
        pv = cash_flow / ((1 + period_yield) ** t)
        duration += (t / frequency) * (pv / price)
    
    return duration


def modified_duration(face_value: float, coupon_rate: float,
                     years_to_maturity: float, yield_to_maturity: float,
                     frequency: int = 2) -> float:
    """
    Calculate modified duration - price sensitivity to yield changes.
    
    Args:
        face_value: Face value of the bond
        coupon_rate: Annual coupon rate
        years_to_maturity: Years until maturity
        yield_to_maturity: Yield to maturity
        frequency: Coupon payments per year
        
    Returns:
        Modified duration
    """
    mac_duration = macaulay_duration(face_value, coupon_rate, years_to_maturity,
                                     yield_to_maturity, frequency)
    period_yield = yield_to_maturity / frequency
    
    return mac_duration / (1 + period_yield)


def bond_convexity(face_value: float, coupon_rate: float,
                  years_to_maturity: float, yield_to_maturity: float,
                  frequency: int = 2) -> float:
    """
    Calculate bond convexity - second-order price sensitivity.
    
    Args:
        face_value: Face value of the bond
        coupon_rate: Annual coupon rate
        years_to_maturity: Years until maturity
        yield_to_maturity: Yield to maturity
        frequency: Coupon payments per year
        
    Returns:
        Convexity
    """
    periods = int(years_to_maturity * frequency)
    coupon_payment = (face_value * coupon_rate) / frequency
    period_yield = yield_to_maturity / frequency
    
    price = bond_price(face_value, coupon_rate, years_to_maturity, yield_to_maturity, frequency)
    
    convexity = 0.0
    for t in range(1, periods + 1):
        if t < periods:
            cash_flow = coupon_payment
        else:
            cash_flow = coupon_payment + face_value
        
        pv = cash_flow / ((1 + period_yield) ** t)
        time_factor = (t / frequency) * ((t / frequency) + 1)
        convexity += time_factor * (pv / price) / ((1 + period_yield) ** 2)
    
    return convexity


def yield_curve_bootstrap(bond_data: pd.DataFrame) -> pd.Series:
    """
    Bootstrap yield curve from bond prices using bootstrapping method.
    
    Args:
        bond_data: DataFrame with columns: 'maturity', 'coupon_rate', 'price', 'face_value'
        
    Returns:
        Series of spot rates indexed by maturity
    """
    bond_data = bond_data.sort_values('maturity')
    spot_rates = {}
    
    for idx, bond in bond_data.iterrows():
        maturity = bond['maturity']
        coupon_rate = bond['coupon_rate']
        price = bond['price']
        face_value = bond.get('face_value', 100.0)
        
        # For first bond, solve directly
        if len(spot_rates) == 0:
            # Zero-coupon approximation
            ytm = bond_yield_to_maturity(face_value, coupon_rate, maturity, price)
            spot_rates[maturity] = ytm
        else:
            # Bootstrap using previous spot rates
            def price_error(spot_rate):
                periods = int(maturity * 2)  # Semi-annual
                coupon_payment = (face_value * coupon_rate) / 2
                
                pv = 0.0
                for t in range(1, periods):
                    t_years = t / 2.0
                    # Use interpolated spot rate
                    if t_years in spot_rates:
                        rate = spot_rates[t_years]
                    else:
                        # Interpolate
                        maturities = sorted(spot_rates.keys())
                        rates = [spot_rates[m] for m in maturities]
                        if t_years < min(maturities):
                            rate = rates[0]
                        elif t_years > max(maturities):
                            rate = rates[-1]
                        else:
                            interp = interp1d(maturities, rates, kind='linear', fill_value='extrapolate')
                            rate = float(interp(t_years))
                    
                    pv += coupon_payment / ((1 + rate / 2) ** t)
                
                # Final payment uses current spot rate
                pv += (coupon_payment + face_value) / ((1 + spot_rate / 2) ** periods)
                return abs(pv - price)
            
            result = minimize(price_error, x0=0.05, method='BFGS', bounds=[(0.0001, 1.0)])
            spot_rates[maturity] = result.x[0]
    
    return pd.Series(spot_rates)


def duration_matching(liabilities: pd.DataFrame, assets: pd.DataFrame) -> Dict[str, float]:
    """
    Duration matching for asset-liability management.
    
    Args:
        liabilities: DataFrame with 'amount', 'duration' columns
        assets: DataFrame with 'amount', 'duration', 'yield' columns
        
    Returns:
        Dictionary with optimal asset allocation
    """
    total_liability = liabilities['amount'].sum()
    liability_duration = (liabilities['amount'] * liabilities['duration']).sum() / total_liability
    
    # Simple duration matching: find asset mix that matches liability duration
    asset_durations = assets['duration'].values
    asset_amounts = assets['amount'].values
    
    # Weighted average duration constraint
    def duration_error(weights):
        portfolio_duration = np.dot(weights, asset_durations)
        return abs(portfolio_duration - liability_duration)
    
    # Constraints: weights sum to 1, all positive
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0, 1) for _ in range(len(assets))]
    
    initial_weights = np.ones(len(assets)) / len(assets)
    result = minimize(duration_error, initial_weights, method='SLSQP',
                     bounds=bounds, constraints=constraints)
    
    optimal_weights = result.x
    optimal_allocation = {asset: weight * total_liability 
                         for asset, weight in zip(assets.index, optimal_weights)}
    
    return {
        'liability_duration': liability_duration,
        'portfolio_duration': np.dot(optimal_weights, asset_durations),
        'allocation': optimal_allocation,
        'weights': dict(zip(assets.index, optimal_weights))
    }


if __name__ == "__main__":
    # Example usage
    print("Fixed Income Models Demo")
    print("=" * 50)
    
    # Bond pricing example
    price = bond_price(1000, 0.05, 10, 0.04, frequency=2)
    print(f"\nBond Price: ${price:.2f}")
    
    # Duration example
    mac_dur = macaulay_duration(1000, 0.05, 10, 0.04)
    mod_dur = modified_duration(1000, 0.05, 10, 0.04)
    conv = bond_convexity(1000, 0.05, 10, 0.04)
    
    print(f"\nMacaulay Duration: {mac_dur:.2f} years")
    print(f"Modified Duration: {mod_dur:.2f}")
    print(f"Convexity: {conv:.2f}")
    
    # Yield curve example
    bond_data = pd.DataFrame({
        'maturity': [1, 2, 5, 10],
        'coupon_rate': [0.02, 0.025, 0.03, 0.035],
        'price': [98, 96, 92, 88],
        'face_value': [100, 100, 100, 100]
    })
    
    yield_curve = yield_curve_bootstrap(bond_data)
    print("\nYield Curve (Spot Rates):")
    print(yield_curve)
