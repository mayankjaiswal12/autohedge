"""
Portfolio Optimizer - Modern Portfolio Theory Implementation
Implements mean-variance optimization, efficient frontier, and Sharpe ratio maximization
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")


class PortfolioOptimizer:
    """
    Modern Portfolio Theory optimizer for multi-asset portfolios
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer
        
        Args:
            risk_free_rate: Annual risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
        self.returns = None
        self.mean_returns = None
        self.cov_matrix = None
        self.stocks = None
        
    def prepare_data(self, stocks: List[str], start_date: str, end_date: str):
        """
        Download and prepare historical price data
        
        Args:
            stocks: List of stock tickers
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        self.stocks = stocks
        
        # Download data
        try:
            raw_data = yf.download(
                stocks, 
                start=start_date, 
                end=end_date, 
                auto_adjust=True,
                progress=False
            )
            
            if raw_data.empty:
                raise ValueError(f"No data downloaded for {stocks}")
            
            # Extract Close prices
            if len(stocks) == 1:
                if 'Close' in raw_data.columns:
                    prices = raw_data['Close'].to_frame()
                    prices.columns = [stocks[0]]
                else:
                    prices = pd.DataFrame(raw_data)
                    if prices.shape[1] == 1:
                        prices.columns = [stocks[0]]
            else:
                if isinstance(raw_data.columns, pd.MultiIndex):
                    prices = raw_data['Close']
                elif 'Close' in raw_data.columns:
                    prices = raw_data['Close']
                else:
                    prices = raw_data
            
            if not isinstance(prices, pd.DataFrame):
                prices = pd.DataFrame(prices)
                if prices.shape[1] == 1 and len(stocks) == 1:
                    prices.columns = [stocks[0]]
            
            prices = prices.dropna()
            
            if prices.empty:
                raise ValueError("No valid price data after cleaning")
            
            # Calculate daily returns
            self.returns = prices.pct_change().dropna()
            
            if self.returns.empty:
                raise ValueError("Could not calculate returns")
            
            # Calculate annualized mean returns and covariance matrix
            self.mean_returns = self.returns.mean() * 252
            self.cov_matrix = self.returns.cov() * 252
            
        except Exception as e:
            raise ValueError(f"Error preparing data: {str(e)}")
    
    def get_return_range(self) -> Tuple[float, float]:
        """Get the achievable return range for the portfolio"""
        min_return = float(self.mean_returns.min())
        max_return = float(self.mean_returns.max())
        return min_return, max_return
        
    def portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """Calculate portfolio statistics"""
        weights = np.array(weights)
        portfolio_return = np.sum(self.mean_returns.values * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix.values, weights)))
        
        # Avoid division by zero
        if portfolio_volatility == 0:
            sharpe_ratio = 0
        else:
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
            
        return portfolio_return, portfolio_volatility, sharpe_ratio
    
    def negative_sharpe(self, weights: np.ndarray) -> float:
        """Negative Sharpe ratio for minimization"""
        _, _, sharpe = self.portfolio_stats(weights)
        return -sharpe
    
    def portfolio_volatility(self, weights: np.ndarray) -> float:
        """Portfolio volatility for minimization"""
        _, volatility, _ = self.portfolio_stats(weights)
        return volatility
    
    def optimize_sharpe(self) -> Dict:
        """Find portfolio with maximum Sharpe ratio"""
        n_assets = len(self.stocks)
        
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            self.negative_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        if not result.success:
            result = minimize(
                self.negative_sharpe,
                initial_guess,
                method='trust-constr',
                bounds=bounds,
                constraints=constraints
            )
        
        optimal_weights = result.x
        ret, vol, sharpe = self.portfolio_stats(optimal_weights)
        
        # Get achievable range
        min_ret, max_ret = self.get_return_range()
        
        return {
            'weights': dict(zip(self.stocks, optimal_weights)),
            'expected_return': float(ret),
            'volatility': float(vol),
            'sharpe_ratio': float(sharpe),
            'min_possible_return': float(min_ret),
            'max_possible_return': float(max_ret)
        }
    
    def optimize_min_volatility(self) -> Dict:
        """Find minimum variance portfolio"""
        n_assets = len(self.stocks)
        
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            self.portfolio_volatility,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        if not result.success:
            result = minimize(
                self.portfolio_volatility,
                initial_guess,
                method='trust-constr',
                bounds=bounds,
                constraints=constraints
            )
        
        optimal_weights = result.x
        ret, vol, sharpe = self.portfolio_stats(optimal_weights)
        
        min_ret, max_ret = self.get_return_range()
        
        return {
            'weights': dict(zip(self.stocks, optimal_weights)),
            'expected_return': float(ret),
            'volatility': float(vol),
            'sharpe_ratio': float(sharpe),
            'min_possible_return': float(min_ret),
            'max_possible_return': float(max_ret)
        }
    
    def optimize_target_return(self, target_return: float) -> Dict:
        """Find minimum variance portfolio for target return"""
        
        # Check if target is achievable
        min_ret, max_ret = self.get_return_range()
        
        if target_return < min_ret or target_return > max_ret:
            raise ValueError(
                f"Target return {target_return:.2%} is outside achievable range "
                f"[{min_ret:.2%}, {max_ret:.2%}]. "
                f"Please choose a target between {min_ret*100:.1f}% and {max_ret*100:.1f}%"
            )
        
        n_assets = len(self.stocks)
        
        def return_constraint(weights):
            return np.sum(self.mean_returns.values * weights) - target_return
        
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': return_constraint}
        )
        
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            self.portfolio_volatility,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        if not result.success:
            raise ValueError(
                f"Optimization failed for target return {target_return:.2%}. "
                f"Try a value between {min_ret*100:.1f}% and {max_ret*100:.1f}%"
            )
        
        optimal_weights = result.x
        ret, vol, sharpe = self.portfolio_stats(optimal_weights)
        
        return {
            'weights': dict(zip(self.stocks, optimal_weights)),
            'expected_return': float(ret),
            'volatility': float(vol),
            'sharpe_ratio': float(sharpe),
            'min_possible_return': float(min_ret),
            'max_possible_return': float(max_ret)
        }
    
    def calculate_efficient_frontier(self, n_points: int = 50) -> List[Dict]:
        """Calculate efficient frontier points"""
        min_ret = float(self.mean_returns.min())
        max_ret = float(self.mean_returns.max())
        
        # Use slightly smaller range to ensure optimization succeeds
        ret_range = max_ret - min_ret
        min_ret = min_ret + 0.05 * ret_range
        max_ret = max_ret - 0.05 * ret_range
        
        target_returns = np.linspace(min_ret, max_ret, n_points)
        
        frontier = []
        for target in target_returns:
            try:
                result = self.optimize_target_return(target)
                frontier.append({
                    'return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe_ratio': result['sharpe_ratio']
                })
            except:
                continue
        
        return frontier
    
    def calculate_allocations(self, weights: Dict[str, float], capital: float) -> Dict[str, Dict]:
        """Calculate dollar allocations from weights"""
        allocations = {}
        for stock, weight in weights.items():
            dollar_amount = capital * weight
            allocations[stock] = {
                'weight': weight,
                'allocation': dollar_amount,
                'percentage': weight * 100
            }
        return allocations
