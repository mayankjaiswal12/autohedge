"""
Real-time stock data providers
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime
import requests


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
            
            current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
            
            data = {
                "symbol": symbol,
                "current_price": current_price,
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap"),
                "volume": hist['Volume'].iloc[-1] if len(hist) > 0 else None,
                
                # Price changes
                "day_change": self._calculate_change(hist, 1),
                "week_change": self._calculate_change(hist, 5),
                "month_change": self._calculate_change(hist, 20),
                
                # Technical indicators
                "rsi": self._calculate_rsi(hist),
                "sma_20": self._calculate_sma(hist, 20),
                "sma_50": self._calculate_sma(hist, 50),
                "sma_200": self._calculate_sma(hist, 200),
                
                # Fundamentals
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                
                # Financial metrics
                "profit_margins": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "beta": info.get("beta"),
                
                # Analyst data
                "target_mean_price": info.get("targetMeanPrice"),
                "recommendation": info.get("recommendationKey"),
                
                # Company info
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "full_name": info.get("longName"),
                
                # Support/Resistance
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                
                "timestamp": datetime.now().isoformat(),
                "data_source": self.name
            }
            
            return data
            
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}
    
    def _calculate_change(self, hist: pd.DataFrame, periods: int) -> Optional[float]:
        """Calculate percentage change over periods"""
        try:
            if len(hist) > periods:
                old_price = hist['Close'].iloc[-periods-1]
                new_price = hist['Close'].iloc[-1]
                return ((new_price - old_price) / old_price) * 100
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
            return rsi.iloc[-1]
        except:
            return None
    
    def _calculate_sma(self, hist: pd.DataFrame, periods: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(hist) >= periods:
                return hist['Close'].rolling(window=periods).mean().iloc[-1]
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
            print(f"❌ Error fetching data from Alpha Vantage: {e}")
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
        
        print(f"📊 Fetching data for {symbol} from {provider.name}...")
        data = provider.get_stock_data(symbol, **kwargs)
        
        if "error" in data and self.primary == "yfinance":
            print(f"⚠️  Falling back to Alpha Vantage...")
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
        
        formatted = f"""
REAL-TIME MARKET DATA for {data.get('symbol', 'N/A')}
{'='*60}

CURRENT PRICE: ${data.get('current_price', 'N/A'):.2f}

PRICE CHANGES:
- Today: {data.get('day_change', 'N/A'):.2f}%
- Week: {data.get('week_change', 'N/A'):.2f}%
- Month: {data.get('month_change', 'N/A'):.2f}%

TECHNICAL INDICATORS:
- RSI (14): {data.get('rsi', 'N/A'):.2f if data.get('rsi') else 'N/A'}
- SMA 20: ${data.get('sma_20', 'N/A'):.2f if data.get('sma_20') else 'N/A'}
- SMA 50: ${data.get('sma_50', 'N/A'):.2f if data.get('sma_50') else 'N/A'}
- SMA 200: ${data.get('sma_200', 'N/A'):.2f if data.get('sma_200') else 'N/A'}

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
- Target Price: ${data.get('target_mean_price', 'N/A')}
- Recommendation: {data.get('recommendation', 'N/A').upper() if data.get('recommendation') else 'N/A'}

52-WEEK RANGE:
- High: ${data.get('52_week_high', 'N/A')}
- Low: ${data.get('52_week_low', 'N/A')}

COMPANY INFO:
- Sector: {data.get('sector', 'N/A')}
- Industry: {data.get('industry', 'N/A')}
- Market Cap: ${data.get('market_cap', 0):,.0f if data.get('market_cap') else 'N/A'}

Data as of: {data.get('timestamp', 'N/A')}
"""
        return formatted
EOFcat > autohedge/data_providers.py << 'EOF'
"""
Real-time stock data providers
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime
import requests


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
            
            current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
            
            data = {
                "symbol": symbol,
                "current_price": current_price,
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap"),
                "volume": hist['Volume'].iloc[-1] if len(hist) > 0 else None,
                
                # Price changes
                "day_change": self._calculate_change(hist, 1),
                "week_change": self._calculate_change(hist, 5),
                "month_change": self._calculate_change(hist, 20),
                
                # Technical indicators
                "rsi": self._calculate_rsi(hist),
                "sma_20": self._calculate_sma(hist, 20),
                "sma_50": self._calculate_sma(hist, 50),
                "sma_200": self._calculate_sma(hist, 200),
                
                # Fundamentals
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                
                # Financial metrics
                "profit_margins": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "beta": info.get("beta"),
                
                # Analyst data
                "target_mean_price": info.get("targetMeanPrice"),
                "recommendation": info.get("recommendationKey"),
                
                # Company info
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "full_name": info.get("longName"),
                
                # Support/Resistance
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                
                "timestamp": datetime.now().isoformat(),
                "data_source": self.name
            }
            
            return data
            
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}
    
    def _calculate_change(self, hist: pd.DataFrame, periods: int) -> Optional[float]:
        """Calculate percentage change over periods"""
        try:
            if len(hist) > periods:
                old_price = hist['Close'].iloc[-periods-1]
                new_price = hist['Close'].iloc[-1]
                return ((new_price - old_price) / old_price) * 100
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
            return rsi.iloc[-1]
        except:
            return None
    
    def _calculate_sma(self, hist: pd.DataFrame, periods: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(hist) >= periods:
                return hist['Close'].rolling(window=periods).mean().iloc[-1]
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
            print(f"❌ Error fetching data from Alpha Vantage: {e}")
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
        
        print(f"📊 Fetching data for {symbol} from {provider.name}...")
        data = provider.get_stock_data(symbol, **kwargs)
        
        if "error" in data and self.primary == "yfinance":
            print(f"⚠️  Falling back to Alpha Vantage...")
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
        
        formatted = f"""
REAL-TIME MARKET DATA for {data.get('symbol', 'N/A')}
{'='*60}

CURRENT PRICE: ${data.get('current_price', 'N/A'):.2f}

PRICE CHANGES:
- Today: {data.get('day_change', 'N/A'):.2f}%
- Week: {data.get('week_change', 'N/A'):.2f}%
- Month: {data.get('month_change', 'N/A'):.2f}%

TECHNICAL INDICATORS:
- RSI (14): {data.get('rsi', 'N/A'):.2f if data.get('rsi') else 'N/A'}
- SMA 20: ${data.get('sma_20', 'N/A'):.2f if data.get('sma_20') else 'N/A'}
- SMA 50: ${data.get('sma_50', 'N/A'):.2f if data.get('sma_50') else 'N/A'}
- SMA 200: ${data.get('sma_200', 'N/A'):.2f if data.get('sma_200') else 'N/A'}

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
- Target Price: ${data.get('target_mean_price', 'N/A')}
- Recommendation: {data.get('recommendation', 'N/A').upper() if data.get('recommendation') else 'N/A'}

52-WEEK RANGE:
- High: ${data.get('52_week_high', 'N/A')}
- Low: ${data.get('52_week_low', 'N/A')}

COMPANY INFO:
- Sector: {data.get('sector', 'N/A')}
- Industry: {data.get('industry', 'N/A')}
- Market Cap: ${data.get('market_cap', 0):,.0f if data.get('market_cap') else 'N/A'}

Data as of: {data.get('timestamp', 'N/A')}
"""
        return formatted
