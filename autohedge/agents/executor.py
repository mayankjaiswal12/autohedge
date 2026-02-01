"""
Execution Agent
"""

from typing import Dict
from datetime import datetime
from ..ollama_client import OllamaClient
from ..models import Order


class ExecutionAgent:
    """Execution Agent - creates executable orders"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
    
    def create_order(
        self,
        stock: str,
        risk_assessment: Dict,
        allocation: float,
        thesis: str = ""
    ) -> Dict:
        """Create executable order"""
        
        if risk_assessment.get("decision") == "REJECTED":
            return {
                "status": "REJECTED",
                "reason": "Risk assessment rejected trade",
                "stock": stock
            }
        
        # Calculate position size
        position_size_pct = risk_assessment.get("position_size_pct", 50)
        position_size = allocation * (position_size_pct / 100)
        
        # Determine action from thesis (simple heuristic)
        action = "BUY"
        if thesis and any(word in thesis.lower() for word in ["sell", "short", "bearish"]):
            action = "SELL"
        
        # Create order
        order = Order(
            stock=stock,
            action=action,
            quantity=int(position_size / 100),  # Simplified: assume $100/share
            order_type="LIMIT",
            allocation=position_size,
            stop_loss_pct=risk_assessment.get("stop_loss_pct", 5),
            risk_level=risk_assessment.get("risk_level", 5),
            status="PENDING"
        )
        
        return order.dict()
