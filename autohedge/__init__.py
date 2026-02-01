"""
AutoHedge - Autonomous AI Hedge Fund using Ollama with Real-Time Data
"""

from .core import AutoHedge
from .models import AutoHedgeOutput
from .ollama_client import OllamaClient
from .data_providers import StockDataManager, YFinanceProvider, AlphaVantageProvider
from .agents.director import TradingDirector
from .agents.quant import QuantAnalyst
from .agents.risk_manager import RiskManager
from .agents.executor import ExecutionAgent

__version__ = "2.0.0"
__all__ = [
    "AutoHedge",
    "AutoHedgeOutput",
    "OllamaClient",
    "StockDataManager",
    "YFinanceProvider",
    "AlphaVantageProvider",
    "TradingDirector",
    "QuantAnalyst",
    "RiskManager",
    "ExecutionAgent",
]
