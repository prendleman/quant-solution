"""
Performance Attribution

Decompose returns into various components and analyze performance drivers.
Generated as part of quant portfolio development.
"""

from typing import Optional, Dict, List
import numpy as np
import pandas as pd
from scipy import stats


def performance_attribution(portfolio_returns: pd.Series, 
                           benchmark_returns: pd.Series) -> Dict:
    """
    Performance attribution analysis vs benchmark.
    
    Args:
        portfolio_returns: Portfolio return series
        benchmark_returns: Benchmark return series
        
    Returns:
        Dictionary with attribution metrics
    """
    # Align data
    aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    portfolio = aligned.iloc[:, 0]
    benchmark = aligned.iloc[:, 1]
    
    # Excess returns
    excess_returns = portfolio - benchmark
    
    # Cumulative returns
    portfolio_cum = (1 + portfolio).cumprod()
    benchmark_cum = (1 + benchmark).cumprod()
    
    # Total return
    portfolio_total = portfolio_cum.iloc[-1] - 1
    benchmark_total = benchmark_cum.iloc[-1] - 1
    excess_total = portfolio_total - benchmark_total
    
    # Volatility
    portfolio_vol = portfolio.std() * np.sqrt(252)
    benchmark_vol = benchmark.std() * np.sqrt(252)
    
    # Sharpe ratios
    portfolio_sharpe = portfolio.mean() / portfolio.std() * np.sqrt(252) if portfolio.std() > 0 else 0
    benchmark_sharpe = benchmark.mean() / benchmark.std() * np.sqrt(252) if benchmark.std() > 0 else 0
    
    # Information ratio
    info_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
    
    # Tracking error
    tracking_error = excess_returns.std() * np.sqrt(252)
    
    # Beta
    covariance = np.cov(portfolio, benchmark)[0, 1]
    benchmark_variance = np.var(benchmark)
    beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
    
    # Alpha (annualized)
    alpha = (excess_returns.mean() - (beta - 1) * benchmark.mean()) * 252
    
    return {
        'total_return': portfolio_total,
        'benchmark_return': benchmark_total,
        'excess_return': excess_total,
        'volatility': portfolio_vol,
        'benchmark_volatility': benchmark_vol,
        'sharpe_ratio': portfolio_sharpe,
        'benchmark_sharpe': benchmark_sharpe,
        'information_ratio': info_ratio,
        'tracking_error': tracking_error,
        'beta': beta,
        'alpha': alpha
    }


def rolling_performance_metrics(returns: pd.Series, window: int = 60) -> pd.DataFrame:
    """
    Calculate rolling performance metrics.
    
    Args:
        returns: Return series
        window: Rolling window size
        
    Returns:
        DataFrame with rolling metrics
    """
    metrics = pd.DataFrame(index=returns.index)
    
    # Rolling returns
    metrics['rolling_return'] = returns.rolling(window).apply(
        lambda x: (1 + x).prod() - 1
    )
    
    # Rolling volatility
    metrics['rolling_volatility'] = returns.rolling(window).std() * np.sqrt(252)
    
    # Rolling Sharpe ratio
    metrics['rolling_sharpe'] = (
        returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)
    )
    
    # Rolling max drawdown
    def rolling_max_dd(x):
        cumret = (1 + x).cumprod()
        running_max = cumret.expanding().max()
        drawdown = (cumret - running_max) / running_max
        return drawdown.min()
    
    metrics['rolling_max_dd'] = returns.rolling(window).apply(rolling_max_dd)
    
    return metrics


def return_decomposition(returns: pd.Series, factors: pd.DataFrame) -> pd.DataFrame:
    """
    Decompose returns into factor contributions.
    
    Args:
        returns: Asset/portfolio returns
        factors: DataFrame of factor returns
        
    Returns:
        DataFrame with decomposed returns
    """
    # Align data
    aligned = pd.concat([returns, factors], axis=1).dropna()
    asset_returns = aligned.iloc[:, 0]
    factor_data = aligned[factors.columns]
    
    # Calculate factor betas using full period
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(factor_data, asset_returns)
    
    # Factor contributions
    decomposition = pd.DataFrame(index=aligned.index)
    for i, factor in enumerate(factors.columns):
        decomposition[f'{factor}_contribution'] = model.coef_[i] * factor_data[factor]
    
    decomposition['factor_total'] = decomposition.sum(axis=1)
    decomposition['alpha'] = model.intercept_
    decomposition['residual'] = asset_returns - decomposition['factor_total'] - decomposition['alpha']
    decomposition['total_return'] = asset_returns
    
    return decomposition


def win_rate_analysis(returns: pd.Series, benchmark: Optional[pd.Series] = None) -> Dict:
    """
    Calculate win rate and related metrics.
    
    Args:
        returns: Return series
        benchmark: Optional benchmark for comparison
        
    Returns:
        Dictionary with win rate metrics
    """
    if benchmark is not None:
        aligned = pd.concat([returns, benchmark], axis=1).dropna()
        returns_aligned = aligned.iloc[:, 0]
        benchmark_aligned = aligned.iloc[:, 1]
        excess = returns_aligned - benchmark_aligned
        win_rate = (excess > 0).sum() / len(excess)
    else:
        win_rate = (returns > 0).sum() / len(returns)
        excess = None
    
    # Average win vs average loss
    positive_returns = returns[returns > 0]
    negative_returns = returns[returns < 0]
    
    avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
    avg_loss = negative_returns.mean() if len(negative_returns) > 0 else 0
    win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
    return {
        'win_rate': win_rate,
        'average_win': avg_win,
        'average_loss': avg_loss,
        'win_loss_ratio': win_loss_ratio,
        'excess_win_rate': win_rate if benchmark is not None else None
    }


def calmar_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Calmar ratio (annual return / max drawdown).
    
    Args:
        returns: Return series
        risk_free_rate: Risk-free rate
        
    Returns:
        Calmar ratio
    """
    # Annualized return
    annual_return = returns.mean() * 252 - risk_free_rate
    
    # Max drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_dd = abs(drawdown.min())
    
    return annual_return / max_dd if max_dd > 0 else 0


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    portfolio_returns = pd.Series(np.random.randn(500) * 0.01, index=dates)
    benchmark_returns = pd.Series(np.random.randn(500) * 0.008, index=dates)
    
    # Performance attribution
    attribution = performance_attribution(portfolio_returns, benchmark_returns)
    print("Performance Attribution:")
    print(f"  Excess Return: {attribution['excess_return']:.2%}")
    print(f"  Alpha: {attribution['alpha']:.2%}")
    print(f"  Beta: {attribution['beta']:.4f}")
    print(f"  Information Ratio: {attribution['information_ratio']:.4f}")
    
    # Win rate
    win_rate = win_rate_analysis(portfolio_returns, benchmark_returns)
    print(f"\nWin Rate Analysis:")
    print(f"  Win Rate: {win_rate['win_rate']:.2%}")
    print(f"  Win/Loss Ratio: {win_rate['win_loss_ratio']:.4f}")
    
    # Calmar ratio
    calmar = calmar_ratio(portfolio_returns)
    print(f"\nCalmar Ratio: {calmar:.4f}")
