"""
Paper Trading Data Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from decimal import Decimal


class Position(BaseModel):
    """Stock position in portfolio"""
    symbol: str
    quantity: int
    average_price: float
    current_price: float = 0.0
    market_value: float = 0.0
    cost_basis: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    
    def update_market_value(self, current_price: float):
        """Update position with current market price"""
        self.current_price = current_price
        self.market_value = self.quantity * current_price
        self.cost_basis = self.quantity * self.average_price
        self.unrealized_pnl = self.market_value - self.cost_basis
        if self.cost_basis > 0:
            self.unrealized_pnl_pct = (self.unrealized_pnl / self.cost_basis) * 100
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "quantity": 20,
                "average_price": 250.00,
                "current_price": 275.50,
                "market_value": 5510.00,
                "cost_basis": 5000.00,
                "unrealized_pnl": 510.00,
                "unrealized_pnl_pct": 10.2
            }
        }


class Order(BaseModel):
    """Trading order"""
    id: str
    portfolio_id: str
    symbol: str
    order_type: Literal["market", "limit"] = "market"
    side: Literal["buy", "sell"]
    quantity: int
    limit_price: Optional[float] = None
    status: Literal["pending", "filled", "cancelled", "rejected"] = "pending"
    filled_price: Optional[float] = None
    filled_quantity: int = 0
    commission: float = 0.0
    total_cost: float = 0.0
    created_at: datetime
    filled_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "order-001",
                "portfolio_id": "portfolio-001",
                "symbol": "AAPL",
                "order_type": "market",
                "side": "buy",
                "quantity": 10,
                "status": "filled",
                "filled_price": 275.50,
                "filled_quantity": 10,
                "commission": 0.00,
                "total_cost": 2755.00
            }
        }


class Trade(BaseModel):
    """Executed trade record"""
    id: str
    portfolio_id: str
    order_id: str
    symbol: str
    side: Literal["buy", "sell"]
    quantity: int
    price: float
    commission: float = 0.0
    total: float
    realized_pnl: Optional[float] = None  # For sells
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "trade-001",
                "portfolio_id": "portfolio-001",
                "order_id": "order-001",
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10,
                "price": 275.50,
                "commission": 0.00,
                "total": 2755.00,
                "timestamp": "2025-02-12T10:30:01"
            }
        }


class Portfolio(BaseModel):
    """Virtual trading portfolio"""
    id: str
    name: str
    starting_capital: float
    cash_balance: float
    positions: List[Position] = []
    total_value: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    total_invested: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    def calculate_totals(self):
        """Calculate portfolio totals"""
        positions_value = sum(p.market_value for p in self.positions)
        self.total_value = self.cash_balance + positions_value
        self.total_invested = positions_value
        self.total_pnl = self.total_value - self.starting_capital
        if self.starting_capital > 0:
            self.total_pnl_pct = (self.total_pnl / self.starting_capital) * 100
        self.updated_at = datetime.now()
    
    class Config:
        schema_extra = {
            "example": {
                "id": "portfolio-001",
                "name": "My Paper Portfolio",
                "starting_capital": 100000.00,
                "cash_balance": 95000.00,
                "total_value": 100510.00,
                "total_pnl": 510.00,
                "total_pnl_pct": 0.51
            }
        }


class PerformanceMetrics(BaseModel):
    """Portfolio performance metrics"""
    total_return: float
    total_return_pct: float
    cash_balance: float
    invested_value: float
    total_value: float
    num_positions: int
    num_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    best_trade: Optional[Trade] = None
    worst_trade: Optional[Trade] = None
    average_trade_pnl: float = 0.0
    total_realized_pnl: float = 0.0
    total_unrealized_pnl: float = 0.0
    
    class Config:
        schema_extra = {
            "example": {
                "total_return": 510.00,
                "total_return_pct": 0.51,
                "cash_balance": 95000.00,
                "invested_value": 5510.00,
                "total_value": 100510.00,
                "num_positions": 1,
                "num_trades": 2,
                "winning_trades": 1,
                "losing_trades": 0,
                "win_rate": 100.0
            }
        }
