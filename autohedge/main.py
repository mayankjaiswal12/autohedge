"""
Main entry point for AutoHedge CLI
"""

import argparse
import sys


def run_trade(args):
    """Run trading analysis"""
    from .core import AutoHedge
    from .utils import print_analysis

    system = AutoHedge(
        stocks=args.stocks,
        ollama_url=args.url,
        model=args.model,
        allocation=args.allocation
    )

    result = system.run(task=args.task)
    print_analysis(result)


def run_backtest(args):
    """Run backtesting"""
    from .backtesting import Backtester

    backtester = Backtester(
        initial_capital=args.capital,
        stop_loss_pct=args.stop_loss,
        take_profit_pct=args.take_profit,
        holding_period_days=args.holding_period
    )

    if len(args.stocks) == 1:
        result = backtester.run_backtest(
            symbol=args.stocks[0],
            start_date=args.start,
            end_date=args.end
        )
        result.print_report()

        filename = f"backtest_{args.stocks[0]}_{args.start}_to_{args.end}.json"
        backtester.save_results(result, filename)
    else:
        results = backtester.run_multi_stock_backtest(
            symbols=args.stocks,
            start_date=args.start,
            end_date=args.end
        )

        for symbol, result in results.items():
            result.print_report()
            filename = f"backtest_{symbol}_{args.start}_to_{args.end}.json"
            backtester.save_results(result, filename)


def run_dashboard(args):
    """Run web dashboard"""
    import uvicorn
    from .dashboard.routes import app

    host = args.host
    port = args.port

    print("=" * 60)
    print("🏦 AutoHedge Dashboard")
    print("=" * 60)
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   URL:  http://localhost:{port}")
    print("=" * 60)

    uvicorn.run(app, host=host, port=port)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="AutoHedge - AI Hedge Fund")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Trade command
    trade_parser = subparsers.add_parser("trade", help="Run trading analysis")
    trade_parser.add_argument("--stocks", nargs="+", required=True, help="Stocks to analyze")
    trade_parser.add_argument("--task", required=True, help="Analysis task")
    trade_parser.add_argument("--allocation", type=float, default=50000, help="Allocation amount")
    trade_parser.add_argument("--model", default=None, help="Ollama model")
    trade_parser.add_argument("--url", default=None, help="Ollama URL")

    # Backtest command
    backtest_parser = subparsers.add_parser("backtest", help="Run backtesting")
    backtest_parser.add_argument("--stocks", nargs="+", required=True, help="Stocks to backtest")
    backtest_parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    backtest_parser.add_argument("--capital", type=float, default=100000, help="Initial capital")
    backtest_parser.add_argument("--stop-loss", type=float, default=5.0, help="Stop loss %")
    backtest_parser.add_argument("--take-profit", type=float, default=10.0, help="Take profit %")
    backtest_parser.add_argument("--holding-period", type=int, default=30, help="Max holding period in days")

    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start web dashboard")
    dashboard_parser.add_argument("--host", default="0.0.0.0", help="Server host")
    dashboard_parser.add_argument("--port", type=int, default=8000, help="Server port")

    args = parser.parse_args()

    if args.command == "trade":
        run_trade(args)
    elif args.command == "backtest":
        run_backtest(args)
    elif args.command == "dashboard":
        run_dashboard(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
