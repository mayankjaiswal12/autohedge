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
