"""
Portfolio Manager - Manages virtual portfolio state
"""

from typing import Optional, List
from datetime import datetime
from .models import Portfolio, Position
import json
import os


class PortfolioManager:
    """Manages portfolio operations"""
    
    def __init__(self, portfolio_dir: str = "data/paper_portfolios"):
        self.portfolio_dir = portfolio_dir
        os.makedirs(portfolio_dir, exist_ok=True)
        self.current_portfolio: Optional[Portfolio] = None
    
    def create_portfolio(self, name: str, starting_capital: float) -> Portfolio:
        """Create new portfolio"""
        portfolio = Portfolio(
            id=f"portfolio-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=name,
            starting_capital=starting_capital,
            cash_balance=starting_capital,
            positions=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        portfolio.calculate_totals()
        self.current_portfolio = portfolio
        self.save_portfolio(portfolio)
        
        print(f"✅ Created portfolio '{name}' with ${starting_capital:,.2f}")
        return portfolio
    
    def load_portfolio(self, portfolio_id: str = "default") -> Optional[Portfolio]:
        """Load portfolio from disk"""
        filepath = os.path.join(self.portfolio_dir, f"{portfolio_id}.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    portfolio = Portfolio(**data)
                    self.current_portfolio = portfolio
                    print(f"✅ Loaded portfolio '{portfolio.name}'")
                    return portfolio
            except Exception as e:
                print(f"❌ Error loading portfolio: {e}")
                return None
        else:
            print(f"ℹ️  No portfolio found at {filepath}")
            return None
    
    def save_portfolio(self, portfolio: Portfolio):
        """Save portfolio to disk"""
        filepath = os.path.join(self.portfolio_dir, f"{portfolio.id}.json")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(portfolio.dict(), f, indent=2, default=str)
            
            # Also save as 'default' for easy loading
            default_path = os.path.join(self.portfolio_dir, "default.json")
            with open(default_path, 'w') as f:
                json.dump(portfolio.dict(), f, indent=2, default=str)
                
        except Exception as e:
            print(f"❌ Error saving portfolio: {e}")
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for symbol"""
        if not self.current_portfolio:
            return None
        
        for position in self.current_portfolio.positions:
            if position.symbol == symbol:
                return position
        return None
    
    def add_position(self, symbol: str, quantity: int, price: float):
        """Add or update position"""
        if not self.current_portfolio:
            raise ValueError("No active portfolio")
        
        position = self.get_position(symbol)
        
        if position:
            # Update existing position (average price)
            total_cost = (position.quantity * position.average_price) + (quantity * price)
            new_quantity = position.quantity + quantity
            position.average_price = total_cost / new_quantity
            position.quantity = new_quantity
        else:
            # Create new position
            position = Position(
                symbol=symbol,
                quantity=quantity,
                average_price=price
            )
            self.current_portfolio.positions.append(position)
        
        self.save_portfolio(self.current_portfolio)
    
    def reduce_position(self, symbol: str, quantity: int) -> float:
        """Reduce or remove position, returns realized P&L"""
        if not self.current_portfolio:
            raise ValueError("No active portfolio")
        
        position = self.get_position(symbol)
        
        if not position:
            raise ValueError(f"No position found for {symbol}")
        
        if quantity > position.quantity:
            raise ValueError(f"Cannot sell {quantity} shares, only own {position.quantity}")
        
        # Calculate realized P&L
        realized_pnl = (position.current_price - position.average_price) * quantity
        
        # Update or remove position
        position.quantity -= quantity
        
        if position.quantity == 0:
            self.current_portfolio.positions.remove(position)
        
        self.save_portfolio(self.current_portfolio)
        
        return realized_pnl
    
    def update_positions_prices(self, price_data: dict):
        """Update all positions with current prices"""
        if not self.current_portfolio:
            return
        
        for position in self.current_portfolio.positions:
            if position.symbol in price_data:
                position.update_market_value(price_data[position.symbol])
        
        self.current_portfolio.calculate_totals()
        self.save_portfolio(self.current_portfolio)
    
    def update_cash(self, amount: float):
        """Update cash balance"""
        if not self.current_portfolio:
            raise ValueError("No active portfolio")
        
        self.current_portfolio.cash_balance += amount
        self.current_portfolio.calculate_totals()
        self.save_portfolio(self.current_portfolio)
    
    def reset_portfolio(self):
        """Reset portfolio to starting capital"""
        if not self.current_portfolio:
            raise ValueError("No active portfolio")
        
        self.current_portfolio.cash_balance = self.current_portfolio.starting_capital
        self.current_portfolio.positions = []
        self.current_portfolio.calculate_totals()
        self.save_portfolio(self.current_portfolio)
        
        print(f"✅ Portfolio reset to ${self.current_portfolio.starting_capital:,.2f}")
