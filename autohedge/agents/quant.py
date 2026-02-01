"""
Quantitative Analyst Agent with Real-Time Data
"""

from ..ollama_client import OllamaClient
from ..data_providers import StockDataManager


class QuantAnalyst:
    """Quant Agent - performs technical and statistical analysis with real data"""
    
    def __init__(self, ollama_client: OllamaClient, use_real_data: bool = True):
        self.client = ollama_client
        self.use_real_data = use_real_data
        
        if self.use_real_data:
            self.data_manager = StockDataManager(primary="yfinance")
    
    def analyze(self, stock: str, thesis: str) -> str:
        """Perform quantitative analysis with real-time data"""
        
        market_data = ""
        if self.use_real_data:
            try:
                stock_data = self.data_manager.get_stock_data(stock)
                market_data = self.data_manager.format_for_analysis(stock_data)
            except Exception as e:
                print(f"⚠️  Could not fetch real-time data: {e}")
                market_data = "Real-time data unavailable"
        
        system_prompt = """You are a quantitative analyst specializing in technical analysis.
        Use data-driven insights to validate or challenge trading theses.
        Focus on technical indicators, statistical patterns, and probability."""
        
        prompt = f"""
        Stock: {stock}
        Trading Thesis: {thesis}
        
        {market_data}
        
        Provide quantitative analysis covering:
        
        1. TECHNICAL INDICATORS: Key indicators to monitor (RSI, MACD, Moving Averages)
        2. PRICE PATTERNS: Chart patterns and trend analysis
        3. VOLUME ANALYSIS: Volume trends and their implications
        4. STATISTICAL METRICS: Volatility, beta, correlation with market
        5. PROBABILITY ASSESSMENT: Likelihood of thesis success (percentage)
        6. DATA POINTS: Specific levels to watch (support/resistance)
        
        Be analytical and provide specific numbers where possible.
        Challenge the thesis if technical indicators suggest otherwise.
        Keep analysis focused and actionable (400-600 words).
        """
        
        return self.client.generate(prompt, system=system_prompt)
