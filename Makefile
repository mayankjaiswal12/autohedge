.PHONY: build run shell stop clean analyze backtest help

IMAGE_NAME=autohedge
CONTAINER_NAME=autohedge
MODEL=qwen2.5:7b

help:
	@echo "AutoHedge Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make build          - Build AutoHedge image"
	@echo "  make run            - Start AutoHedge container"
	@echo "  make shell          - Open shell in container"
	@echo "  make stop           - Stop container"
	@echo "  make clean          - Remove container and image"
	@echo "  make logs           - View logs"
	@echo ""
	@echo "Trading:"
	@echo "  make analyze        - Run sample NVDA analysis"
	@echo ""
	@echo "Backtesting:"
	@echo "  make backtest       - Run sample AAPL backtest (1 year)"
	@echo "  make backtest-multi - Run multi-stock backtest"

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker-compose up -d
	@echo "✅ AutoHedge started and connected to Ollama"
	@echo "Run 'make test' to verify connection"

shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

test:
	@echo "Testing Ollama connection..."
	@docker exec -it $(CONTAINER_NAME) curl -s http://ollama:11434/api/tags > /dev/null && \
		echo "✅ Connected to Ollama!" || \
		echo "❌ Cannot connect to Ollama"

analyze:
	docker exec -it $(CONTAINER_NAME) python -m autohedge.main trade \
		--stocks NVDA \
		--task "Analyze NVIDIA for investment" \
		--allocation 50000

backtest:
	docker exec -it $(CONTAINER_NAME) python -m autohedge.main backtest \
		--stocks AAPL \
		--start 2024-01-01 \
		--end 2025-01-01 \
		--capital 100000 \
		--stop-loss 5 \
		--take-profit 10 \
		--holding-period 30

backtest-multi:
	docker exec -it $(CONTAINER_NAME) python -m autohedge.main backtest \
		--stocks AAPL NVDA MSFT GOOGL \
		--start 2024-01-01 \
		--end 2025-01-01 \
		--capital 100000 \
		--stop-loss 5 \
		--take-profit 10 \
		--holding-period 30

stop:
	docker-compose down

clean: stop
	docker rmi $(IMAGE_NAME) || true

logs:
	docker logs -f $(CONTAINER_NAME)

restart: stop run
