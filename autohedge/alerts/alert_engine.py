"""
Alert Engine - Core alert evaluation logic
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .models import AlertRule, AlertNotification
from .notification import NotificationDispatcher
import json
import os


class AlertEngine:
    """Evaluate alert rules and trigger notifications"""
    
    def __init__(self, alerts_file: str = "data/alerts.json"):
        self.alerts_file = alerts_file
        self.alerts: List[AlertRule] = []
        self.dispatcher = NotificationDispatcher()
        self.load_alerts()
    
    def load_alerts(self):
        """Load alerts from JSON file"""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = [AlertRule(**alert) for alert in data]
                print(f"✅ Loaded {len(self.alerts)} alerts from {self.alerts_file}")
            except Exception as e:
                print(f"❌ Error loading alerts: {e}")
                self.alerts = []
        else:
            print(f"ℹ️  No alerts file found at {self.alerts_file}")
            self.alerts = []
    
    def save_alerts(self):
        """Save alerts to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
            with open(self.alerts_file, 'w') as f:
                json.dump(
                    [alert.dict() for alert in self.alerts], 
                    f, 
                    indent=2, 
                    default=str
                )
            print(f"✅ Saved {len(self.alerts)} alerts to {self.alerts_file}")
        except Exception as e:
            print(f"❌ Error saving alerts: {e}")
    
    def add_alert(self, alert: AlertRule) -> AlertRule:
        """Add new alert rule"""
        self.alerts.append(alert)
        self.save_alerts()
        return alert
    
    def update_alert(self, alert_id: str, updates: Dict) -> Optional[AlertRule]:
        """Update existing alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                for key, value in updates.items():
                    if hasattr(alert, key):
                        setattr(alert, key, value)
                self.save_alerts()
                return alert
        return None
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete alert"""
        original_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a.id != alert_id]
        
        if len(self.alerts) < original_count:
            self.save_alerts()
            return True
        return False
    
    def get_alert(self, alert_id: str) -> Optional[AlertRule]:
        """Get alert by ID"""
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def check_alert(self, alert: AlertRule) -> Optional[AlertNotification]:
        """Check if alert condition is met"""
        # Check if alert is enabled
        if not alert.enabled:
            return None
        
        # Check cooldown
        if alert.last_triggered:
            cooldown_delta = timedelta(minutes=alert.cooldown_minutes)
            if datetime.now() - alert.last_triggered < cooldown_delta:
                return None
        
        # Import here to avoid circular import
        from ..data_providers import StockDataManager
        
        # Get current data
        try:
            data_manager = StockDataManager(primary="yfinance")
            
            if alert.alert_type == "price" and alert.stock:
                data = data_manager.get_stock_data(alert.stock)
                current_value = data.get('current_price', 0)
                
                if current_value == 0:
                    print(f"⚠️  Could not get price for {alert.stock}")
                    return None
                
                # Check condition
                triggered = False
                message = ""
                
                if alert.condition == "above" and current_value > alert.threshold:
                    triggered = True
                    message = f"{alert.stock} price ${current_value:.2f} is above threshold ${alert.threshold:.2f}"
                    
                elif alert.condition == "below" and current_value < alert.threshold:
                    triggered = True
                    message = f"{alert.stock} price ${current_value:.2f} is below threshold ${alert.threshold:.2f}"
                
                if triggered:
                    # Update last triggered
                    alert.last_triggered = datetime.now()
                    self.save_alerts()
                    
                    return AlertNotification(
                        alert_id=alert.id,
                        alert_name=alert.name,
                        message=message,
                        channels=alert.notification_channels,
                        timestamp=datetime.now(),
                        stock=alert.stock,
                        current_value=current_value,
                        threshold=alert.threshold
                    )
        
        except Exception as e:
            print(f"❌ Error checking alert {alert.name}: {e}")
        
        return None
    
    def evaluate_all(self) -> int:
        """Evaluate all enabled alerts"""
        triggered_count = 0
        
        for alert in self.alerts:
            if alert.enabled:
                notification = self.check_alert(alert)
                if notification:
                    channels = self.dispatcher.send(notification)
                    print(f"🔔 Alert triggered: {alert.name} → {', '.join(channels)}")
                    triggered_count += 1
        
        return triggered_count
