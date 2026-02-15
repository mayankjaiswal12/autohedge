"""
Notification Handlers for Alerts
Supports Email, Slack, and Web notifications
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict
from datetime import datetime
import os

# Import models at the top to avoid circular import
from .models import AlertNotification


class EmailNotifier:
    """Send email notifications via SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        self.enabled = all([self.sender_email, self.sender_password, self.recipient_email])
    
    def send(self, subject: str, body: str) -> bool:
        """Send email notification"""
        if not self.enabled:
            print("⚠️  Email credentials not configured. Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL env vars.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"🤖 AutoHedge Alert: {subject}"
            
            # Create HTML body
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #2c3e50;">AutoHedge Alert</h2>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <pre style="white-space: pre-wrap;">{body}</pre>
                    </div>
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 20px;">
                        This is an automated alert from AutoHedge.
                    </p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            return False


class SlackNotifier:
    """Send Slack notifications via webhook"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)
    
    def send(self, message: str) -> bool:
        """Send Slack notification"""
        if not self.enabled:
            print("⚠️  Slack webhook not configured. Set SLACK_WEBHOOK_URL env var.")
            return False
        
        try:
            payload = {
                "text": f"🤖 *AutoHedge Alert*\n{message}",
                "username": "AutoHedge",
                "icon_emoji": ":chart_with_upwards_trend:"
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Slack notification sent")
                return True
            else:
                print(f"❌ Slack send failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Slack send failed: {e}")
            return False


class NotificationDispatcher:
    """Dispatch notifications to multiple channels"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.slack_notifier = SlackNotifier()
        self.web_notifications: List[Dict] = []
        self.max_web_notifications = 100
    
    def send(self, notification: AlertNotification):
        """Send notification to all specified channels"""
        message = self._format_message(notification)
        subject = f"{notification.alert_name} - {notification.stock or 'Portfolio'}"
        
        success_channels = []
        
        for channel in notification.channels:
            if channel == "email":
                if self.email_notifier.send(subject, message):
                    success_channels.append("email")
                    
            elif channel == "slack":
                if self.slack_notifier.send(message):
                    success_channels.append("slack")
                    
            elif channel == "web":
                self._add_web_notification(notification, message)
                success_channels.append("web")
        
        return success_channels
    
    def _add_web_notification(self, notification: AlertNotification, message: str):
        """Add notification to web queue"""
        self.web_notifications.insert(0, {
            "id": f"{notification.alert_id}_{notification.timestamp.timestamp()}",
            "alert_id": notification.alert_id,
            "alert_name": notification.alert_name,
            "message": message,
            "timestamp": notification.timestamp.isoformat(),
            "stock": notification.stock,
            "current_value": notification.current_value,
            "threshold": notification.threshold,
            "read": False
        })
        
        if len(self.web_notifications) > self.max_web_notifications:
            self.web_notifications = self.web_notifications[:self.max_web_notifications]
    
    def _format_message(self, notification: AlertNotification) -> str:
        """Format notification message"""
        return f"""
Alert: {notification.alert_name}
Stock: {notification.stock or 'Portfolio'}
Current Value: ${notification.current_value:.2f}
Threshold: ${notification.threshold:.2f}
Time: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{notification.message}
        """.strip()
    
    def get_web_notifications(self, limit: int = 50, unread_only: bool = False) -> List[Dict]:
        """Get web notifications"""
        notifications = self.web_notifications
        
        if unread_only:
            notifications = [n for n in notifications if not n.get('read', False)]
        
        return notifications[:limit]
    
    def mark_as_read(self, notification_id: str):
        """Mark notification as read"""
        for notif in self.web_notifications:
            if notif['id'] == notification_id:
                notif['read'] = True
                break
    
    def clear_all(self):
        """Clear all web notifications"""
        self.web_notifications = []
