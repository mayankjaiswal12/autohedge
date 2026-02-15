"""
Order Engine - Processes and executes trading orders
"""

from typing import Optional, List
from datetime import datetime
from .models import Order, Trade
from .portfolio import PortfolioManager
import json
import os
import uuid


class OrderEngine:
    """Processes trading orders"""
    
    def __init__(self, portfolio_manager: PortfolioManager, orders_file: str = "data/paper_portfolios/orders.json"):
        self.portfolio_manager = portfolio_manager
        self.orders_file = orders_file
        self.trades_file = "data/paper_portfolios/trades.json"
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.load_data()
    
    def load_data(self):
        """Load orders and trades from disk"""
        # Load orders
        if os.path.exists(self.orders_file):
            try:
                with open(self.orders_file, 'r') as f:
                    data = json.load(f)
                    self.orders = [Order(**order) for order in data]
            except Exception as e:
                print(f"⚠️  Error loading orders: {e}")
                self.orders = []
        
        # Load trades
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r') as f:
                    data = json.load(f)
                    self.trades = [Trade(**trade) for trade in data]
            except Exception as e:
                print(f"⚠️  Error loading trades: {e}")
                self.trades = []
    
    def save_data(self):
        """Save orders and trades to disk"""
        try:
            with open(self.orders_file, 'w') as f:
                json.dump([order.dict() for order in self.orders], f, indent=2, default=str)
            
            with open(self.trades_file, 'w') as f:
                json.dump([trade.dict() for trade in self.trades], f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def place_order(self, symbol: str, side: str, quantity: int, order_type: str = "market", 
                    limit_price: Optional[float] = None) -> Order:
        """Place a new order"""
        portfolio = self.portfolio_manager.current_portfolio
        
        if not portfolio:
            raise ValueError("No active portfolio")
        
        # Create order
        order = Order(
            id=f"order-{str(uuid.uuid4())[:8]}",
            portfolio_id=portfolio.id,
            symbol=symbol.upper(),
            order_type=order_type,
            side=side,
            quantity=quantity,
            limit_price=limit_price,
            created_at=datetime.now()
        )
        
        # Validate and execute market orders immediately
        if order_type == "market":
            self._execute_market_order(order)
        
        self.orders.append(order)
        self.save_data()
        
        return order
    
    def _execute_market_order(self, order: Order):
        """Execute market order immediately"""
        try:
            # Get current market price
            from ..data_providers import StockDataManager
            data_manager = StockDataManager(primary="yfinance")
            stock_data = data_manager.get_stock_data(order.symbol)
            current_price = stock_data.get('current_price', 0)
            
            if current_price == 0:
                order.status = "rejected"
                order.rejection_reason = f"Could not get price for {order.symbol}"
                return
            
            # Calculate total cost
            total_cost = current_price * order.quantity
            
            # Validate order
            portfolio = self.portfolio_manager.current_portfolio
            
            if order.side == "buy":
                if total_cost > portfolio.cash_balance:
                    order.status = "rejected"
                    order.rejection_reason = f"Insufficient funds. Need ${total_cost:,.2f}, have ${portfolio.cash_balance:,.2f}"
                    return
            elif order.side == "sell":
                position = self.portfolio_manager.get_position(order.symbol)
                if not position or position.quantity < order.quantity:
                    order.status = "rejected"
                    order.rejection_reason = f"Insufficient shares. Trying to sell {order.quantity}, own {position.quantity if position else 0}"
                    return
            
            # Execute order
            order.filled_price = current_price
            order.filled_quantity = order.quantity
            order.total_cost = total_cost
            order.status = "filled"
            order.filled_at = datetime.now()
            
            # Create trade record
            realized_pnl = None
            
            if order.side == "buy":
                self.portfolio_manager.add_position(order.symbol, order.quantity, current_price)
                self.portfolio_manager.update_cash(-total_cost)
            elif order.side == "sell":
                realized_pnl = self.portfolio_manager.reduce_position(order.symbol, order.quantity)
                self.portfolio_manager.update_cash(total_cost)
            
            trade = Trade(
                id=f"trade-{str(uuid.uuid4())[:8]}",
                portfolio_id=portfolio.id,
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=current_price,
                commission=order.commission,
                total=total_cost,
                realized_pnl=realized_pnl,
                timestamp=datetime.now()
            )
            
            self.trades.append(trade)
            
            # Update position prices
            self.portfolio_manager.update_positions_prices({order.symbol: current_price})
            
            print(f"✅ Order filled: {order.side.upper()} {order.quantity} {order.symbol} @ ${current_price:.2f}")
            
        except Exception as e:
            order.status = "rejected"
            order.rejection_reason = str(e)
            print(f"❌ Order execution failed: {e}")
    
    def get_order_history(self, limit: int = 50) -> List[Order]:
        """Get recent orders"""
        return sorted(self.orders, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_trade_history(self, limit: int = 50) -> List[Trade]:
        """Get recent trades"""
        return sorted(self.trades, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order"""
        for order in self.orders:
            if order.id == order_id and order.status == "pending":
                order.status = "cancelled"
                self.save_data()
                return True
        return False
