"""
Alert System Data Models
"""

from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime


class AlertRule(BaseModel):
    """Alert rule definition"""
    id: str
    name: str
    alert_type: Literal["price", "portfolio", "technical"]
    condition: Literal["above", "below", "crosses_above", "crosses_below"]
    threshold: float
    stock: Optional[str] = None
    enabled: bool = True
    notification_channels: List[str]  # ["email", "slack", "web"]
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "alert-001",
                "name": "AAPL High Price Alert",
                "alert_type": "price",
                "condition": "above",
                "threshold": 200.0,
                "stock": "AAPL",
                "enabled": True,
                "notification_channels": ["email", "slack", "web"],
                "cooldown_minutes": 60,
                "created_at": "2025-01-01T12:00:00"
            }
        }


class AlertNotification(BaseModel):
    """Notification to be sent"""
    alert_id: str
    alert_name: str
    message: str
    channels: List[str]
    timestamp: datetime
    stock: Optional[str] = None
    current_value: float
    threshold: float
    
    class Config:
        schema_extra = {
            "example": {
                "alert_id": "alert-001",
                "alert_name": "AAPL High Price Alert",
                "message": "AAPL price $205.50 is above threshold $200.00",
                "channels": ["email", "web"],
                "timestamp": "2025-01-01T12:30:00",
                "stock": "AAPL",
                "current_value": 205.50,
                "threshold": 200.00
            }
        }
