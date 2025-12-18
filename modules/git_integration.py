'''
Git Integration Module for Quant Portfolio Repository

This module handles:
- Analyzing job descriptions to extract generic requirements
- Identifying gaps in the portfolio repository
- Generating portfolio-quality code improvements
- Committing changes to git repository
'''

import os
import re
from datetime import datetime
from typing import Literal
import subprocess

from modules.helpers import print_lg


def sanitize_requirements(jd_requirements: dict) -> dict:
    '''
    Removes any company names, job titles, or role-specific details from requirements.
    Ensures only generic technical requirements remain.
    Returns sanitized requirements dict.
    '''
    sanitized = jd_requirements.copy()
    
    # Remove company-specific keywords
    company_keywords = ['company', 'employer', 'organization', 'firm', 'institution']
    for key in sanitized:
        if isinstance(sanitized[key], str):
            # Remove common company name patterns
            sanitized[key] = re.sub(r'\b[A-Z][a-z]+ (?:Inc|LLC|Corp|Ltd|Group|Capital|Partners|Associates)\b', '', sanitized[key], flags=re.IGNORECASE)
        elif isinstance(sanitized[key], list):
            sanitized[key] = [item for item in sanitized[key] if not any(kw in str(item).lower() for kw in company_keywords)]
    
    return sanitized


def analyze_jd_requirements(job_description: str, ai_client) -> dict:
    '''
    Analyzes job description to extract GENERIC requirements, skills, and functionality.
    Removes all company-specific information, job titles, and role details.
    Returns dict with: skills, technologies, algorithms, tools, missing_features
    (all generic, no company info)
    '''
    if not job_description or job_description == "Unknown":
        return {
            'skills': [],
            'technologies': [],
            'algorithms': [],
            'tools': [],
            'methodologies': [],
            'missing_features': []
        }
    
    # Enhanced keyword extraction
    jd_lower = job_description.lower()
    requirements = {
        'skills': [],
        'technologies': [],
        'algorithms': [],
        'tools': [],
        'methodologies': [],
        'missing_features': []
    }
    
    # Common quant technologies (expanded list)
    tech_keywords = {
        'python': ['python', 'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn'],
        'r': ['r ', 'rstudio', 'r language'],
        'c++': ['c++', 'cpp', 'c plus plus'],
        'java': ['java'],
        'sql': ['sql', 'postgresql', 'mysql', 'sqlite'],
        'matlab': ['matlab'],
        'julia': ['julia'],
        'scikit-learn': ['scikit-learn', 'sklearn'],
        'tensorflow': ['tensorflow', 'tf '],
        'pytorch': ['pytorch', 'torch'],
        'keras': ['keras'],
        'spark': ['spark', 'pyspark'],
        'hadoop': ['hadoop'],
        'kafka': ['kafka'],
        'tableau': ['tableau'],
        'power bi': ['power bi', 'powerbi'],
        'jupyter': ['jupyter', 'notebook'],
        'git': ['git', 'github', 'gitlab']
    }
    
    for tech, keywords in tech_keywords.items():
        if any(kw in jd_lower for kw in keywords):
            requirements['technologies'].append(tech)
    
    # Common quant skills (expanded list)
    skill_keywords = {
        'statistics': ['statistics', 'statistical', 'statistical analysis'],
        'machine learning': ['machine learning', 'ml ', 'deep learning', 'neural network'],
        'time series': ['time series', 'timeseries', 'time-series'],
        'risk management': ['risk management', 'risk modeling', 'risk analysis'],
        'portfolio optimization': ['portfolio optimization', 'portfolio management', 'asset allocation'],
        'derivatives': ['derivatives', 'options', 'futures', 'swaps'],
        'options pricing': ['options pricing', 'option pricing', 'black-scholes', 'monte carlo'],
        'algorithmic trading': ['algorithmic trading', 'algo trading', 'systematic trading'],
        'backtesting': ['backtesting', 'backtest', 'back test'],
        'quantitative research': ['quantitative research', 'quant research', 'quantitative analysis'],
        'data analysis': ['data analysis', 'data analytics'],
        'financial modeling': ['financial modeling', 'financial model'],
        'regression': ['regression', 'linear regression', 'logistic regression'],
        'monte carlo': ['monte carlo', 'monte carlo simulation'],
        'volatility': ['volatility', 'vol modeling', 'volatility modeling'],
        'market making': ['market making', 'market maker'],
        'high frequency trading': ['high frequency trading', 'hft', 'low latency']
    }
    
    for skill, keywords in skill_keywords.items():
        if any(kw in jd_lower for kw in keywords):
            requirements['skills'].append(skill)
    
    # Use AI to enhance extraction if available
    if ai_client:
        try:
            from modules.ai.openaiConnections import ai_completion
            from modules.ai.deepseekConnections import deepseek_completion
            from modules.ai.geminiConnections import gemini_completion
            from config.secrets import ai_provider
            
            # Create prompt for AI extraction
            prompt = f"""Extract technical requirements from this job description. 
Return ONLY a JSON object with these keys: technologies, skills, algorithms, tools, methodologies.
Each should be an array of strings. Be generic - no company names, job titles, or role-specific details.

Job Description:
{job_description[:2000]}

Return JSON format:
{{
    "technologies": ["python", "pandas"],
    "skills": ["time series analysis", "risk management"],
    "algorithms": ["monte carlo simulation"],
    "tools": ["jupyter"],
    "methodologies": ["backtesting"]
}}"""

            messages = [{"role": "user", "content": prompt}]
            
            # Call appropriate AI
            if ai_provider.lower() == "openai":
                response = ai_completion(ai_client, messages, temperature=0.1, stream=False)
            elif ai_provider.lower() == "deepseek":
                response = deepseek_completion(ai_client, messages, temperature=0.1, stream=False)
            elif ai_provider.lower() == "gemini":
                response = gemini_completion(ai_client, messages)
            else:
                response = None
            
            # Parse AI response
            if response and isinstance(response, str):
                import json
                # Try to extract JSON from response
                try:
                    # Remove markdown code blocks if present
                    clean_response = re.sub(r'```json\n?', '', response)
                    clean_response = re.sub(r'```\n?', '', clean_response)
                    ai_req = json.loads(clean_response.strip())
                    
                    # Merge AI results with keyword extraction
                    for key in requirements:
                        if key in ai_req and isinstance(ai_req[key], list):
                            requirements[key].extend(ai_req[key])
                            # Remove duplicates
                            requirements[key] = list(set(requirements[key]))
                except:
                    pass  # If JSON parsing fails, use keyword extraction only
                    
        except Exception as e:
            print_lg(f"AI-enhanced extraction failed: {e}, using keyword extraction only")
    
    return sanitize_requirements(requirements)


def identify_repo_gaps(jd_requirements: dict, repo_path: str, min_priority: float = 0.0) -> list[str]:
    '''
    Compares generic JD requirements against existing repo to identify missing features.
    Enhanced with priority scoring and smarter gap detection.
    Returns list of missing functionality/features (generic descriptions only).
    
    Args:
        jd_requirements: Dictionary with skills, technologies, algorithms, tools, methodologies
        repo_path: Path to portfolio repository
        min_priority: Minimum priority score (0.0-1.0) to include gap (default: 0.0 = include all)
    '''
    if not repo_path or not os.path.exists(repo_path):
        print_lg(f"Repository path does not exist: {repo_path}")
        return []
    
    gaps = []
    gap_priorities = {}  # Track priority scores for gaps
    
    # Build a cache of repo content for faster searching
    repo_content_cache = {}
    try:
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common non-code directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git', 'tests', '__pycache__']]
            for file in files:
                if file.endswith(('.py', '.ipynb', '.md', '.txt')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            repo_content_cache[file_path] = content
                    except:
                        pass
    except Exception as e:
        print_lg(f"Error building repo content cache: {e}")
    
    # Check for required technologies with priority scoring
    required_tech = jd_requirements.get('technologies', [])
    for tech in required_tech:
        tech_lower = tech.lower()
        tech_files = []
        
        # Search in cached content
        for file_path, content in repo_content_cache.items():
            if tech_lower in content:
                tech_files.append(file_path)
        
        if not tech_files:
            gap = f"Implementation using {tech}"
            # Priority: Higher if it's a core quant tech (Python, pandas, numpy, etc.)
            priority = 0.7 if tech_lower in ['python', 'pandas', 'numpy', 'scipy', 'scikit-learn', 'tensorflow', 'pytorch'] else 0.5
            gaps.append(gap)
            gap_priorities[gap] = priority
    
    # Check for required skills/methodologies with priority scoring
    required_skills = jd_requirements.get('skills', [])
    for skill in required_skills:
        skill_lower = skill.lower()
        skill_files = []
        
        # Search in cached content
        for file_path, content in repo_content_cache.items():
            if skill_lower in content:
                skill_files.append(file_path)
        
        if not skill_files:
            gap = f"{skill.title()} implementation"
            # Priority: Higher for core quant skills
            core_skills = ['machine learning', 'time series', 'risk management', 'portfolio optimization', 
                          'statistics', 'backtesting', 'quantitative research']
            priority = 0.8 if any(cs in skill_lower for cs in core_skills) else 0.5
            gaps.append(gap)
            gap_priorities[gap] = priority
    
    # Check for algorithms
    required_algorithms = jd_requirements.get('algorithms', [])
    for algo in required_algorithms:
        algo_lower = algo.lower()
        algo_files = []
        
        for file_path, content in repo_content_cache.items():
            if algo_lower in content:
                algo_files.append(file_path)
        
        if not algo_files:
            gap = f"{algo.title()} algorithm implementation"
            priority = 0.7  # Algorithms are generally important
            gaps.append(gap)
            gap_priorities[gap] = priority
    
    # Filter by minimum priority if specified
    if min_priority > 0.0:
        filtered_gaps = [gap for gap in gaps if gap_priorities.get(gap, 0.5) >= min_priority]
        if len(filtered_gaps) < len(gaps):
            print_lg(f"Filtered {len(gaps) - len(filtered_gaps)} low-priority gap(s) (min priority: {min_priority})")
        return filtered_gaps
    
    return gaps


def generate_poc_improvements(gaps: list[str], jd_requirements: dict, 
                              ai_client, repo_path: str) -> list[str]:
    '''
    Generates portfolio-quality generic code/features to address identified gaps.
    Uses AI to create professional implementations with:
    - Proper docstrings and type hints
    - Clean code structure
    - Example usage
    - Tests where appropriate
    - README updates
    Ensures no company-specific information in generated code.
    Returns list of created/updated file paths.
    '''
    if not gaps or not repo_path:
        return []
    
    created_files = []
    
    # Ensure repo structure exists
    os.makedirs(os.path.join(repo_path, 'models'), exist_ok=True)
    os.makedirs(os.path.join(repo_path, 'strategies'), exist_ok=True)
    os.makedirs(os.path.join(repo_path, 'analysis'), exist_ok=True)
    os.makedirs(os.path.join(repo_path, 'utils'), exist_ok=True)
    os.makedirs(os.path.join(repo_path, 'examples'), exist_ok=True)
    os.makedirs(os.path.join(repo_path, 'tests'), exist_ok=True)
    
    # Import AI completion function
    try:
        from modules.ai.openaiConnections import ai_completion
        from modules.ai.deepseekConnections import deepseek_completion
        from modules.ai.geminiConnections import gemini_completion
        from config.secrets import ai_provider
    except:
        ai_completion = None
        ai_provider = "openai"
    
    for gap in gaps:
        try:
            # Determine file location based on gap type
            if 'model' in gap.lower() or 'algorithm' in gap.lower():
                dir_path = os.path.join(repo_path, 'models')
            elif 'strategy' in gap.lower() or 'trading' in gap.lower():
                dir_path = os.path.join(repo_path, 'strategies')
            elif 'analysis' in gap.lower() or 'risk' in gap.lower():
                dir_path = os.path.join(repo_path, 'analysis')
            else:
                dir_path = os.path.join(repo_path, 'utils')
            
            # Create a generic implementation file
            file_name = gap.lower().replace(' ', '_').replace('implementation', '').replace('using_', '')
            file_name = re.sub(r'[^a-z0-9_]', '', file_name)
            if not file_name.endswith('.py'):
                file_name += '.py'
            
            file_path = os.path.join(dir_path, file_name)
            
            # Skip if file already exists
            if os.path.exists(file_path):
                continue
            
            # Generate code using AI if available
            code_content = None
            if ai_client and ai_completion:
                try:
                    # Create prompt for AI code generation
                    tech_stack = jd_requirements.get('technologies', [])
                    skills = jd_requirements.get('skills', [])
                    
                    prompt = f"""Generate a professional Python implementation for: {gap}

Requirements:
- This is for a quantitative finance portfolio
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: {', '.join(tech_stack[:5]) if tech_stack else 'numpy, pandas'}
- Demonstrate quant skills related to: {', '.join(skills[:3]) if skills else 'quantitative analysis'}
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality

Generate ONLY the Python code, no explanations. Start with the module docstring."""

                    messages = [{"role": "user", "content": prompt}]
                    
                    # Call appropriate AI completion
                    if ai_provider.lower() == "openai" and ai_completion:
                        response = ai_completion(ai_client, messages, temperature=0.3, stream=False)
                        code_content = response if isinstance(response, str) else str(response)
                    elif ai_provider.lower() == "deepseek":
                        response = deepseek_completion(ai_client, messages, temperature=0.3, stream=False)
                        code_content = response if isinstance(response, str) else str(response)
                    elif ai_provider.lower() == "gemini":
                        response = gemini_completion(ai_client, messages)
                        code_content = response if isinstance(response, str) else str(response)
                    
                    # Clean up code (remove markdown code blocks if present)
                    if code_content:
                        code_content = re.sub(r'```python\n?', '', code_content)
                        code_content = re.sub(r'```\n?', '', code_content)
                        code_content = code_content.strip()
                        
                except Exception as e:
                    print_lg(f"AI code generation failed for {gap}: {e}")
                    code_content = None
            
            # Fallback to template if AI generation failed
            if not code_content:
                # Generate enhanced template based on gap type
                if 'time series' in gap.lower():
                    code_content = generate_time_series_template(gap)
                elif 'portfolio' in gap.lower() or 'optimization' in gap.lower():
                    code_content = generate_portfolio_template(gap)
                elif 'risk' in gap.lower():
                    code_content = generate_risk_template(gap)
                elif 'trading' in gap.lower() or 'strategy' in gap.lower():
                    code_content = generate_trading_template(gap)
                elif 'backtest' in gap.lower():
                    code_content = generate_backtest_template(gap)
                else:
                    code_content = generate_generic_template(gap, jd_requirements)
            
            # Write file
            if code_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code_content)
                created_files.append(file_path)
                print_lg(f"Created portfolio file: {file_path}")
            
        except Exception as e:
            print_lg(f"Error generating improvement for {gap}: {e}")
    
    return created_files


def generate_time_series_template(gap: str) -> str:
    '''Generate time series analysis template'''
    return f'''"""
{gap.title()}

Time series analysis and modeling implementation.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def analyze_time_series(data: pd.Series, window: int = 30) -> dict:
    """
    Analyze time series data with statistical metrics.
    
    Args:
        data: Time series data as pandas Series
        window: Rolling window size for calculations
        
    Returns:
        Dictionary containing analysis results
    """
    results = {{
        'mean': data.mean(),
        'std': data.std(),
        'min': data.min(),
        'max': data.max(),
        'skewness': stats.skew(data.dropna()),
        'kurtosis': stats.kurtosis(data.dropna()),
        'rolling_mean': data.rolling(window=window).mean(),
        'rolling_std': data.rolling(window=window).std()
    }}
    return results


def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate returns from price series.
    
    Args:
        prices: Price series
        
    Returns:
        Returns series
    """
    return prices.pct_change().dropna()


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    sample_data = pd.Series(np.random.randn(100).cumsum(), index=dates)
    results = analyze_time_series(sample_data)
    returns = calculate_returns(sample_data)
    print("Time series analysis completed successfully")
    print(f"Mean: {{results['mean']:.4f}}, Std: {{results['std']:.4f}}")
'''


def generate_portfolio_template(gap: str) -> str:
    '''Generate portfolio optimization template'''
    return f'''"""
{gap.title()}

Portfolio optimization and management implementation.
Generated as part of quant portfolio development.
"""

from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def optimize_portfolio(returns: pd.DataFrame, risk_free_rate: float = 0.02) -> dict:
    """
    Optimize portfolio using mean-variance optimization.
    
    Args:
        returns: DataFrame of asset returns (columns = assets, rows = time)
        risk_free_rate: Risk-free rate for Sharpe ratio calculation
        
    Returns:
        Dictionary with optimal weights and metrics
    """
    n_assets = returns.shape[1]
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    def portfolio_performance(weights: np.ndarray) -> Tuple[float, float]:
        """Calculate portfolio return and volatility"""
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return portfolio_return, portfolio_vol
    
    def negative_sharpe(weights: np.ndarray) -> float:
        """Negative Sharpe ratio for minimization"""
        ret, vol = portfolio_performance(weights)
        return -(ret - risk_free_rate) / vol if vol > 0 else 1e10
    
    # Constraints: weights sum to 1
    constraints = {{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}}
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.array([1/n_assets] * n_assets)
    
    result = minimize(negative_sharpe, initial_weights, method='SLSQP',
                     bounds=bounds, constraints=constraints)
    
    optimal_weights = result.x
    ret, vol = portfolio_performance(optimal_weights)
    sharpe = (ret - risk_free_rate) / vol if vol > 0 else 0
    
    return {{
        'weights': dict(zip(returns.columns, optimal_weights)),
        'expected_return': ret,
        'volatility': vol,
        'sharpe_ratio': sharpe
    }}


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    assets = ['Asset1', 'Asset2', 'Asset3']
    returns_data = pd.DataFrame(
        np.random.randn(252, 3) * 0.01,
        index=dates,
        columns=assets
    )
    result = optimize_portfolio(returns_data)
    print("Portfolio optimization completed")
    print(f"Optimal weights: {{result['weights']}}")
    print(f"Sharpe ratio: {{result['sharpe_ratio']:.4f}}")
'''


def generate_risk_template(gap: str) -> str:
    '''Generate risk management template'''
    return f'''"""
{gap.title()}

Risk management and analysis implementation.
Generated as part of quant portfolio development.
"""

from typing import Optional
import numpy as np
import pandas as pd
from scipy import stats


def calculate_var(returns: pd.Series, confidence_level: float = 0.05) -> float:
    """
    Calculate Value at Risk (VaR) using historical method.
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
        
    Returns:
        VaR value
    """
    return returns.quantile(confidence_level)


def calculate_cvar(returns: pd.Series, confidence_level: float = 0.05) -> float:
    """
    Calculate Conditional Value at Risk (CVaR).
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level
        
    Returns:
        CVaR value
    """
    var = calculate_var(returns, confidence_level)
    return returns[returns <= var].mean()


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate maximum drawdown.
    
    Args:
        prices: Price series
        
    Returns:
        Maximum drawdown as percentage
    """
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    var_95 = calculate_var(returns, 0.05)
    cvar_95 = calculate_cvar(returns, 0.05)
    print(f"VaR (95%): {{var_95:.4f}}")
    print(f"CVaR (95%): {{cvar_95:.4f}}")
'''


def generate_trading_template(gap: str) -> str:
    '''Generate trading strategy template'''
    return f'''"""
{gap.title()}

Trading strategy implementation.
Generated as part of quant portfolio development.
"""

from typing import Optional, Dict
import numpy as np
import pandas as pd


class TradingStrategy:
    """
    Base trading strategy class.
    """
    
    def __init__(self, name: str):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
        """
        self.name = name
        self.positions = pd.Series(dtype=float)
        self.signals = pd.Series(dtype=int)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals from data.
        
        Args:
            data: Market data DataFrame
            
        Returns:
            Series of signals (1 = buy, -1 = sell, 0 = hold)
        """
        # Strategy-specific signal generation
        signals = pd.Series(0, index=data.index)
        return signals
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000) -> Dict:
        """
        Backtest the strategy.
        
        Args:
            data: Market data with prices
            initial_capital: Starting capital
            
        Returns:
            Dictionary with backtest results
        """
        signals = self.generate_signals(data)
        positions = signals.diff().fillna(0)
        returns = data.pct_change()
        strategy_returns = (positions.shift(1) * returns).sum(axis=1)
        cumulative_returns = (1 + strategy_returns).cumprod()
        
        return {{
            'signals': signals,
            'positions': positions,
            'returns': strategy_returns,
            'cumulative_returns': cumulative_returns,
            'final_value': initial_capital * cumulative_returns.iloc[-1]
        }}


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = pd.DataFrame(
        np.random.randn(100, 2).cumsum() + 100,
        index=dates,
        columns=['Asset1', 'Asset2']
    )
    strategy = TradingStrategy("Example Strategy")
    results = strategy.backtest(prices)
    print(f"Strategy final value: ${{results['final_value']:.2f}}")
'''


def generate_backtest_template(gap: str) -> str:
    '''Generate backtesting framework template'''
    return f'''"""
{gap.title()}

Backtesting framework for trading strategies.
Generated as part of quant portfolio development.
"""

from typing import Callable, Dict, Optional
import numpy as np
import pandas as pd


class BacktestEngine:
    """
    Backtesting engine for quantitative strategies.
    """
    
    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate per trade
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.cash = initial_capital
        self.positions = {{}}
        self.trades = []
    
    def run(self, data: pd.DataFrame, strategy: Callable) -> Dict:
        """
        Run backtest on historical data.
        
        Args:
            data: Historical price data
            strategy: Strategy function that returns signals
            
        Returns:
            Dictionary with backtest results
        """
        equity_curve = [self.initial_capital]
        
        for i, (timestamp, row) in enumerate(data.iterrows()):
            # Get strategy signals
            signals = strategy(data.iloc[:i+1])
            
            # Execute trades based on signals
            # Implementation would handle position sizing, execution, etc.
            
            # Update equity
            current_value = self.cash + sum(
                self.positions.get(asset, 0) * row[asset] 
                for asset in data.columns
            )
            equity_curve.append(current_value)
        
        equity_series = pd.Series(equity_curve, index=[data.index[0]] + list(data.index))
        returns = equity_series.pct_change().dropna()
        
        return {{
            'equity_curve': equity_series,
            'returns': returns,
            'total_return': (equity_series.iloc[-1] / self.initial_capital) - 1,
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'max_drawdown': ((equity_series / equity_series.expanding().max()) - 1).min()
        }}


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    data = pd.DataFrame(
        np.random.randn(252, 1).cumsum() + 100,
        index=dates,
        columns=['Price']
    )
    
    def simple_strategy(data: pd.DataFrame) -> pd.Series:
        """Simple moving average crossover strategy"""
        ma_short = data['Price'].rolling(10).mean()
        ma_long = data['Price'].rolling(30).mean()
        return (ma_short > ma_long).astype(int)
    
    engine = BacktestEngine()
    results = engine.run(data, simple_strategy)
    print(f"Total return: {{results['total_return']:.2%}}")
    print(f"Sharpe ratio: {{results['sharpe_ratio']:.4f}}")
'''


def generate_generic_template(gap: str, jd_requirements: dict) -> str:
    '''Generate generic template based on requirements'''
    tech_stack = jd_requirements.get('technologies', [])
    skills = jd_requirements.get('skills', [])
    
    imports = ["import numpy as np", "import pandas as pd"]
    if 'scipy' in tech_stack or any('stat' in s.lower() for s in skills):
        imports.append("from scipy import stats")
    if 'sklearn' in tech_stack or 'machine learning' in ' '.join(skills).lower():
        imports.append("from sklearn import preprocessing")
    
    return f'''"""
{gap.title()}

This module provides a generic implementation for {gap.lower()}.
Generated as part of quant portfolio development.

Note: This is a portfolio-quality implementation demonstrating quant skills.
"""

from typing import Optional, List, Dict, Any
{chr(10).join(imports)}


def main_function(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Main function for {gap.lower()}.
    
    Args:
        data: Input data as pandas DataFrame
        **kwargs: Additional parameters
        
    Returns:
        Processed data as pandas DataFrame
    """
    # Implementation placeholder - enhance based on specific requirements
    return data


if __name__ == "__main__":
    # Example usage
    sample_data = pd.DataFrame()
    result = main_function(sample_data)
    print("Example completed successfully")
'''


def commit_to_poc_repo(repo_path: str, code_files: list[str], 
                       features_added: list[str], remote_url: str = "", 
                       github_token: str = "") -> bool:
    '''
    Commits code improvements to git repository with generic commit message.
    Optionally pushes to remote repository using GitHub token authentication.
    No company names, job titles, or JD references in commit message.
    Returns success status.
    '''
    if not repo_path or not os.path.exists(repo_path):
        print_lg(f"Repository path does not exist: {repo_path}")
        return False
    
    if not code_files:
        return True  # Nothing to commit
    
    try:
        # Initialize git repo if needed
        if not os.path.exists(os.path.join(repo_path, '.git')):
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True, timeout=10)
            print_lg(f"Initialized git repository at {repo_path}")
        
        # Configure git user if not set (required for commits)
        try:
            subprocess.run(['git', 'config', 'user.name', 'Quant Portfolio Bot'], 
                         cwd=repo_path, check=True, capture_output=True, timeout=5)
            subprocess.run(['git', 'config', 'user.email', 'portfolio@quant.dev'], 
                         cwd=repo_path, check=True, capture_output=True, timeout=5)
        except:
            pass  # User config may already exist
        
        # Stage files
        for file_path in code_files:
            if os.path.exists(file_path):
                rel_path = os.path.relpath(file_path, repo_path)
                subprocess.run(['git', 'add', rel_path], cwd=repo_path, check=True, capture_output=True, timeout=10)
        
        # Create generic commit message
        features_str = ", ".join(features_added[:3])  # Limit to first 3 features
        if len(features_added) > 3:
            features_str += ", ..."
        
        commit_message = f"Add: {features_str} | Portfolio improvements"
        
        # Commit
        result = subprocess.run(
            ['git', 'commit', '-m', commit_message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_lg(f"Successfully committed to portfolio repo: {commit_message}")
            
            # Push to remote if configured
            if remote_url and github_token:
                try:
                    # Check if remote exists
                    remote_check = subprocess.run(
                        ['git', 'remote', 'get-url', 'origin'],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if remote_check.returncode != 0:
                        # Add remote if it doesn't exist
                        # Insert token into remote URL for authentication
                        if 'github.com' in remote_url:
                            # Format: https://token@github.com/user/repo.git
                            auth_url = remote_url.replace('https://', f'https://{github_token}@')
                            subprocess.run(
                                ['git', 'remote', 'add', 'origin', auth_url],
                                cwd=repo_path,
                                check=True,
                                capture_output=True,
                                timeout=10
                            )
                            print_lg("Added remote origin with authentication")
                    
                    # Get current branch name
                    branch_check = subprocess.run(
                        ['git', 'branch', '--show-current'],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    branch_name = branch_check.stdout.strip() if branch_check.returncode == 0 else 'main'
                    if not branch_name:
                        branch_name = 'main'
                    
                    # Push to remote with timeout
                    push_result = subprocess.run(
                        ['git', 'push', '-u', 'origin', branch_name],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=30  # 30 second timeout for push
                    )
                    
                    if push_result.returncode == 0:
                        print_lg("Successfully pushed to remote repository")
                    else:
                        print_lg(f"Push to remote failed: {push_result.stderr}")
                        # Don't fail the whole operation if push fails
                        
                except subprocess.TimeoutExpired:
                    print_lg("Git push operation timed out - continuing without push")
                    # Don't fail the whole operation if push times out
                except Exception as e:
                    print_lg(f"Error pushing to remote: {e}")
                    # Don't fail the whole operation if push fails
            
            return True
        else:
            print_lg(f"Git commit failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_lg("Git operation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print_lg(f"Error committing to git repo: {e}")
        return False
    except Exception as e:
        print_lg(f"Unexpected error in git commit: {e}")
        return False


