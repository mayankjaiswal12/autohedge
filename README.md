# AutoHedge - Autonomous AI Hedge Fund

Multi-agent AI trading system using Ollama for local LLM inference.

## Architecture
```
┌─────────────────────┐         ┌─────────────────────┐
│  AutoHedge          │         │  Ollama             │
│  Container          │────────▶│  Container          │
│                     │         │                     │
│  - Director Agent   │         │  - qwen2.5:7b       │
│  - Quant Agent      │         │  - LLM Inference    │
│  - Risk Manager     │         │                     │
│  - Execution Agent  │         │                     │
└─────────────────────┘         └─────────────────────┘
```

## Agents

- **Director**: Generates trading thesis
- **Quant Analyst**: Technical and statistical analysis
- **Risk Manager**: Risk assessment and position sizing
- **Execution Agent**: Order creation and management

## Setup

1. Install Ollama and pull a model:
```bash
ollama pull qwen2.5:7b
```

2. Build and run:
```bash
make build
make run
make shell
```

3. Run analysis:
```bash
python -m autohedge.main --stocks AAPL --task "Analyze Apple" --allocation 50000
```

## CLI Options
```
--stocks    Stocks to analyze (required)
--task      Analysis task (required)
--allocation Amount in USD (default: 50000)
--model     Ollama model (default: qwen2.5:7b)
--url       Ollama URL (default: http://ollama:11434)
```

## Versions

- **v1.0** - Base multi-agent trading system
- **v2.0** - Added real-time stock data (yfinance)
