"""
Quantitative Analyst Agent
"""

from ..ollama_client import OllamaClient


class QuantAnalyst:
    """Quant Agent - performs technical and statistical analysis"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
    
    def analyze(self, stock: str, thesis: str) -> str:
        """Perform quantitative analysis"""
        system_prompt = """You are a quantitative analyst specializing in technical analysis.
        Use data-driven insights to validate or challenge trading theses.
        Focus on technical indicators, statistical patterns, and probability."""
        
        prompt = f"""
        Stock: {stock}
        Trading Thesis: {thesis}
        
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
