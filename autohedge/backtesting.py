"""
Backtesting Engine for AutoHedge
"""

import json
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class BacktestTrade:
    """Represents a single backtest trade"""
    
    def __init__(
        self,
        stock: str,
        entry_date: str,
        entry_price: float,
        exit_date: str,
        exit_price: float,
        action: str,
        quantity: int,
        allocation: float,
        stop_loss_pct: float
    ):
        self.stock = stock
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.action = action
        self.quantity = quantity
        self.allocation = allocation
        self.stop_loss_pct = stop_loss_pct
        
        # Calculate P&L
        if action == "BUY":
            self.pnl = (exit_price - entry_price) * quantity
        else:
            self.pnl = (entry_price - exit_price) * quantity
        
        self.pnl_pct = (self.pnl / allocation) * 100
        self.is_winner = self.pnl > 0
    
    def to_dict(self) -> Dict:
        return {
            "stock": self.stock,
            "entry_date": self.entry_date,
            "entry_price": self.entry_price,
            "exit_date": self.exit_date,
            "exit_price": self.exit_price,
            "action": self.action,
            "quantity": self.quantity,
            "allocation": self.allocation,
            "stop_loss_pct": self.stop_loss_pct,
            "pnl": round(self.pnl, 2),
            "pnl_pct": round(self.pnl_pct, 2),
            "is_winner": self.is_winner
        }


class BacktestResult:
    """Stores and calculates backtest performance metrics"""
    
    def __init__(self, trades: List[BacktestTrade], initial_capital: float):
        self.trades = trades
        self.initial_capital = initial_capital
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate all performance metrics"""
        if not self.trades:
            self.total_trades = 0
            self.winning_trades = 0
            self.losing_trades = 0
            self.win_rate = 0
            self.total_pnl = 0
            self.total_return_pct = 0
            self.avg_pnl = 0
            self.avg_win = 0
            self.avg_loss = 0
            self.max_win = 0
            self.max_loss = 0
            self.sharpe_ratio = 0
            self.max_drawdown = 0
            self.profit_factor = 0
            self.final_capital = self.initial_capital
            return
        
        # Basic metrics
        self.total_trades = len(self.trades)
        self.winning_trades = sum(1 for t in self.trades if t.is_winner)
        self.losing_trades = self.total_trades - self.winning_trades
        self.win_rate = (self.winning_trades / self.total_trades) * 100
        
        # P&L metrics
        self.total_pnl = sum(t.pnl for t in self.trades)
        self.final_capital = self.initial_capital + self.total_pnl
        self.total_return_pct = (self.total_pnl / self.initial_capital) * 100
        self.avg_pnl = self.total_pnl / self.total_trades
        
        # Win/Loss metrics
        wins = [t.pnl for t in self.trades if t.is_winner]
        losses = [t.pnl for t in self.trades if not t.is_winner]
        
        self.avg_win = np.mean(wins) if wins else 0
        self.avg_loss = np.mean(losses) if losses else 0
        self.max_win = max(wins) if wins else 0
        self.max_loss = min(losses) if losses else 0
        
        # Profit factor
        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0
        self.profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Sharpe ratio (simplified)
        returns = [t.pnl_pct for t in self.trades]
        if len(returns) > 1:
            self.sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            self.sharpe_ratio = 0
        
        # Max drawdown
        self._calculate_max_drawdown()
    
    def _calculate_max_drawdown(self):
        """Calculate maximum drawdown"""
        capital = self.initial_capital
        peak = capital
        self.max_drawdown = 0
        
        for trade in self.trades:
            capital += trade.pnl
            if capital > peak:
                peak = capital
            drawdown = (peak - capital) / peak * 100
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
    
    def print_report(self):
        """Print formatted backtest report"""
        print("\n" + "=" * 80)
        print("📊 BACKTEST REPORT")
        print("=" * 80)
        
        print(f"\n💰 CAPITAL:")
        print(f"   Initial Capital:  ${self.initial_capital:,.2f}")
        print(f"   Final Capital:    ${self.final_capital:,.2f}")
        print(f"   Total P&L:        ${self.total_pnl:,.2f}")
        print(f"   Total Return:     {self.total_return_pct:.2f}%")
        
        print(f"\n📈 TRADE STATISTICS:")
        print(f"   Total Trades:     {self.total_trades}")
        print(f"   Winning Trades:   {self.winning_trades}")
        print(f"   Losing Trades:    {self.losing_trades}")
        print(f"   Win Rate:         {self.win_rate:.2f}%")
        
        print(f"\n💵 P&L BREAKDOWN:")
        print(f"   Average P&L:      ${self.avg_pnl:,.2f}")
        print(f"   Average Win:      ${self.avg_win:,.2f}")
        print(f"   Average Loss:     ${self.avg_loss:,.2f}")
        print(f"   Largest Win:      ${self.max_win:,.2f}")
        print(f"   Largest Loss:     ${self.max_loss:,.2f}")
        
        print(f"\n📉 RISK METRICS:")
        print(f"   Sharpe Ratio:     {self.sharpe_ratio:.2f}")
        print(f"   Max Drawdown:     {self.max_drawdown:.2f}%")
        print(f"   Profit Factor:    {self.profit_factor:.2f}")
        
        print(f"\n📋 TRADE LOG:")
        print("-" * 80)
        print(f"{'#':<4} {'Stock':<8} {'Action':<6} {'Entry':>10} {'Exit':>10} {'P&L':>12} {'Return':>8}")
        print("-" * 80)
        
        for i, trade in enumerate(self.trades, 1):
            pnl_str = f"${trade.pnl:,.2f}"
            color = "✅" if trade.is_winner else "❌"
            print(f"{i:<4} {trade.stock:<8} {trade.action:<6} ${trade.entry_price:>9.2f} ${trade.exit_price:>9.2f} {pnl_str:>12} {trade.pnl_pct:>7.2f}% {color}")
        
        print("-" * 80)
        print("=" * 80)
    
    def to_dict(self) -> Dict:
        """Convert results to dictionary"""
        return {
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_pnl": self.total_pnl,
            "total_return_pct": self.total_return_pct,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "avg_pnl": self.avg_pnl,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "max_win": self.max_win,
            "max_loss": self.max_loss,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "profit_factor": self.profit_factor,
            "trades": [t.to_dict() for t in self.trades]
        }


class Backtester:
    """Main backtesting engine"""
    
    def __init__(
        self,
        initial_capital: float = 100000,
        stop_loss_pct: float = 5.0,
        take_profit_pct: float = 10.0,
        holding_period_days: int = 30
    ):
        self.initial_capital = initial_capital
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.holding_period_days = holding_period_days
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        print(f"📥 Fetching historical data for {symbol}...")
        try:
            df = yf.download(symbol, start=start_date, end=end_date)
            if df.empty:
                print(f"❌ No data found for {symbol}")
            else:
                print(f"✅ Got {len(df)} days of data for {symbol}")
            return df
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return pd.DataFrame()
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trading signals based on technical indicators"""
        if df.empty:
            return df
        
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Volume moving average
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # Generate BUY/SELL signals
        df['Signal'] = 0  # 0 = Hold, 1 = Buy, -1 = Sell
        
        # BUY: Price crosses above SMA_20, RSI < 70, MACD > Signal
        buy_condition = (
            (df['Close'] > df['SMA_20']) &
            (df['Close'].shift(1) <= df['SMA_20'].shift(1)) &
            (df['RSI'] < 70) &
            (df['MACD'] > df['MACD_Signal'])
        )
        
        # SELL: Price crosses below SMA_20, RSI > 30, MACD < Signal
        sell_condition = (
            (df['Close'] < df['SMA_20']) &
            (df['Close'].shift(1) >= df['SMA_20'].shift(1)) &
            (df['RSI'] > 30) &
            (df['MACD'] < df['MACD_Signal'])
        )
        
        df.loc[buy_condition, 'Signal'] = 1
        df.loc[sell_condition, 'Signal'] = -1
        
        return df
    
    def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        allocation_pct: float = 100.0
    ) -> BacktestResult:
        """Run backtest for a single stock"""
        
        print(f"\n{'=' * 80}")
        print(f"🔄 BACKTESTING: {symbol}")
        print(f"   Period: {start_date} to {end_date}")
        print(f"   Capital: ${self.initial_capital:,.2f}")
        print(f"   Stop Loss: {self.stop_loss_pct}%")
        print(f"   Take Profit: {self.take_profit_pct}%")
        print(f"{'=' * 80}\n")
        
        # Get historical data
        df = self.get_historical_data(symbol, start_date, end_date)
        if df.empty:
            return BacktestResult([], self.initial_capital)
        
        # Calculate signals
        df = self.calculate_signals(df)
        
        # Run simulation
        trades = []
        capital = self.initial_capital * (allocation_pct / 100)
        position = None  # Current open position
        
        for i in range(1, len(df)):
            current_date = df.index[i].strftime('%Y-%m-%d')
            current_price = float(df['Close'].iloc[i])
            signal = int(df['Signal'].iloc[i])
            
            # Check stop loss / take profit on open position
            if position:
                entry_price = position['entry_price']
                
                # Stop Loss
                if current_price <= entry_price * (1 - self.stop_loss_pct / 100):
                    trade = BacktestTrade(
                        stock=symbol,
                        entry_date=position['entry_date'],
                        entry_price=entry_price,
                        exit_date=current_date,
                        exit_price=current_price,
                        action="BUY",
                        quantity=position['quantity'],
                        allocation=position['allocation'],
                        stop_loss_pct=self.stop_loss_pct
                    )
                    trades.append(trade)
                    capital += trade.pnl
                    position = None
                    print(f"   �� Stop Loss hit on {current_date}: ${current_price:.2f} (P&L: ${trade.pnl:,.2f})")
                    continue
                
                # Take Profit
                if current_price >= entry_price * (1 + self.take_profit_pct / 100):
                    trade = BacktestTrade(
                        stock=symbol,
                        entry_date=position['entry_date'],
                        entry_price=entry_price,
                        exit_date=current_date,
                        exit_price=current_price,
                        action="BUY",
                        quantity=position['quantity'],
                        allocation=position['allocation'],
                        stop_loss_pct=self.stop_loss_pct
                    )
                    trades.append(trade)
                    capital += trade.pnl
                    position = None
                    print(f"   🎯 Take Profit hit on {current_date}: ${current_price:.2f} (P&L: ${trade.pnl:,.2f})")
                    continue
                
                # Holding period expired
                days_held = (pd.Timestamp(current_date) - pd.Timestamp(position['entry_date'])).days
                if days_held >= self.holding_period_days:
                    trade = BacktestTrade(
                        stock=symbol,
                        entry_date=position['entry_date'],
                        entry_price=entry_price,
                        exit_date=current_date,
                        exit_price=current_price,
                        action="BUY",
                        quantity=position['quantity'],
                        allocation=position['allocation'],
                        stop_loss_pct=self.stop_loss_pct
                    )
                    trades.append(trade)
                    capital += trade.pnl
                    position = None
                    print(f"   ⏰ Holding period expired on {current_date}: ${current_price:.2f} (P&L: ${trade.pnl:,.2f})")
                    continue
            
            # Open new position on BUY signal
            if signal == 1 and position is None and capital > 0:
                quantity = int(capital / current_price)
                if quantity > 0:
                    position = {
                        'entry_date': current_date,
                        'entry_price': current_price,
                        'quantity': quantity,
                        'allocation': quantity * current_price
                    }
                    print(f"   🟢 BUY on {current_date}: {quantity} shares @ ${current_price:.2f}")
        
        # Close any remaining position at end
        if position:
            current_price = float(df['Close'].iloc[-1])
            current_date = df.index[-1].strftime('%Y-%m-%d')
            trade = BacktestTrade(
                stock=symbol,
                entry_date=position['entry_date'],
                entry_price=position['entry_price'],
                exit_date=current_date,
                exit_price=current_price,
                action="BUY",
                quantity=position['quantity'],
                allocation=position['allocation'],
                stop_loss_pct=self.stop_loss_pct
            )
            trades.append(trade)
            capital += trade.pnl
            print(f"   🔚 Closing position on {current_date}: ${current_price:.2f} (P&L: ${trade.pnl:,.2f})")
        
        return BacktestResult(trades, self.initial_capital)
    
    def run_multi_stock_backtest(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, BacktestResult]:
        """Run backtest for multiple stocks"""
        results = {}
        allocation_per_stock = 100.0 / len(symbols)
        
        for symbol in symbols:
            results[symbol] = self.run_backtest(
                symbol, start_date, end_date, allocation_per_stock
            )
        
        return results
    
    def save_results(self, result: BacktestResult, filename: str):
        """Save backtest results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"✅ Results saved to: {filename}")
