"""
Trading Director Agent with Real-Time Data
"""

import os
from typing import List
from ..ollama_client import OllamaClient
from ..data_providers import StockDataManager


class TradingDirector:
    """Director Agent - creates trading thesis with real-time data"""
    
    def __init__(
        self, 
        stocks: List[str],
        ollama_client: OllamaClient,
        output_dir: str = "outputs",
        use_real_data: bool = True
    ):
        self.stocks = stocks
        self.client = ollama_client
        self.output_dir = output_dir
        self.use_real_data = use_real_data
        
        if self.use_real_data:
            self.data_manager = StockDataManager(primary="yfinance")
        
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_thesis(self, task: str, stock: str) -> str:
        """Generate trading thesis with real-time market data"""
        
        market_data = ""
        if self.use_real_data:
            try:
                stock_data = self.data_manager.get_stock_data(stock)
                market_data = self.data_manager.format_for_analysis(stock_data)
            except Exception as e:
                print(f"⚠️  Could not fetch real-time data: {e}")
                market_data = "Real-time data unavailable"
        
        system_prompt = """You are an expert hedge fund director with 20+ years of experience.
        Analyze stocks with a focus on fundamentals, market trends, and risk-adjusted returns.
        Provide clear, actionable trading theses backed by reasoning."""
        
        prompt = f"""
        Task: {task}
        Stock: {stock}
        
        {market_data}
        
        Generate a comprehensive trading thesis including:
        
        1. MARKET CONTEXT: Current market environment and sector trends
        2. COMPANY ANALYSIS: Fundamentals, competitive position, recent developments
        3. OPPORTUNITY/RISK: Key catalysts and potential risks
        4. RECOMMENDATION: Clear buy/sell/hold recommendation with reasoning
        5. PRICE TARGETS: Entry, target, and stop-loss levels
        
        Be specific, analytical, and focused on risk-adjusted returns.
        Keep the thesis concise but thorough (500-800 words).
        """
        
        return self.client.generate(prompt, system=system_prompt)
