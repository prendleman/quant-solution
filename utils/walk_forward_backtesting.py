"""
Walk-Forward Backtesting Framework

Robust backtesting methodology using walk-forward analysis to avoid
overfitting and provide realistic performance estimates.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy
"""

from typing import List, Dict, Optional, Tuple, Callable
import numpy as np
import pandas as pd


class WalkForwardBacktest:
    """
    Walk-forward backtesting framework.
    """
    
    def __init__(self, train_window: int, test_window: int, step_size: int = 1):
        """
        Initialize walk-forward backtest.
        
        Args:
            train_window: Training window size (in periods)
            test_window: Testing window size (in periods)
            step_size: Step size for moving forward
        """
        self.train_window = train_window
        self.test_window = test_window
        self.step_size = step_size
        self.results = []
    
    def run(self, data: pd.DataFrame, strategy_func: Callable,
            strategy_params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Run walk-forward backtest.
        
        Args:
            data: Historical data
            strategy_func: Strategy function that takes (train_data, test_data, params)
            strategy_params: Strategy parameters
            
        Returns:
            DataFrame with backtest results
        """
        if strategy_params is None:
            strategy_params = {}
        
        n_periods = len(data)
        results = []
        
        start_idx = self.train_window
        end_idx = start_idx + self.test_window
        
        while end_idx <= n_periods:
            # Split data
            train_data = data.iloc[start_idx - self.train_window:start_idx]
            test_data = data.iloc[start_idx:end_idx]
            
            # Run strategy
            try:
                result = strategy_func(train_data, test_data, strategy_params)
                result['train_start'] = train_data.index[0]
                result['train_end'] = train_data.index[-1]
                result['test_start'] = test_data.index[0]
                result['test_end'] = test_data.index[-1]
                results.append(result)
            except Exception as e:
                print(f"Error in walk-forward step {start_idx}: {e}")
            
            # Move forward
            start_idx += self.step_size
            end_idx = start_idx + self.test_window
        
        return pd.DataFrame(results)
    
    def aggregate_results(self, results_df: pd.DataFrame) -> Dict[str, float]:
        """
        Aggregate walk-forward results.
        
        Args:
            results_df: Results from run()
            
        Returns:
            Dictionary with aggregated metrics
        """
        if len(results_df) == 0:
            return {}
        
        # Aggregate metrics
        metrics = {}
        
        # Return metrics
        if 'returns' in results_df.columns:
            metrics['total_return'] = results_df['returns'].sum()
            metrics['avg_return'] = results_df['returns'].mean()
            metrics['sharpe_ratio'] = results_df['returns'].mean() / (results_df['returns'].std() + 1e-8) * np.sqrt(252)
        
        # Win rate
        if 'returns' in results_df.columns:
            metrics['win_rate'] = (results_df['returns'] > 0).sum() / len(results_df) * 100
        
        # Max drawdown
        if 'equity_curve' in results_df.columns:
            all_drawdowns = []
            for curve in results_df['equity_curve']:
                if isinstance(curve, pd.Series):
                    running_max = curve.expanding().max()
                    drawdown = (curve - running_max) / running_max
                    all_drawdowns.append(abs(drawdown.min()))
            if all_drawdowns:
                metrics['max_drawdown'] = max(all_drawdowns)
        
        return metrics


def monte_carlo_backtest(strategy_func: Callable, data: pd.DataFrame,
                        n_simulations: int = 1000, confidence_level: float = 0.95) -> Dict[str, float]:
    """
    Monte Carlo backtesting - randomize data order to test robustness.
    
    Args:
        strategy_func: Strategy function
        data: Historical data
        n_simulations: Number of Monte Carlo simulations
        confidence_level: Confidence level for intervals
        
    Returns:
        Dictionary with MC backtest results
    """
    results = []
    
    for _ in range(n_simulations):
        # Randomize data (bootstrap)
        shuffled_data = data.sample(frac=1.0, replace=True).reset_index(drop=True)
        
        # Split train/test
        split_idx = int(len(shuffled_data) * 0.7)
        train_data = shuffled_data.iloc[:split_idx]
        test_data = shuffled_data.iloc[split_idx:]
        
        try:
            result = strategy_func(train_data, test_data, {})
            if 'returns' in result:
                results.append(result['returns'])
        except:
            pass
    
    if len(results) == 0:
        return {}
    
    results_array = np.array(results)
    
    return {
        'mean_return': results_array.mean(),
        'std_return': results_array.std(),
        'percentile_5': np.percentile(results_array, 5),
        'percentile_95': np.percentile(results_array, 95),
        'confidence_interval_lower': np.percentile(results_array, (1 - confidence_level) / 2 * 100),
        'confidence_interval_upper': np.percentile(results_array, (1 + confidence_level) / 2 * 100)
    }


def out_of_sample_test(train_data: pd.DataFrame, test_data: pd.DataFrame,
                       strategy_func: Callable, strategy_params: Dict) -> Dict[str, float]:
    """
    Simple out-of-sample test.
    
    Args:
        train_data: Training data
        test_data: Test data
        strategy_func: Strategy function
        strategy_params: Strategy parameters
        
    Returns:
        Dictionary with OOS test results
    """
    try:
        result = strategy_func(train_data, test_data, strategy_params)
        
        # Calculate metrics
        if 'returns' in result:
            returns = result['returns']
            if isinstance(returns, pd.Series):
                return {
                    'total_return': returns.sum(),
                    'sharpe_ratio': returns.mean() / (returns.std() + 1e-8) * np.sqrt(252),
                    'max_drawdown': calculate_max_drawdown(returns),
                    'win_rate': (returns > 0).sum() / len(returns) * 100
                }
    except Exception as e:
        return {'error': str(e)}
    
    return {}


def calculate_max_drawdown(returns: pd.Series) -> float:
    """Calculate maximum drawdown from returns."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return abs(drawdown.min())


if __name__ == "__main__":
    # Example usage
    print("Walk-Forward Backtesting Demo")
    print("=" * 50)
    
    # Simple strategy function
    def simple_strategy(train_data, test_data, params):
        # Buy and hold
        returns = test_data['returns'] if 'returns' in test_data.columns else test_data.iloc[:, 0]
        return {'returns': returns, 'equity_curve': (1 + returns).cumprod()}
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    data = pd.DataFrame({
        'returns': np.random.randn(252) * 0.01,
        'prices': 100 + np.cumsum(np.random.randn(252) * 0.5)
    }, index=dates)
    
    # Walk-forward backtest
    wf = WalkForwardBacktest(train_window=60, test_window=30, step_size=30)
    results = wf.run(data, simple_strategy)
    aggregated = wf.aggregate_results(results)
    
    print("\nWalk-Forward Results:")
    for key, value in aggregated.items():
        print(f"  {key}: {value:.4f}")
