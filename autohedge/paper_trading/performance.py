"""
Performance Analytics - Calculate portfolio performance metrics
"""

from typing import List, Optional
from .models import Trade, Portfolio, PerformanceMetrics
from datetime import datetime


class PerformanceAnalytics:
    """Calculate portfolio performance metrics"""
    
    def __init__(self, portfolio: Portfolio, trades: List[Trade]):
        self.portfolio = portfolio
        self.trades = trades
    
    def calculate_metrics(self) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        # Basic totals
        total_return = self.portfolio.total_pnl
        total_return_pct = self.portfolio.total_pnl_pct
        
        # Trade statistics
        completed_trades = [t for t in self.trades if t.side == "sell"]
        num_trades = len(self.trades)
        
        # Realized P&L from sells
        total_realized_pnl = sum(t.realized_pnl for t in completed_trades if t.realized_pnl)
        
        # Unrealized P&L from positions
        total_unrealized_pnl = sum(p.unrealized_pnl for p in self.portfolio.positions)
        
        # Win/loss analysis
        winning_trades = [t for t in completed_trades if t.realized_pnl and t.realized_pnl > 0]
        losing_trades = [t for t in completed_trades if t.realized_pnl and t.realized_pnl < 0]
        
        win_rate = (len(winning_trades) / len(completed_trades) * 100) if completed_trades else 0.0
        
        # Best and worst trades
        best_trade = max(completed_trades, key=lambda t: t.realized_pnl or 0) if completed_trades else None
        worst_trade = min(completed_trades, key=lambda t: t.realized_pnl or 0) if completed_trades else None
        
        # Average trade P&L
        average_trade_pnl = (total_realized_pnl / len(completed_trades)) if completed_trades else 0.0
        
        return PerformanceMetrics(
            total_return=total_return,
            total_return_pct=total_return_pct,
            cash_balance=self.portfolio.cash_balance,
            invested_value=self.portfolio.total_invested,
            total_value=self.portfolio.total_value,
            num_positions=len(self.portfolio.positions),
            num_trades=num_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            best_trade=best_trade,
            worst_trade=worst_trade,
            average_trade_pnl=average_trade_pnl,
            total_realized_pnl=total_realized_pnl,
            total_unrealized_pnl=total_unrealized_pnl
        )
    
    def get_daily_returns(self) -> List[dict]:
        """Calculate daily portfolio returns"""
        # Group trades by date
        daily_data = {}
        
        for trade in self.trades:
            date = trade.timestamp.date()
            if date not in daily_data:
                daily_data[date] = {
                    'date': date.isoformat(),
                    'trades': 0,
                    'volume': 0,
                    'pnl': 0
                }
            
            daily_data[date]['trades'] += 1
            daily_data[date]['volume'] += trade.total
            if trade.realized_pnl:
                daily_data[date]['pnl'] += trade.realized_pnl
        
        return sorted(daily_data.values(), key=lambda x: x['date'])
    
    def get_position_allocation(self) -> List[dict]:
        """Get portfolio allocation by position"""
        if self.portfolio.total_value == 0:
            return []
        
        allocations = []
        
        # Cash allocation
        cash_pct = (self.portfolio.cash_balance / self.portfolio.total_value) * 100
        allocations.append({
            'name': 'Cash',
            'value': self.portfolio.cash_balance,
            'percentage': cash_pct
        })
        
        # Position allocations
        for position in self.portfolio.positions:
            pct = (position.market_value / self.portfolio.total_value) * 100
            allocations.append({
                'name': position.symbol,
                'value': position.market_value,
                'percentage': pct
            })
        
        return sorted(allocations, key=lambda x: x['value'], reverse=True)
