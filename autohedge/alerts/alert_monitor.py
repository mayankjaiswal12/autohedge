"""
Background Alert Monitor
Continuously evaluates alerts in a separate thread
"""

import time
import threading
from .alert_engine import AlertEngine
from datetime import datetime


class AlertMonitor:
    """Background service to monitor alerts"""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize alert monitor
        
        Args:
            check_interval: Seconds between alert checks (default: 60)
        """
        self.check_interval = check_interval
        self.engine = AlertEngine()
        self.running = False
        self.thread = None
        self.last_check = None
        self.total_checks = 0
        self.total_triggered = 0
    
    def start(self):
        """Start monitoring in background thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print(f"🚀 Alert monitor started (checking every {self.check_interval}s)")
        else:
            print("⚠️  Alert monitor already running")
    
    def stop(self):
        """Stop monitoring"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            print(f"🛑 Alert monitor stopped (Checks: {self.total_checks}, Triggered: {self.total_triggered})")
        else:
            print("ℹ️  Alert monitor not running")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.last_check = datetime.now()
                self.total_checks += 1
                
                # Reload alerts to pick up any changes
                self.engine.load_alerts()
                
                # Evaluate all alerts
                triggered = self.engine.evaluate_all()
                self.total_triggered += triggered
                
                if triggered > 0:
                    print(f"✅ Check #{self.total_checks}: {triggered} alert(s) triggered")
                
            except Exception as e:
                print(f"❌ Alert evaluation error: {e}")
            
            # Sleep in small increments to allow quick shutdown
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def get_status(self) -> dict:
        """Get monitor status"""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "total_checks": self.total_checks,
            "total_triggered": self.total_triggered,
            "active_alerts": len([a for a in self.engine.alerts if a.enabled])
        }
