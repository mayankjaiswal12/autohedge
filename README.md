# 🤖 AutoHedge - AI-Powered Hedge Fund System

> A complete AI-powered trading system with multi-agent architecture, portfolio optimization, paper trading, and real-time alerts.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v8.0.0-orange.svg)](https://github.com/mayankjaiswal12/autohedge)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Version History](#version-history)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

AutoHedge is a sophisticated AI-powered hedge fund system that combines:
- **Multi-Agent Trading** - AI agents collaborate to make trading decisions
- **Portfolio Optimization** - Modern Portfolio Theory for optimal allocation
- **Paper Trading** - Risk-free virtual trading with $100k starting capital
- **Alert System** - Real-time notifications via Email, Slack, and Web
- **Backtesting Engine** - Test strategies on historical data
- **Live Analysis** - Real-time AI-powered market analysis

**Tech Stack:**
- Backend: Python, FastAPI
- AI: Ollama (qwen2.5:7b local LLM)
- Data: yfinance, pandas, numpy, scipy
- Frontend: HTML/CSS/JavaScript, Chart.js
- Containers: Docker, Docker Compose

---

## ✨ Features

### 🤖 Multi-Agent Trading System (v1.0.0)
- **Director Agent** - Generates high-level trading thesis
- **Quant Analyst** - Performs technical and statistical analysis
- **Risk Manager** - Assesses risk and determines position sizing
- **Executor** - Creates and validates trade orders
- Collaborative decision-making with local LLM

### 📊 Real-Time Market Data (v2.0.0)
- Live stock prices and fundamentals via yfinance
- Technical indicators (RSI, MACD, SMA, EMA)
- Alpha Vantage fallback for reliability
- Formatted data optimized for AI consumption

### 📈 Backtesting Engine (v3.0.0)
- Historical performance testing
- Multiple technical indicators
- Stop loss & take profit simulation
- Performance metrics (Sharpe ratio, max drawdown, profit factor)
- Detailed trade logs with P&L tracking

### 🌐 Web Dashboard (v4.0.0)
- Real-time market data cards
- Interactive backtesting interface
- Analysis history viewer
- Results visualization with charts
- Responsive design

### 🧠 Live AI Analysis (v5.0.0)
- Browser-based agent execution
- Real-time trading thesis generation
- Dynamic risk assessment
- Actionable order recommendations
- Analysis history tracking

### 💼 Portfolio Optimizer (v6.0.0)
- Modern Portfolio Theory implementation
- Efficient frontier calculation (50 points)
- Multiple optimization strategies:
  - Maximum Sharpe Ratio
  - Minimum Volatility
  - Target Return with validation
- Interactive charts (efficient frontier, allocation pie)
- Dollar allocation calculator
- Correlation analysis
- Return range validation

### 🔔 Alert System (v7.0.0)
- Real-time price monitoring
- Multi-channel notifications:
  - Web Dashboard (built-in)
  - Email via SMTP
  - Slack via webhooks
- Alert management (create, edit, delete, toggle)
- Cooldown system to prevent spam
- Manual alert testing
- Background monitoring service
- Alert history tracking

### 💰 Paper Trading (v8.0.0)
- Virtual portfolio with $100,000 starting capital
- Real-time market order execution
- Position tracking and management
- Cash balance management
- P&L calculation (realized & unrealized)
- Trade and order history
- Performance analytics
- Quick buy/sell interface
- Portfolio reset functionality

---

## 📦 Version History

| Version | Release | Features |
|---------|---------|----------|
| **v1.0.0** | ✅ Released | Base multi-agent trading system (4 agents) |
| **v2.0.0** | ✅ Released | Real-time stock data (yfinance + Alpha Vantage) |
| **v3.0.0** | ✅ Released | Backtesting engine with technical indicators |
| **v4.0.0** | ✅ Released | Web dashboard with live market data |
| **v5.0.0** | ✅ Released | Live AI analysis via web interface |
| **v6.0.0** | ✅ Released | Portfolio optimizer (Modern Portfolio Theory) |
| **v7.0.0** | ✅ Released | Alert system (Email/Slack/Web notifications) |
| **v8.0.0** | ✅ Released | Paper trading system (virtual portfolio) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AutoHedge System                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │  Web         │◄────►│  FastAPI     │                    │
│  │  Dashboard   │      │  Backend     │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│         ┌─────────────────────┼─────────────────────┐       │
│         ▼                     ▼                     ▼       │
│  ┌──────────────┐      ┌──────────────┐    ┌─────────────┐│
│  │ Multi-Agent  │      │  Portfolio   │    │   Paper     ││
│  │  Trading     │      │  Optimizer   │    │  Trading    ││
│  └──────┬───────┘      └──────┬───────┘    └──────┬──────┘│
│         │                     │                    │       │
│         ▼                     ▼                    ▼       │
│  ┌──────────────┐      ┌──────────────┐    ┌─────────────┐│
│  │  Backtester  │      │    Alert     │    │Performance  ││
│  │              │      │   System     │    │ Analytics   ││
│  └──────────────┘      └──────────────┘    └─────────────┘│
│         │                     │                    │       │
│         └─────────────────────┼────────────────────┘       │
│                               ▼                            │
│                     ┌──────────────────┐                   │
│                     │   Market Data    │                   │
│                     │   (yfinance)     │                   │
│                     └──────────────────┘                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Ollama Container (qwen2.5:7b)           │  │
│  │              Local LLM for AI Agents                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Git installed
- 8GB+ RAM recommended
- Internet connection for market data

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/mayankjaiswal12/autohedge.git
cd autohedge

# 2. Build and start containers
docker-compose build
docker-compose up -d

# 3. Pull the LLM model (one-time setup)
docker exec ollama ollama pull qwen2.5:7b

# 4. Start the dashboard
make dashboard

# 5. Open in browser
open http://localhost:8000
```

### First Time Setup

```bash
# Optional: Configure email/Slack alerts
cp .env.example .env
nano .env  # Add your credentials

# Restart to load environment
docker-compose restart
```

---

## 💻 Usage

### Access the System

```bash
# Start the dashboard
make dashboard

# Access different modules
open http://localhost:8000/                 # Dashboard
open http://localhost:8000/paper-trading    # Paper Trading
open http://localhost:8000/portfolio        # Portfolio Optimizer
open http://localhost:8000/alerts           # Alert Management
open http://localhost:8000/analysis         # Live AI Analysis
open http://localhost:8000/backtest         # Backtesting
open http://localhost:8000/history          # History
```

### Paper Trading

```bash
# Start with $100,000 virtual capital
# 1. Navigate to Paper Trading page
# 2. Click "+ Place Order"
# 3. Enter:
#    - Symbol: AAPL
#    - Side: Buy
#    - Quantity: 10
# 4. Click "Place Order"
# 5. Watch your portfolio grow! 📈
```

### Portfolio Optimization

```bash
# 1. Navigate to Portfolio Optimizer
# 2. Enter stock symbols (e.g., AAPL, MSFT, GOOGL, AMZN)
# 3. Set date range (e.g., 2024-01-01 to 2025-01-01)
# 4. Set capital amount (e.g., $100,000)
# 5. Choose optimization type:
#    - Max Sharpe Ratio (best risk-adjusted returns)
#    - Min Volatility (lowest risk)
#    - Target Return (specify desired return)
# 6. Click "Optimize Portfolio"
# 7. View efficient frontier and optimal allocation
```

### Alert System

```bash
# 1. Navigate to Alerts page
# 2. Click "+ Create Alert"
# 3. Configure:
#    - Name: "AAPL High Price"
#    - Stock: AAPL
#    - Condition: Above
#    - Threshold: 200
#    - Channels: Web, Email, Slack
# 4. Click "Save Alert"
# 5. Alert will trigger when condition is met
# 6. Test alerts manually with "Test" button
```

### CLI Commands

```bash
# Run live analysis
docker exec -it autohedge python -m autohedge.main trade \
  --stocks NVDA \
  --task "Analyze NVIDIA for swing trading" \
  --allocation 50000

# Run backtest
docker exec -it autohedge python -m autohedge.main backtest \
  --stocks AAPL MSFT \
  --start 2024-01-01 \
  --end 2025-01-01 \
  --capital 100000

# Check logs
docker logs autohedge -f
docker logs ollama -f
```

---

## 📡 API Reference

### Paper Trading API

```bash
# Get portfolio
GET /api/paper/portfolio

# Place order
POST /api/paper/order
{
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10
}

# Get trades
GET /api/paper/trades

# Get orders
GET /api/paper/orders

# Get performance
GET /api/paper/performance

# Reset portfolio
POST /api/paper/portfolio/reset
```

### Portfolio Optimizer API

```bash
# Optimize portfolio
POST /api/portfolio/optimize
{
  "stocks": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "capital": 100000,
  "optimization_type": "sharpe"
}

# Get optimization history
GET /api/portfolio/history
```

### Alert System API

```bash
# List alerts
GET /api/alerts

# Create alert
POST /api/alerts
{
  "name": "AAPL Price Alert",
  "alert_type": "price",
  "stock": "AAPL",
  "condition": "above",
  "threshold": 200,
  "notification_channels": ["web", "email"],
  "cooldown_minutes": 60
}

# Update alert
PUT /api/alerts/{alert_id}

# Delete alert
DELETE /api/alerts/{alert_id}

# Toggle alert
POST /api/alerts/{alert_id}/toggle

# Test alert
POST /api/alerts/test/{alert_id}

# Get notifications
GET /api/alerts/notifications

# Monitor status
GET /api/alerts/monitor/status
```

### Market Data API

```bash
# Get stock data
GET /api/stock/{symbol}

# Get multiple stocks
GET /api/stocks?symbols=AAPL,MSFT,GOOGL
```

### Backtesting API

```bash
# Run backtest
POST /api/backtest
{
  "stocks": ["AAPL"],
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "capital": 100000,
  "stop_loss": 5.0,
  "take_profit": 10.0
}

# Get history
GET /api/history
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Email Notifications (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=alerts@example.com

# Slack Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Alert Monitor
ALERT_CHECK_INTERVAL=60  # Seconds between checks
```

### Email Setup (Gmail)

1. Enable 2-Factor Authentication
2. Create App Password at [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Add credentials to `.env`
4. Restart: `docker-compose restart`

See [ALERT_SETUP.md](ALERT_SETUP.md) for detailed instructions.

### Slack Setup

1. Create Slack App at [https://api.slack.com/apps](https://api.slack.com/apps)
2. Enable Incoming Webhooks
3. Add webhook URL to `.env`
4. Restart: `docker-compose restart`

---

## 🛠️ Development

### Project Structure

```
autohedge/
├── autohedge/
│   ├── agents/              # AI trading agents
│   │   ├── director.py
│   │   ├── quant.py
│   │   ├── risk_manager.py
│   │   └── executor.py
│   ├── alerts/              # Alert system
│   │   ├── models.py
│   │   ├── alert_engine.py
│   │   ├── notification.py
│   │   └── alert_monitor.py
│   ├── paper_trading/       # Paper trading system
│   │   ├── models.py
│   │   ├── portfolio.py
│   │   ├── order_engine.py
│   │   └── performance.py
│   ├── dashboard/           # Web interface
│   │   ├── routes.py
│   │   ├── templates/
│   │   └── static/
│   ├── backtesting.py       # Backtesting engine
│   ├── data_providers.py    # Market data
│   ├── portfolio_optimizer.py  # Portfolio optimization
│   ├── core.py              # Main system
│   └── main.py              # CLI entry
├── data/                    # Data storage
│   ├── alerts.json
│   ├── paper_portfolios/
│   └── outputs/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── Makefile
└── README.md
```

### Adding New Features

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make changes
# ... edit files ...

# 3. Test locally
docker-compose restart
make dashboard

# 4. Commit
git add .
git commit -m "feat: Add new feature"

# 5. Create pull request
git push origin feature/my-new-feature
```

### Running Tests

```bash
# Test paper trading
./test_alerts.sh

# Test imports
docker exec autohedge python -c "from autohedge.paper_trading import PortfolioManager; print('OK')"

# Test API endpoints
curl http://localhost:8000/api/paper/portfolio | jq
curl http://localhost:8000/api/alerts | jq
```

---

## 🐛 Troubleshooting

### Container Issues

```bash
# Container won't start
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker logs autohedge --tail 50
docker logs ollama --tail 50

# Container exiting immediately
docker-compose up  # Run without -d to see errors
```

### Dashboard Issues

```bash
# Dashboard won't start
docker ps  # Check if containers are running
docker logs autohedge  # Check for errors

# Port already in use
lsof -i :8000  # Find process using port 8000
kill -9 <PID>  # Kill the process
```

### Alert Issues

```bash
# Email not sending
# - Check SMTP credentials in .env
# - Use Gmail App Password (not regular password)
# - Restart containers after .env changes

# Slack not working
# - Verify webhook URL in .env
# - Test webhook: curl -X POST $SLACK_WEBHOOK_URL -d '{"text":"test"}'

# Monitor not running
curl http://localhost:8000/api/alerts/monitor/status
```

### Paper Trading Issues

```bash
# Orders failing
# - Check stock symbol is valid
# - Check sufficient cash balance
# - Check market hours (9:30 AM - 4:00 PM ET)

# Prices not updating
# - Verify internet connection
# - Check yfinance is working
# - Restart container

# Portfolio reset
curl -X POST http://localhost:8000/api/paper/portfolio/reset
```

### Common Errors

| Error | Solution |
|-------|----------|
| `No such container: autohedge` | Run `docker-compose up -d` |
| `Port 8000 already in use` | Kill process or change port |
| `Could not get price for {symbol}` | Check symbol or market hours |
| `Insufficient funds` | Reduce order size or reset portfolio |
| `Alert monitor not running` | Restart container |

---

## 📚 Documentation

- [Alert Setup Guide](ALERT_SETUP.md) - Complete email/Slack configuration
- [v8.0.0 Implementation Plan](v8_implementation_plan.md) - Paper trading details
- [v7.0.0 Implementation Plan](v7_implementation_plan.md) - Alert system details
- [v6.0.0 Implementation Guide](v6_implementation_guide.md) - Portfolio optimizer details

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Tests
- `chore:` Maintenance

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **yfinance** - Market data
- **FastAPI** - Web framework
- **Chart.js** - Visualization
- **Pydantic** - Data validation
- **scipy** - Portfolio optimization

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mayankjaiswal12/autohedge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mayankjaiswal12/autohedge/discussions)
- **Email**: mayankjaiswal12@example.com

---

## 🎯 Roadmap

### Planned Features

- **v9.0.0** - Live Trading Integration
  - Broker API integration (Alpaca, Interactive Brokers)
  - Real order execution
  - Account synchronization

- **v10.0.0** - Advanced Analytics
  - Machine learning predictions
  - Sentiment analysis
  - Options trading support

- **v11.0.0** - Mobile App
  - iOS app
  - Android app
  - Push notifications

---

## 📊 Stats

- **Lines of Code**: ~15,000+
- **Files**: 50+
- **Dependencies**: 15+
- **API Endpoints**: 40+
- **Development Time**: Extensive
- **Version**: 8.0.0
- **Status**: Production Ready ✅

---

## 🌟 Star History

If you find AutoHedge useful, please star the repository!

---

<div align="center">

**Built with ❤️ by Mayank Jaiswal**

[⬆ Back to Top](#-autohedge---ai-powered-hedge-fund-system)

</div>