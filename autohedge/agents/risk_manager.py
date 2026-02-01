"""
Risk Manager Agent
"""

import json
from typing import Dict
from ..ollama_client import OllamaClient
from ..models import RiskAssessment
from ..config import Config


class RiskManager:
    """Risk Manager - assesses and manages trading risk"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
    
    def assess_risk(
        self,
        stock: str,
        thesis: str,
        quant_analysis: str,
        allocation: float
    ) -> Dict:
        """Assess risk and approve/reject trade"""
        system_prompt = """You are a risk manager protecting capital.
        Your primary goal is to prevent losses while allowing good opportunities.
        Be conservative but not overly restrictive.
        ALWAYS respond with valid JSON only."""
        
        prompt = f"""
        Stock: {stock}
        Thesis: {thesis}
        Quant Analysis: {quant_analysis}
        Proposed Allocation: ${allocation:,.2f}
        
        Assess the risk and provide your decision in JSON format:
        
        {{
            "risk_level": <1-10, where 10 is highest risk>,
            "decision": "<APPROVED|REJECTED|MODIFY>",
            "position_size_pct": <percentage of allocation to use, 0-100>,
            "risks": ["<list of specific risks identified>"],
            "stop_loss_pct": <recommended stop loss percentage, typically 3-15>
        }}
        
        CRITICAL: 
        - Stop loss should typically be 3-15%, NOT 55%
        - Position size should reflect risk level (higher risk = smaller position)
        - Be specific about risks
        - ONLY return valid JSON, no other text
        """
        
        response = self.client.generate(prompt, system=system_prompt)
        
        # Parse JSON response
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                # Validate stop loss is reasonable
                if data.get("stop_loss_pct", 0) > 20:
                    print("⚠️  Adjusting unrealistic stop loss")
                    data["stop_loss_pct"] = Config.DEFAULT_STOP_LOSS_PCT
                
                return data
        except Exception as e:
            print(f"⚠️  Failed to parse risk assessment: {e}")
        
        # Fallback
        return {
            "risk_level": 5,
            "decision": "MODIFY",
            "position_size_pct": 50,
            "risks": ["Unable to parse detailed risk assessment"],
            "stop_loss_pct": Config.DEFAULT_STOP_LOSS_PCT,
            "raw_response": response
        }
