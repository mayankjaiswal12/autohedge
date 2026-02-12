"""
Dashboard API routes
"""

import json
import os
import glob
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..backtesting import Backtester
from ..data_providers import StockDataManager
from ..portfolio_optimizer import PortfolioOptimizer
from ..alerts.alert_engine import AlertEngine
from ..alerts.models import AlertRule
import uuid


# Initialize FastAPI app
app = FastAPI(title="AutoHedge Dashboard")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUTS_DIR = os.getenv("OUTPUT_DIR", "outputs")

# Setup templates and static files
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Request models
class TradeRequest(BaseModel):
    stocks: List[str]
    task: str
    allocation: float = 50000


class BacktestRequest(BaseModel):
    stocks: List[str]
    start_date: str
    end_date: str
    capital: float = 100000
    stop_loss: float = 5.0
    take_profit: float = 10.0
    holding_period: int = 30


class LiveAnalysisRequest(BaseModel):
    stock: str
    task: str
    allocation: float = 50000


class PortfolioOptimizeRequest(BaseModel):
    """Request model for portfolio optimization"""
    stocks: List[str]
    start_date: str
    end_date: str
    capital: float = 100000
    optimization_type: str = "sharpe"
    target_return: Optional[float] = None


# ============================================================
# Page Routes
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/backtest", response_class=HTMLResponse)
async def backtest_page(request: Request):
    """Backtest page"""
    return templates.TemplateResponse("backtest.html", {"request": request})


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Trade history page"""
    return templates.TemplateResponse("history.html", {"request": request})


@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """Live analysis page"""
    return templates.TemplateResponse("analysis.html", {"request": request})


@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request):
    """Portfolio optimizer page"""
    return templates.TemplateResponse("portfolio.html", {"request": request})


# ============================================================
# API Routes
# ============================================================

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get real-time stock data"""
    try:
        manager = StockDataManager(primary="yfinance")
        data = manager.get_stock_data(symbol)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/stocks")
async def get_multiple_stocks(symbols: str = "AAPL,NVDA,MSFT,GOOGL"):
    """Get data for multiple stocks"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        manager = StockDataManager(primary="yfinance")
        results = manager.get_multiple_stocks(symbol_list)
        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """Run a backtest"""
    try:
        backtester = Backtester(
            initial_capital=request.capital,
            stop_loss_pct=request.stop_loss,
            take_profit_pct=request.take_profit,
            holding_period_days=request.holding_period
        )

        results = {}
        for stock in request.stocks:
            result = backtester.run_backtest(
                symbol=stock,
                start_date=request.start_date,
                end_date=request.end_date
            )
            results[stock] = result.to_dict()

            # Save results
            filename = os.path.join(
                OUTPUTS_DIR,
                f"backtest_{stock}_{request.start_date}_to_{request.end_date}.json"
            )
            os.makedirs(OUTPUTS_DIR, exist_ok=True)
            backtester.save_results(result, filename)

        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/analysis")
async def run_live_analysis(request: LiveAnalysisRequest):
    """Run live AI analysis using Ollama"""
    try:
        from ..core import AutoHedge

        system = AutoHedge(
            stocks=[request.stock],
            allocation=request.allocation
        )

        result = system.run(task=request.task, stock=request.stock)

        # Parse risk assessment
        risk_data = json.loads(result.risk_assessment)

        response_data = {
            "id": result.id,
            "stock": result.current_stock,
            "task": result.task,
            "thesis": result.thesis,
            "quant_analysis": result.quant_analysis,
            "risk_assessment": risk_data,
            "order": result.order,
            "timestamp": result.timestamp
        }

        # Save analysis
        filename = os.path.join(OUTPUTS_DIR, f"analysis_{result.id}.json")
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(response_data, f, indent=2)

        return {"status": "success", "data": response_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/portfolio/optimize")
async def optimize_portfolio(request: PortfolioOptimizeRequest):
    """Run portfolio optimization"""
    try:
        optimizer = PortfolioOptimizer(risk_free_rate=0.02)
        
        # Prepare data
        optimizer.prepare_data(
            stocks=request.stocks,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Run optimization based on type
        if request.optimization_type == "sharpe":
            result = optimizer.optimize_sharpe()
        elif request.optimization_type == "min_vol":
            result = optimizer.optimize_min_volatility()
        elif request.optimization_type == "target_return":
            if request.target_return is None:
                return {"status": "error", "message": "target_return required for target_return optimization"}
            try:
                result = optimizer.optimize_target_return(request.target_return)
            except ValueError as e:
                min_ret, max_ret = optimizer.get_return_range()
                return {
                    "status": "error",
                    "message": f"{str(e)}. Achievable range: {min_ret*100:.1f}% to {max_ret*100:.1f}%"
                }
        else:
            return {"status": "error", "message": "Invalid optimization_type"}
        
        # Calculate efficient frontier
        result['efficient_frontier'] = optimizer.calculate_efficient_frontier(n_points=50)
        
        # Calculate allocations
        allocations = optimizer.calculate_allocations(result['weights'], request.capital)
        result['allocations'] = allocations
        result['stocks'] = request.stocks
        result['capital'] = request.capital
        result['optimization_type'] = request.optimization_type
        result['timestamp'] = datetime.now().isoformat()
        
        # Save results
        filename = os.path.join(
            OUTPUTS_DIR,
            f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/portfolio/history")
async def get_portfolio_history():
    """Get all saved portfolio optimization results"""
    try:
        results = []
        pattern = os.path.join(OUTPUTS_DIR, "portfolio_*.json")

        for filepath in sorted(glob.glob(pattern), reverse=True)[:10]:
            with open(filepath, 'r') as f:
                data = json.load(f)
                data['filename'] = os.path.basename(filepath)
                results.append(data)

        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/analysis/history")
async def get_analysis_history():
    """Get all saved analysis results"""
    try:
        results = []
        pattern = os.path.join(OUTPUTS_DIR, "analysis_*.json")

        for filepath in sorted(glob.glob(pattern), reverse=True):
            with open(filepath, 'r') as f:
                data = json.load(f)
                data['filename'] = os.path.basename(filepath)
                results.append(data)

        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/history")
async def get_history():
    """Get all saved backtest results"""
    try:
        results = []
        pattern = os.path.join(OUTPUTS_DIR, "backtest_*.json")

        for filepath in sorted(glob.glob(pattern), reverse=True):
            with open(filepath, 'r') as f:
                data = json.load(f)
                data['filename'] = os.path.basename(filepath)
                results.append(data)

        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Initialize alert engine
alert_engine = AlertEngine()

@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """Alerts management page"""
    return templates.TemplateResponse("alerts.html", {"request": request})

@app.get("/api/alerts")
async def get_alerts():
    """Get all alerts"""
    try:
        return {"status": "success", "data": [a.dict() for a in alert_engine.alerts]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/alerts")
async def create_alert(request: Request):
    """Create new alert"""
    try:
        data = await request.json()
        alert = AlertRule(
            id=str(uuid.uuid4()),
            name=data['name'],
            alert_type=data['alert_type'],
            condition=data['condition'],
            threshold=float(data['threshold']),
            stock=data.get('stock'),
            enabled=data.get('enabled', True),
            notification_channels=data.get('notification_channels', ['web']),
            cooldown_minutes=data.get('cooldown_minutes', 60),
            created_at=datetime.now()
        )
        alert_engine.add_alert(alert)
        return {"status": "success", "data": alert.dict()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.put("/api/alerts/{alert_id}")
async def update_alert(alert_id: str, request: Request):
    """Update alert"""
    try:
        data = await request.json()
        alert = alert_engine.update_alert(alert_id, data)
        if alert:
            return {"status": "success", "data": alert.dict()}
        return {"status": "error", "message": "Alert not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete alert"""
    try:
        if alert_engine.delete_alert(alert_id):
            return {"status": "success"}
        return {"status": "error", "message": "Alert not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/alerts/notifications")
async def get_notifications():
    """Get web notifications"""
    try:
        return {
            "status": "success",
            "data": alert_engine.dispatcher.web_notifications[-50:]  # Last 50
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# Alert System Routes (v7.0.0)
# ============================================================

from ..alerts import AlertEngine, AlertRule, AlertMonitor
from datetime import datetime
import uuid

# Initialize alert system
alert_engine = AlertEngine()
alert_monitor = AlertMonitor(check_interval=60)  # Check every 60 seconds

# Start background monitor
alert_monitor.start()


@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """Alerts management page"""
    return templates.TemplateResponse("alerts.html", {"request": request})


@app.get("/api/alerts")
async def get_alerts():
    """Get all alerts"""
    try:
        return {
            "status": "success",
            "data": [a.dict() for a in alert_engine.alerts]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/alerts")
async def create_alert(request: Request):
    """Create new alert"""
    try:
        data = await request.json()
        
        alert = AlertRule(
            id=str(uuid.uuid4()),
            name=data['name'],
            alert_type=data['alert_type'],
            condition=data['condition'],
            threshold=float(data['threshold']),
            stock=data.get('stock'),
            enabled=data.get('enabled', True),
            notification_channels=data.get('notification_channels', ['web']),
            cooldown_minutes=data.get('cooldown_minutes', 60),
            created_at=datetime.now(),
            last_triggered=None
        )
        
        alert_engine.add_alert(alert)
        
        return {
            "status": "success",
            "data": alert.dict(),
            "message": f"Alert '{alert.name}' created successfully"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.put("/api/alerts/{alert_id}")
async def update_alert(alert_id: str, request: Request):
    """Update alert"""
    try:
        data = await request.json()
        alert = alert_engine.update_alert(alert_id, data)
        
        if alert:
            return {
                "status": "success",
                "data": alert.dict(),
                "message": f"Alert updated successfully"
            }
        
        return {"status": "error", "message": "Alert not found"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete alert"""
    try:
        if alert_engine.delete_alert(alert_id):
            return {
                "status": "success",
                "message": "Alert deleted successfully"
            }
        
        return {"status": "error", "message": "Alert not found"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/alerts/{alert_id}/toggle")
async def toggle_alert(alert_id: str):
    """Toggle alert enabled/disabled"""
    try:
        alert = alert_engine.get_alert(alert_id)
        
        if alert:
            alert.enabled = not alert.enabled
            alert_engine.save_alerts()
            
            status = "enabled" if alert.enabled else "disabled"
            return {
                "status": "success",
                "data": alert.dict(),
                "message": f"Alert {status}"
            }
        
        return {"status": "error", "message": "Alert not found"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/alerts/notifications")
async def get_notifications():
    """Get web notifications"""
    try:
        notifications = alert_engine.dispatcher.get_web_notifications(limit=50)
        
        return {
            "status": "success",
            "data": notifications,
            "unread_count": len([n for n in notifications if not n.get('read', False)])
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/alerts/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        alert_engine.dispatcher.mark_as_read(notification_id)
        return {"status": "success", "message": "Notification marked as read"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.delete("/api/alerts/notifications")
async def clear_notifications():
    """Clear all notifications"""
    try:
        alert_engine.dispatcher.clear_all()
        return {"status": "success", "message": "All notifications cleared"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/alerts/monitor/status")
async def get_monitor_status():
    """Get alert monitor status"""
    try:
        status = alert_monitor.get_status()
        return {"status": "success", "data": status}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/alerts/test/{alert_id}")
async def test_alert(alert_id: str):
    """Manually test an alert (ignores cooldown)"""
    try:
        alert = alert_engine.get_alert(alert_id)
        
        if not alert:
            return {"status": "error", "message": "Alert not found"}
        
        # Temporarily clear cooldown
        original_last_triggered = alert.last_triggered
        alert.last_triggered = None
        
        # Check alert
        notification = alert_engine.check_alert(alert)
        
        # Restore original cooldown
        alert.last_triggered = original_last_triggered
        
        if notification:
            channels = alert_engine.dispatcher.send(notification)
            return {
                "status": "success",
                "message": f"Test alert sent to: {', '.join(channels)}",
                "data": notification.dict()
            }
        else:
            return {
                "status": "info",
                "message": "Alert condition not met or alert disabled"
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
