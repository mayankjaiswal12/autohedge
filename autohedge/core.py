"""
Core AutoHedge system
"""

import json
import os
from typing import List, Optional
from datetime import datetime

from .config import Config
from .models import AutoHedgeOutput
from .ollama_client import OllamaClient
from .agents.director import TradingDirector
from .agents.quant import QuantAnalyst
from .agents.risk_manager import RiskManager
from .agents.executor import ExecutionAgent


class AutoHedge:
    """Main AutoHedge system using Ollama"""
    
    def __init__(
        self,
        stocks: List[str],
        ollama_url: Optional[str] = None,
        model: Optional[str] = None,
        allocation: Optional[float] = None
    ):
        self.stocks = stocks
        self.allocation = allocation or Config.DEFAULT_ALLOCATION
        
        # Priority: parameter > environment variable > config default
        final_url = ollama_url or Config.get_ollama_url()
        final_model = model or Config.get_ollama_model()
        
        print(f"🔧 Initializing AutoHedge with:")
        print(f"   Ollama URL: {final_url}")
        print(f"   Model: {final_model}")
        print(f"   Allocation: ${self.allocation:,.2f}")
        
        # Initialize Ollama client
        self.ollama = OllamaClient(base_url=final_url, model=final_model)
        
        # Initialize agents
        self.director = TradingDirector(stocks, self.ollama)
        self.quant = QuantAnalyst(self.ollama)
        self.risk_manager = RiskManager(self.ollama)
        self.executor = ExecutionAgent(self.ollama)
    
    def run(self, task: str, stock: Optional[str] = None) -> AutoHedgeOutput:
        """Run the complete trading pipeline"""
        current_stock = stock or self.stocks[0]
        
        print(f"\n{'='*80}")
        print(f"🏦 AutoHedge Analysis: {current_stock}")
        print(f"{'='*80}\n")
        
        # Step 1: Generate thesis
        print(f"🎯 Director: Generating thesis...")
        thesis = self.director.generate_thesis(task, current_stock)
        
        # Step 2: Quant analysis
        print(f"📊 Quant: Analyzing {current_stock}...")
        quant_analysis = self.quant.analyze(current_stock, thesis)
        
        # Step 3: Risk assessment
        print(f"⚠️  Risk Manager: Assessing risk...")
        risk_assessment = self.risk_manager.assess_risk(
            current_stock, thesis, quant_analysis, self.allocation
        )
        
        # Step 4: Create order
        print(f"🔨 Executor: Creating order...")
        order = self.executor.create_order(
            current_stock, risk_assessment, self.allocation, thesis
        )
        
        # Create output
        return AutoHedgeOutput(
            id=f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=f"{current_stock} Analysis",
            stocks=self.stocks,
            task=task,
            thesis=thesis,
            quant_analysis=quant_analysis,
            risk_assessment=json.dumps(risk_assessment, indent=2),
            order=order,
            timestamp=datetime.now().isoformat(),
            current_stock=current_stock
        )
