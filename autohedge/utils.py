"""
Utility functions for AutoHedge
"""

import json
from typing import Dict
from .models import AutoHedgeOutput


def print_analysis(result: AutoHedgeOutput, save_to_file: bool = True):
    """Pretty print analysis results"""
    
    print("\n" + "="*80)
    print("🏦 AUTOHEDGE ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\n📈 Stock: {result.current_stock}")
    print(f"⏰ Timestamp: {result.timestamp}")
    print(f"🆔 Trade ID: {result.id}")
    
    print("\n" + "-"*80)
    print("💡 TRADING THESIS")
    print("-"*80)
    print(result.thesis)
    
    if result.quant_analysis:
        print("\n" + "-"*80)
        print("📊 QUANTITATIVE ANALYSIS")
        print("-"*80)
        print(result.quant_analysis)
    
    print("\n" + "-"*80)
    print("⚠️  RISK ASSESSMENT")
    print("-"*80)
    risk_data = json.loads(result.risk_assessment)
    print(f"Decision: {risk_data.get('decision', 'N/A')}")
    print(f"Risk Level: {risk_data.get('risk_level', 'N/A')}/10")
    print(f"Position Size: {risk_data.get('position_size_pct', 'N/A')}%")
    print(f"Stop Loss: {risk_data.get('stop_loss_pct', 'N/A')}%")
    print(f"\nIdentified Risks:")
    for i, risk in enumerate(risk_data.get('risks', []), 1):
        print(f"  {i}. {risk}")
    
    print("\n" + "-"*80)
    print("📋 EXECUTION ORDER")
    print("-"*80)
    if result.order:
        print(f"Status: {result.order.get('status', 'N/A')}")
        print(f"Action: {result.order.get('action', 'N/A')}")
        print(f"Stock: {result.order.get('stock', 'N/A')}")
        print(f"Quantity: {result.order.get('quantity', 'N/A')} shares")
        print(f"Order Type: {result.order.get('order_type', 'N/A')}")
        print(f"Allocation: ${result.order.get('allocation', 0):,.2f}")
        print(f"Stop Loss: {result.order.get('stop_loss_pct', 'N/A')}%")
    else:
        print("No order generated")
    
    print("\n" + "="*80)
    
    if save_to_file:
        filename = f"trade_analysis_{result.id}.json"
        with open(filename, 'w') as f:
            json.dump(result.dict(), f, indent=2)
        print(f"✅ Analysis saved to: {filename}")
    
    print("="*80 + "\n")


def load_analysis(filename: str) -> AutoHedgeOutput:
    """Load analysis from file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return AutoHedgeOutput(**data)
