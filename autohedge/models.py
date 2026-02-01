"""
Data models for AutoHedge
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class AutoHedgeOutput(BaseModel):
    """Output model for AutoHedge analysis"""
    
    id: str = Field(description="Unique trade ID")
    name: Optional[str] = Field(None, description="Analysis name")
    description: Optional[str] = Field(None, description="Analysis description")
    stocks: Optional[List[str]] = Field(None, description="List of stocks analyzed")
    task: Optional[str] = Field(None, description="Original task")
    thesis: Optional[str] = Field(None, description="Trading thesis")
    quant_analysis: Optional[str] = Field(None, description="Quantitative analysis")
    risk_assessment: Optional[str] = Field(None, description="Risk assessment")
    order: Optional[Dict] = Field(None, description="Execution order")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    current_stock: str = Field(description="Current stock being analyzed")


class RiskAssessment(BaseModel):
    """Risk assessment model"""
    
    risk_level: int = Field(ge=1, le=10, description="Risk level 1-10")
    decision: str = Field(description="APPROVED, REJECTED, or MODIFY")
    position_size_pct: float = Field(ge=0, le=100, description="Position size percentage")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    stop_loss_pct: float = Field(description="Stop loss percentage")
    raw_response: Optional[str] = Field(None, description="Raw LLM response")


class Order(BaseModel):
    """Trading order model"""
    
    stock: str
    action: str = Field(description="BUY or SELL")
    quantity: int = Field(ge=0)
    order_type: str = Field(default="LIMIT")
    allocation: float = Field(ge=0)
    stop_loss_pct: float
    risk_level: int = Field(ge=1, le=10)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = Field(default="PENDING")
