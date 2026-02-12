# AutoHedge Alert System Setup Guide

## 🚀 Quick Start

The Alert System works out of the box with **web notifications**. Email and Slack are optional but recommended!

---

## 📧 Email Notifications Setup (Gmail)

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification"

### Step 2: Create App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Other (Custom name)"
3. Name it "AutoHedge"
4. Copy the 16-character password

### Step 3: Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env file
nano .env
```

Add your credentials:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop  # Your app password
RECIPIENT_EMAIL=your-email@gmail.com
```

### Step 4: Restart Docker
```bash
docker-compose down
docker-compose up -d
```

### Test Email
Create an alert with "Email" channel selected and click "Test" button!

---

## 💬 Slack Notifications Setup

### Step 1: Create Slack App
1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name it "AutoHedge" and select your workspace

### Step 2: Enable Incoming Webhooks
1. In your app settings, go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to **On**
3. Click "Add New Webhook to Workspace"
4. Select the channel where alerts should appear
5. Click "Allow"
6. Copy the Webhook URL (looks like: `https://hooks.slack.com/services/T00/B00/XXX`)

### Step 3: Configure Environment
```bash
# Edit .env file
nano .env
```

Add webhook:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 4: Restart Docker
```bash
docker-compose down
docker-compose up -d
```

### Test Slack
Create an alert with "Slack" channel selected and click "Test" button!

---

## 🔧 Advanced Configuration

### Custom SMTP Server (Non-Gmail)

For other email providers:

**Outlook/Hotmail:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Custom Server:**
```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587  # or 465 for SSL
```

### Alert Check Interval

Change how often alerts are checked (in seconds):
```env
ALERT_CHECK_INTERVAL=30  # Check every 30 seconds
```

Restart after changes:
```bash
docker-compose restart
```

---

## 📊 Monitor Status

Check if the alert monitor is running:
```bash
curl http://localhost:8000/api/alerts/monitor/status
```

Should return:
```json
{
  "status": "success",
  "data": {
    "running": true,
    "check_interval": 60,
    "total_checks": 42,
    "total_triggered": 3,
    "active_alerts": 5
  }
}
```

---

## 🧪 Testing Alerts

### Test Without Waiting for Condition
1. Go to http://localhost:8000/alerts
2. Create an alert
3. Click the "Test" button
4. Alert will trigger immediately (ignores cooldown)

### Test Real Conditions
1. Create alert with realistic threshold
2. Wait for market to hit condition
3. Check notifications panel

---

## 🐛 Troubleshooting

### Email Not Sending
```bash
# Check logs
docker logs autohedge | grep -i email

# Common issues:
# - Wrong app password (must be 16 chars from Google)
# - 2FA not enabled
# - "Less secure apps" blocking (use app password instead)
```

### Slack Not Sending
```bash
# Check logs
docker logs autohedge | grep -i slack

# Common issues:
# - Wrong webhook URL
# - Webhook expired/revoked
# - Channel deleted
```

### Monitor Not Running
```bash
# Check status
curl http://localhost:8000/api/alerts/monitor/status

# Restart container
docker-compose restart
```

### Alerts Not Triggering
- Check alert is **enabled** (green toggle)
- Check **cooldown period** hasn't blocked it
- Check **stock symbol** is correct
- Check **threshold** is realistic for current price
- Use **Test** button to verify

---

## 💡 Tips

1. **Start with Web notifications** - they always work
2. **Test alerts** before relying on them
3. **Set realistic cooldowns** (60+ minutes recommended)
4. **Monitor the monitor** - check status occasionally
5. **Use descriptive names** for alerts

---

## 🔐 Security Notes

- Never commit `.env` file to git (it's in `.gitignore`)
- Use app passwords, not your main password
- Rotate credentials periodically
- Limit webhook URLs to trusted apps only

---

## 📚 API Reference

### Create Alert
```bash
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AAPL Price Alert",
    "alert_type": "price",
    "stock": "AAPL",
    "condition": "above",
    "threshold": 200.0,
    "notification_channels": ["email", "slack", "web"],
    "cooldown_minutes": 60
  }'
```

### List Alerts
```bash
curl http://localhost:8000/api/alerts
```

### Toggle Alert
```bash
curl -X POST http://localhost:8000/api/alerts/{alert_id}/toggle
```

### Test Alert
```bash
curl -X POST http://localhost:8000/api/alerts/{alert_id}/test
```

### Get Notifications
```bash
curl http://localhost:8000/api/alerts/notifications
```

---

## ✅ Success Checklist

- [ ] Web notifications working
- [ ] Email configured and tested
- [ ] Slack configured and tested
- [ ] Monitor status shows "running"
- [ ] Test alert triggers successfully
- [ ] Real alert triggers on condition
- [ ] Cooldown prevents spam
- [ ] Multiple channels work together

---

Need help? Check the logs:
```bash
docker logs autohedge --tail 100 -f
```
