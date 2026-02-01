"""
Real-time stock data providers
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime
import requests


def convert_value(value):
    """Convert numpy types to native Python types"""
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


class YFinanceProvider:
    """Yahoo Finance data provider"""

    def __init__(self):
        self.name = "Yahoo Finance"

    def get_stock_data(self, symbol: str, period: str = "1mo") -> Dict:
        """Get comprehensive stock data"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period=period)

            current_price = float(hist['Close'].iloc[-1]) if len(hist) > 0 else None

            data = {
                "symbol": symbol,
                "current_price": convert_value(current_price),
                "currency": info.get("currency", "USD"),
                "market_cap": convert_value(info.get("marketCap")),
                "volume": convert_value(int(hist['Volume'].iloc[-1])) if len(hist) > 0 else None,
                "day_change": convert_value(self._calculate_change(hist, 1)),
                "week_change": convert_value(self._calculate_change(hist, 5)),
                "month_change": convert_value(self._calculate_change(hist, 20)),
                "rsi": convert_value(self._calculate_rsi(hist)),
                "sma_20": convert_value(self._calculate_sma(hist, 20)),
                "sma_50": convert_value(self._calculate_sma(hist, 50)),
                "sma_200": convert_value(self._calculate_sma(hist, 200)),
                "pe_ratio": convert_value(info.get("trailingPE")),
                "forward_pe": convert_value(info.get("forwardPE")),
                "peg_ratio": convert_value(info.get("pegRatio")),
                "price_to_book": convert_value(info.get("priceToBook")),
                "dividend_yield": convert_value(info.get("dividendYield")),
                "profit_margins": convert_value(info.get("profitMargins")),
                "revenue_growth": convert_value(info.get("revenueGrowth")),
                "earnings_growth": convert_value(info.get("earningsGrowth")),
                "beta": convert_value(info.get("beta")),
                "target_mean_price": convert_value(info.get("targetMeanPrice")),
                "recommendation": info.get("recommendationKey"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "full_name": info.get("longName"),
                "52_week_high": convert_value(info.get("fiftyTwoWeekHigh")),
                "52_week_low": convert_value(info.get("fiftyTwoWeekLow")),
                "timestamp": datetime.now().isoformat(),
                "data_source": self.name
            }

            return data

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}

    def _calculate_change(self, hist: pd.DataFrame, periods: int) -> Optional[float]:
        """Calculate percentage change over periods"""
        try:
            if len(hist) > periods:
                old_price = hist['Close'].iloc[-periods - 1]
                new_price = hist['Close'].iloc[-1]
                return float(((new_price - old_price) / old_price) * 100)
        except:
            pass
        return None

    def _calculate_rsi(self, hist: pd.DataFrame, periods: int = 14) -> Optional[float]:
        """Calculate RSI"""
        try:
            if len(hist) < periods:
                return None
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return None

    def _calculate_sma(self, hist: pd.DataFrame, periods: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(hist) >= periods:
                return float(hist['Close'].rolling(window=periods).mean().iloc[-1])
        except:
            pass
        return None

    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get data for multiple stocks"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_data(symbol)
        return results


class AlphaVantageProvider:
    """Alpha Vantage data provider (backup)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo"
        self.base_url = "https://www.alphavantage.co/query"
        self.name = "Alpha Vantage"

    def get_stock_data(self, symbol: str) -> Dict:
        """Get stock quote from Alpha Vantage"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "Global Quote" in data:
                quote = data["Global Quote"]
                return {
                    "symbol": symbol,
                    "current_price": float(quote.get("05. price", 0)),
                    "day_change": float(quote.get("09. change", 0)),
                    "day_change_percent": quote.get("10. change percent", ""),
                    "volume": int(quote.get("06. volume", 0)),
                    "timestamp": datetime.now().isoformat(),
                    "data_source": self.name
                }
            else:
                return {"error": "No data returned", "symbol": symbol}

        except Exception as e:
            print(f"Error fetching data from Alpha Vantage: {e}")
            return {"error": str(e), "symbol": symbol}


class StockDataManager:
    """Unified stock data manager"""

    def __init__(self, primary: str = "yfinance", alpha_vantage_key: Optional[str] = None):
        self.yfinance = YFinanceProvider()
        self.alphavantage = AlphaVantageProvider(alpha_vantage_key)
        self.primary = primary
        self.providers = {
            "yfinance": self.yfinance,
            "alphavantage": self.alphavantage
        }

    def get_stock_data(self, symbol: str, **kwargs) -> Dict:
        """Get stock data with fallback"""
        provider = self.providers.get(self.primary, self.yfinance)

        print(f"Fetching data for {symbol} from {provider.name}...")
        data = provider.get_stock_data(symbol, **kwargs)

        if "error" in data and self.primary == "yfinance":
            print(f"Falling back to Alpha Vantage...")
            data = self.alphavantage.get_stock_data(symbol)

        return data

    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get data for multiple stocks"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_data(symbol)
        return results

    def format_for_analysis(self, data: Dict) -> str:
        """Format stock data for AI analysis"""
        if "error" in data:
            return f"Error fetching data for {data.get('symbol')}: {data['error']}"

        price = data.get('current_price', 0) or 0
        day_chg = data.get('day_change') or 0
        week_chg = data.get('week_change') or 0
        month_chg = data.get('month_change') or 0
        rsi = data.get('rsi')
        sma_20 = data.get('sma_20')
        sma_50 = data.get('sma_50')
        sma_200 = data.get('sma_200')
        market_cap = data.get('market_cap') or 0

        formatted = f"""
REAL-TIME MARKET DATA for {data.get('symbol', 'N/A')}
============================================================
CURRENT PRICE: ${price:.2f}

PRICE CHANGES:
- Today: {day_chg:.2f}%
- Week: {week_chg:.2f}%
- Month: {month_chg:.2f}%

TECHNICAL INDICATORS:
- RSI (14): {f'{rsi:.2f}' if rsi else 'N/A'}
- SMA 20: {f'${sma_20:.2f}' if sma_20 else 'N/A'}
- SMA 50: {f'${sma_50:.2f}' if sma_50 else 'N/A'}
- SMA 200: {f'${sma_200:.2f}' if sma_200 else 'N/A'}

FUNDAMENTALS:
- P/E Ratio: {data.get('pe_ratio', 'N/A')}
- Forward P/E: {data.get('forward_pe', 'N/A')}
- PEG Ratio: {data.get('peg_ratio', 'N/A')}
- Price/Book: {data.get('price_to_book', 'N/A')}
- Dividend Yield: {data.get('dividend_yield', 'N/A')}
- Beta: {data.get('beta', 'N/A')}

GROWTH METRICS:
- Revenue Growth: {data.get('revenue_growth', 'N/A')}
- Earnings Growth: {data.get('earnings_growth', 'N/A')}
- Profit Margins: {data.get('profit_margins', 'N/A')}

ANALYST DATA:
- Target Price: {f"${data.get('target_mean_price')}" if data.get('target_mean_price') else 'N/A'}
- Recommendation: {data.get('recommendation', 'N/A').upper() if data.get('recommendation') else 'N/A'}

52-WEEK RANGE:
- High: {f"${data.get('52_week_high')}" if data.get('52_week_high') else 'N/A'}
- Low: {f"${data.get('52_week_low')}" if data.get('52_week_low') else 'N/A'}

COMPANY INFO:
- Sector: {data.get('sector', 'N/A')}
- Industry: {data.get('industry', 'N/A')}
- Market Cap: ${market_cap:,.0f}

Data as of: {data.get('timestamp', 'N/A')}
"""
        return formatted
