"""
AutoHedge - Autonomous AI Hedge Fund using Ollama
"""

from .core import AutoHedge
from .models import AutoHedgeOutput
from .ollama_client import OllamaClient
from .agents.director import TradingDirector
from .agents.quant import QuantAnalyst
from .agents.risk_manager import RiskManager
from .agents.executor import ExecutionAgent

__version__ = "1.0.0"
__all__ = [
    "AutoHedge",
    "AutoHedgeOutput",
    "OllamaClient",
    "TradingDirector",
    "QuantAnalyst",
    "RiskManager",
    "ExecutionAgent",
]
