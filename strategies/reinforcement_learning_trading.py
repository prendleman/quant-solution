"""
Reinforcement Learning Trading Agent

Deep Q-Network (DQN) and Policy Gradient methods for algorithmic trading.
Implements RL agents that learn optimal trading strategies from market data.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, torch (PyTorch), gym (optional)
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TradingEnvironment:
    """
    Simple trading environment for reinforcement learning.
    """
    
    def __init__(self, prices: pd.Series, initial_capital: float = 100000,
                 transaction_cost: float = 0.001):
        """
        Initialize trading environment.
        
        Args:
            prices: Series of asset prices
            initial_capital: Starting capital
            transaction_cost: Transaction cost as fraction (e.g., 0.001 = 0.1%)
        """
        self.prices = prices.values
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.reset()
    
    def reset(self) -> np.ndarray:
        """Reset environment to initial state."""
        self.current_step = 0
        self.capital = self.initial_capital
        self.position = 0  # Number of shares held
        self.total_trades = 0
        return self._get_state()
    
    def _get_state(self) -> np.ndarray:
        """Get current state representation."""
        if self.current_step >= len(self.prices) - 1:
            return np.array([0, 0, 0, 0])
        
        # State: [price_normalized, position_normalized, capital_normalized, returns]
        price = self.prices[self.current_step]
        price_normalized = (price - self.prices[:self.current_step+1].mean()) / (self.prices[:self.current_step+1].std() + 1e-8)
        position_normalized = self.position / 100 if self.position != 0 else 0
        capital_normalized = self.capital / self.initial_capital
        
        if self.current_step > 0:
            returns = (price - self.prices[self.current_step-1]) / self.prices[self.current_step-1]
        else:
            returns = 0
        
        return np.array([price_normalized, position_normalized, capital_normalized, returns])
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute action and return next state, reward, done, info.
        
        Args:
            action: 0=hold, 1=buy, 2=sell
            
        Returns:
            (next_state, reward, done, info)
        """
        if self.current_step >= len(self.prices) - 1:
            return self._get_state(), 0, True, {}
        
        current_price = self.prices[self.current_step]
        next_price = self.prices[self.current_step + 1]
        
        reward = 0.0
        
        # Execute action
        if action == 1 and self.position == 0:  # Buy
            shares = int(self.capital / (current_price * (1 + self.transaction_cost)))
            if shares > 0:
                cost = shares * current_price * (1 + self.transaction_cost)
                self.capital -= cost
                self.position = shares
                self.total_trades += 1
        elif action == 2 and self.position > 0:  # Sell
            proceeds = self.position * current_price * (1 - self.transaction_cost)
            self.capital += proceeds
            self.position = 0
            self.total_trades += 1
        
        # Calculate reward (portfolio value change)
        portfolio_value = self.capital + self.position * next_price
        if hasattr(self, 'prev_portfolio_value'):
            reward = (portfolio_value - self.prev_portfolio_value) / self.initial_capital
        self.prev_portfolio_value = portfolio_value
        
        self.current_step += 1
        done = self.current_step >= len(self.prices) - 1
        
        info = {
            'portfolio_value': portfolio_value,
            'position': self.position,
            'capital': self.capital
        }
        
        return self._get_state(), reward, done, info


class DQNTradingAgent:
    """
    Deep Q-Network agent for trading.
    """
    
    def __init__(self, state_size: int = 4, action_size: int = 3,
                 learning_rate: float = 0.001, gamma: float = 0.95):
        """
        Initialize DQN agent.
        
        Args:
            state_size: Size of state vector
            action_size: Number of actions (hold, buy, sell)
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for DQN agent")
        
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        
        # Neural network: Q-function approximator
        self.q_network = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )
        
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.memory = []  # Experience replay buffer
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
    
    def act(self, state: np.ndarray, training: bool = True) -> int:
        """
        Choose action using epsilon-greedy policy.
        
        Args:
            state: Current state
            training: Whether in training mode (uses epsilon-greedy)
            
        Returns:
            Action index
        """
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_network(state_tensor)
        return q_values.argmax().item()
    
    def remember(self, state: np.ndarray, action: int, reward: float,
                next_state: np.ndarray, done: bool):
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self, batch_size: int = 32):
        """Train on batch of experiences."""
        if len(self.memory) < batch_size:
            return
        
        batch = np.random.choice(len(self.memory), batch_size, replace=False)
        states = torch.FloatTensor([self.memory[i][0] for i in batch])
        actions = torch.LongTensor([self.memory[i][1] for i in batch])
        rewards = torch.FloatTensor([self.memory[i][2] for i in batch])
        next_states = torch.FloatTensor([self.memory[i][3] for i in batch])
        dones = torch.BoolTensor([self.memory[i][4] for i in batch])
        
        current_q = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q = self.q_network(next_states).max(1)[0].detach()
        target_q = rewards + (self.gamma * next_q * ~dones)
        
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


def train_rl_agent(prices: pd.Series, episodes: int = 100,
                  initial_capital: float = 100000) -> Dict[str, List[float]]:
    """
    Train reinforcement learning trading agent.
    
    Args:
        prices: Series of asset prices
        episodes: Number of training episodes
        initial_capital: Starting capital
        
    Returns:
        Dictionary with training metrics
    """
    if not TORCH_AVAILABLE:
        return {
            'episode_returns': [],
            'episode_sharpe': [],
            'message': 'PyTorch not available'
        }
    
    env = TradingEnvironment(prices, initial_capital)
    agent = DQNTradingAgent()
    
    episode_returns = []
    episode_sharpe = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        rewards = []
        
        done = False
        while not done:
            action = agent.act(state, training=True)
            next_state, reward, done, info = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
            rewards.append(reward)
            
            if len(agent.memory) > 32:
                agent.replay()
        
        episode_returns.append(total_reward)
        if len(rewards) > 1:
            sharpe = np.mean(rewards) / (np.std(rewards) + 1e-8) * np.sqrt(252)
            episode_sharpe.append(sharpe)
        else:
            episode_sharpe.append(0)
    
    return {
        'episode_returns': episode_returns,
        'episode_sharpe': episode_sharpe,
        'final_epsilon': agent.epsilon
    }


def evaluate_rl_agent(agent: DQNTradingAgent, prices: pd.Series,
                     initial_capital: float = 100000) -> Dict[str, float]:
    """
    Evaluate trained RL agent on test data.
    
    Args:
        agent: Trained DQN agent
        prices: Series of test prices
        initial_capital: Starting capital
        
    Returns:
        Dictionary with performance metrics
    """
    env = TradingEnvironment(prices, initial_capital)
    state = env.reset()
    
    returns = []
    done = False
    
    while not done:
        action = agent.act(state, training=False)
        state, reward, done, info = env.step(action)
        returns.append(reward)
    
    total_return = sum(returns)
    sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252) if len(returns) > 1 else 0
    max_drawdown = calculate_max_drawdown_from_returns(returns)
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'total_trades': env.total_trades,
        'final_portfolio_value': info.get('portfolio_value', initial_capital)
    }


def calculate_max_drawdown_from_returns(returns: List[float]) -> float:
    """Calculate maximum drawdown from return series."""
    cumulative = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    return abs(drawdown.min())


if __name__ == "__main__":
    # Example usage
    print("Reinforcement Learning Trading Agent Demo")
    print("=" * 50)
    
    if TORCH_AVAILABLE:
        # Generate sample price data
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        price_series = pd.Series(prices, index=dates)
        
        # Train agent
        print("\nTraining RL agent...")
        results = train_rl_agent(price_series, episodes=50)
        print(f"Training completed. Final epsilon: {results['final_epsilon']:.4f}")
        print(f"Average return: {np.mean(results['episode_returns']):.4f}")
    else:
        print("\nPyTorch not available. Install with: pip install torch")
