"""
Main entry point for AutoHedge CLI
"""

import argparse
from .core import AutoHedge
from .utils import print_analysis
from .config import Config


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="AutoHedge - AI Hedge Fund")
    parser.add_argument("--stocks", nargs="+", required=True, help="Stocks to analyze")
    parser.add_argument("--task", required=True, help="Analysis task")
    parser.add_argument("--allocation", type=float, default=50000, help="Allocation amount")
    parser.add_argument("--model", default=None, help="Ollama model")
    parser.add_argument("--url", default=None, help="Ollama URL")
    
    args = parser.parse_args()
    
    # Create system
    system = AutoHedge(
        stocks=args.stocks,
        ollama_url=args.url,
        model=args.model,
        allocation=args.allocation
    )
    
    # Run analysis
    result = system.run(task=args.task)
    
    # Display results
    print_analysis(result)


if __name__ == "__main__":
    main()
