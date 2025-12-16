"""
Statistical Analysis and Hypothesis Testing

Advanced statistical methods for quantitative finance.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple, Dict, List
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, t, chi2


def t_test(sample1: pd.Series, sample2: Optional[pd.Series] = None, 
           mu: Optional[float] = None, alternative: str = 'two-sided') -> Dict:
    """
    Perform t-test for means.
    
    Args:
        sample1: First sample
        sample2: Second sample (for two-sample test) or None (for one-sample)
        mu: Population mean for one-sample test
        alternative: 'two-sided', 'greater', or 'less'
        
    Returns:
        Dictionary with test results
    """
    if sample2 is None:
        # One-sample t-test
        result = stats.ttest_1samp(sample1.dropna(), mu if mu is not None else 0)
        return {
            'test_type': 'one_sample',
            'statistic': result.statistic,
            'p_value': result.pvalue,
            'mean': sample1.mean(),
            'std': sample1.std(),
            'n': len(sample1.dropna())
        }
    else:
        # Two-sample t-test
        result = stats.ttest_ind(sample1.dropna(), sample2.dropna())
        return {
            'test_type': 'two_sample',
            'statistic': result.statistic,
            'p_value': result.pvalue,
            'mean1': sample1.mean(),
            'mean2': sample2.mean(),
            'n1': len(sample1.dropna()),
            'n2': len(sample2.dropna())
        }


def normality_test(data: pd.Series, method: str = 'shapiro') -> Dict:
    """
    Test for normality using various tests.
    
    Args:
        data: Data series to test
        method: 'shapiro', 'jarque_bera', or 'anderson'
        
    Returns:
        Dictionary with test results
    """
    data_clean = data.dropna()
    
    if method == 'shapiro':
        # Shapiro-Wilk test (for small samples)
        stat, p_value = stats.shapiro(data_clean[:5000])  # Limit to 5000 for performance
        return {
            'test': 'Shapiro-Wilk',
            'statistic': stat,
            'p_value': p_value,
            'is_normal': p_value > 0.05
        }
    elif method == 'jarque_bera':
        # Jarque-Bera test
        stat, p_value = stats.jarque_bera(data_clean)
        return {
            'test': 'Jarque-Bera',
            'statistic': stat,
            'p_value': p_value,
            'is_normal': p_value > 0.05
        }
    elif method == 'anderson':
        # Anderson-Darling test
        result = stats.anderson(data_clean, dist='norm')
        return {
            'test': 'Anderson-Darling',
            'statistic': result.statistic,
            'critical_values': result.critical_values,
            'significance_levels': result.significance_level
        }
    else:
        raise ValueError(f"Unknown method: {method}")


def correlation_test(x: pd.Series, y: pd.Series, method: str = 'pearson') -> Dict:
    """
    Test correlation between two series.
    
    Args:
        x: First series
        y: Second series
        method: 'pearson', 'spearman', or 'kendall'
        
    Returns:
        Dictionary with correlation and test results
    """
    aligned = pd.concat([x, y], axis=1).dropna()
    x_aligned = aligned.iloc[:, 0]
    y_aligned = aligned.iloc[:, 1]
    
    if method == 'pearson':
        corr, p_value = stats.pearsonr(x_aligned, y_aligned)
    elif method == 'spearman':
        corr, p_value = stats.spearmanr(x_aligned, y_aligned)
    elif method == 'kendall':
        corr, p_value = stats.kendalltau(x_aligned, y_aligned)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return {
        'correlation': corr,
        'p_value': p_value,
        'method': method,
        'is_significant': p_value < 0.05,
        'n': len(aligned)
    }


def bootstrap_confidence_interval(data: pd.Series, statistic: callable,
                                  confidence: float = 0.95, n_bootstrap: int = 10000) -> Tuple[float, float]:
    """
    Calculate bootstrap confidence interval.
    
    Args:
        data: Data series
        statistic: Function to calculate statistic (e.g., np.mean, np.median)
        confidence: Confidence level (e.g., 0.95 for 95%)
        n_bootstrap: Number of bootstrap samples
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    data_clean = data.dropna().values
    bootstrap_stats = []
    
    for _ in range(n_bootstrap):
        sample = np.random.choice(data_clean, size=len(data_clean), replace=True)
        bootstrap_stats.append(statistic(sample))
    
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
    upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))
    
    return (lower, upper)


def chi_square_test(observed: np.ndarray, expected: Optional[np.ndarray] = None) -> Dict:
    """
    Perform chi-square test of independence or goodness of fit.
    
    Args:
        observed: Observed frequencies
        expected: Expected frequencies (for goodness of fit) or None (for independence)
        
    Returns:
        Dictionary with test results
    """
    if expected is None:
        # Test of independence (requires 2D array)
        if observed.ndim != 2:
            raise ValueError("For independence test, observed must be 2D")
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(observed)
    else:
        # Goodness of fit test
        chi2_stat, p_value = stats.chisquare(observed, expected)
        dof = len(observed) - 1
    
    return {
        'chi2_statistic': chi2_stat,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'is_significant': p_value < 0.05
    }


def mann_whitney_test(sample1: pd.Series, sample2: pd.Series) -> Dict:
    """
    Mann-Whitney U test (non-parametric alternative to t-test).
    
    Args:
        sample1: First sample
        sample2: Second sample
        
    Returns:
        Dictionary with test results
    """
    stat, p_value = stats.mannwhitneyu(sample1.dropna(), sample2.dropna(), alternative='two-sided')
    
    return {
        'statistic': stat,
        'p_value': p_value,
        'is_significant': p_value < 0.05,
        'median1': sample1.median(),
        'median2': sample2.median()
    }


def confidence_interval_mean(data: pd.Series, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for the mean.
    
    Args:
        data: Data series
        confidence: Confidence level
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    data_clean = data.dropna()
    n = len(data_clean)
    mean = data_clean.mean()
    std_err = data_clean.std() / np.sqrt(n)
    
    alpha = 1 - confidence
    t_critical = t.ppf(1 - alpha/2, df=n-1)
    
    lower = mean - t_critical * std_err
    upper = mean + t_critical * std_err
    
    return (lower, upper)


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    returns1 = pd.Series(np.random.randn(500) * 0.01, index=dates)
    returns2 = pd.Series(np.random.randn(500) * 0.01 + 0.001, index=dates)
    
    # T-test
    t_result = t_test(returns1, returns2)
    print("Two-sample t-test:")
    print(f"  Statistic: {t_result['statistic']:.4f}")
    print(f"  P-value: {t_result['p_value']:.4f}")
    
    # Normality test
    norm_result = normality_test(returns1, method='jarque_bera')
    print(f"\nNormality test ({norm_result['test']}):")
    print(f"  Is normal: {norm_result['is_normal']}")
    print(f"  P-value: {norm_result['p_value']:.4f}")
    
    # Correlation test
    corr_result = correlation_test(returns1, returns2)
    print(f"\nCorrelation test:")
    print(f"  Correlation: {corr_result['correlation']:.4f}")
    print(f"  P-value: {corr_result['p_value']:.4f}")
    
    # Confidence interval
    ci = confidence_interval_mean(returns1)
    print(f"\n95% Confidence Interval for Mean:")
    print(f"  [{ci[0]:.4f}, {ci[1]:.4f}]")
