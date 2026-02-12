#!/bin/bash

echo "🧪 AutoHedge Alert System Test"
echo "================================"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/api/alerts/monitor/status > /dev/null; then
    echo "❌ Server not running. Start with: make dashboard"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Check monitor status
echo "📊 Monitor Status:"
curl -s http://localhost:8000/api/alerts/monitor/status | python3 -m json.tool
echo ""

# Create test alert
echo "📝 Creating test alert..."
ALERT_ID=$(curl -s -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Alert - AAPL",
    "alert_type": "price",
    "stock": "AAPL",
    "condition": "above",
    "threshold": 1.0,
    "notification_channels": ["web"],
    "cooldown_minutes": 1
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])")

echo "✅ Created alert: $ALERT_ID"
echo ""

# Test the alert
echo "🔔 Testing alert..."
curl -s -X POST "http://localhost:8000/api/alerts/test/$ALERT_ID" | python3 -m json.tool
echo ""

# List notifications
echo "📬 Notifications:"
curl -s http://localhost:8000/api/alerts/notifications | python3 -m json.tool
echo ""

# Cleanup
echo "🧹 Cleaning up test alert..."
curl -s -X DELETE "http://localhost:8000/api/alerts/$ALERT_ID" | python3 -m json.tool

echo ""
echo "✅ Test complete!"
