/**
 * AutoHedge Dashboard JS
 */

let stocks = ["AAPL", "NVDA", "MSFT", "GOOGL"];
let stockData = {};

// ============================================================
// Initialize
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    loadStocks();
});

// ============================================================
// Stock Management
// ============================================================

async function loadStocks() {
    const grid = document.getElementById("stockGrid");
    grid.innerHTML = '<div class="loading">Loading market data...</div>';

    try {
        const response = await fetch(`/api/stocks?symbols=${stocks.join(",")}`);
        const result = await response.json();

        if (result.status === "success") {
            stockData = result.data;
            renderStockCards();
            updateSummary();
        } else {
            showToast("Failed to load stock data", "error");
        }
    } catch (e) {
        showToast("Error connecting to API", "error");
    }
}

function renderStockCards() {
    const grid = document.getElementById("stockGrid");
    grid.innerHTML = "";

    for (const symbol of stocks) {
        const data = stockData[symbol];
        if (!data || data.error) continue;

        const change = data.day_change || 0;
        const isPositive = change >= 0;
        const changeClass = isPositive ? "change-positive" : "change-negative";
        const arrow = isPositive ? "▲" : "▼";

        grid.innerHTML += `
            <div class="stock-card">
                <div class="stock-card-header">
                    <div>
                        <div class="stock-symbol">${data.symbol}</div>
                        <div class="stock-name">${data.full_name || "N/A"}</div>
                    </div>
                    <button class="stock-remove" onclick="removeStock('${symbol}')">✕</button>
                </div>
                <div class="stock-price">$${Number(data.current_price).toFixed(2)}</div>
                <div class="stock-change">
                    <span class="${changeClass}">${arrow} ${Math.abs(change).toFixed(2)}%</span>
                    <span style="color:#64748b">|</span>
                    <span style="color:#64748b">Vol: ${Number(data.volume || 0).toLocaleString()}</span>
                </div>
                <div class="stock-details">
                    <div class="stock-detail-item">
                        <span class="stock-detail-label">P/E Ratio</span>
                        <span class="stock-detail-value">${data.pe_ratio || "N/A"}</span>
                    </div>
                    <div class="stock-detail-item">
                        <span class="stock-detail-label">Beta</span>
                        <span class="stock-detail-value">${data.beta || "N/A"}</span>
                    </div>
                    <div class="stock-detail-item">
                        <span class="stock-detail-label">52W High</span>
                        <span class="stock-detail-value">$${data["52_week_high"] || "N/A"}</span>
                    </div>
                    <div class="stock-detail-item">
                        <span class="stock-detail-label">52W Low</span>
                        <span class="stock-detail-value">$${data["52_week_low"] || "N/A"}</span>
                    </div>
                    <div class="stock-detail-item">
                        <span class="stock-detail-label">RSI</span>
                        <span class="stock-detail-value">${data.rsi ? Number(data.rsi).toFixed(1) : "N/A"}</span>
                    </div>
                    <div class="stock-detail-item">
                        <span class="stock-detail-label">Sector</span>
                        <span class="stock-detail-value">${data.sector || "N/A"}</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function updateSummary() {
    document.getElementById("totalStocks").textContent = stocks.length;

    let best = null, worst = null;

    for (const symbol of stocks) {
        const data = stockData[symbol];
        if (!data || data.error) continue;

        const change = data.day_change || 0;

        if (!best || change > (stockData[best]?.day_change || 0)) best = symbol;
        if (!worst || change < (stockData[worst]?.day_change || 0)) worst = symbol;
    }

    if (best) {
        const change = (stockData[best].day_change || 0).toFixed(2);
        document.getElementById("bestPerformer").innerHTML =
            `${best} <span class="change-positive">${change}%</span>`;
    }

    if (worst) {
        const change = (stockData[worst].day_change || 0).toFixed(2);
        document.getElementById("worstPerformer").innerHTML =
            `${worst} <span class="change-negative">${change}%</span>`;
    }

    document.getElementById("marketStatus").textContent = "Live ✅";
}

async function addStock() {
    const input = document.getElementById("stockSymbol");
    const symbol = input.value.trim().toUpperCase();

    if (!symbol) return;
    if (stocks.includes(symbol)) {
        showToast(`${symbol} is already tracked`, "error");
        return;
    }

    stocks.push(symbol);
    input.value = "";
    await loadStocks();
    showToast(`Added ${symbol}`, "success");
}

function removeStock(symbol) {
    stocks = stocks.filter(s => s !== symbol);
    delete stockData[symbol];
    renderStockCards();
    updateSummary();
    showToast(`Removed ${symbol}`, "success");
}

// ============================================================
// Quick Backtest
// ============================================================

async function runQuickBacktest() {
    const stocksInput = document.getElementById("btStocks").value;
    const capital = document.getElementById("btCapital").value;
    const start = document.getElementById("btStart").value;
    const end = document.getElementById("btEnd").value;

    if (!stocksInput || !capital || !start || !end) {
        showToast("Please fill all fields", "error");
        return;
    }

    const stockList = stocksInput.split(",").map(s => s.trim().toUpperCase());

    showToast("Running backtest...", "success");

    try {
        const response = await fetch("/api/backtest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                stocks: stockList,
                start_date: start,
                end_date: end,
                capital: parseFloat(capital),
                stop_loss: 5,
                take_profit: 10,
                holding_period: 30
            })
        });

        const result = await response.json();

        if (result.status === "success") {
            renderQuickResults(result.data);
            showToast("Backtest completed!", "success");
        } else {
            showToast("Backtest failed: " + result.message, "error");
        }
    } catch (e) {
        showToast("Error running backtest", "error");
    }
}

function renderQuickResults(data) {
    const section = document.getElementById("backtestResults");
    const grid = document.getElementById("resultsGrid");

    section.classList.remove("hidden");
    grid.innerHTML = "";

    for (const [symbol, result] of Object.entries(data)) {
        const isPositive = result.total_return_pct >= 0;
        const returnClass = isPositive ? "positive" : "negative";
        const returnSign = isPositive ? "+" : "";

        grid.innerHTML += `
            <div class="result-card">
                <div class="result-card-header">
                    <span class="result-stock">${symbol}</span>
                    <span class="result-return ${returnClass}">${returnSign}${result.total_return_pct.toFixed(2)}%</span>
                </div>
                <div class="result-metrics">
                    <div class="result-metric">
                        <span class="result-metric-label">Final Capital</span>
                        <span class="result-metric-value">$${result.final_capital.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                    </div>
                    <div class="result-metric">
                        <span class="result-metric-label">Total Trades</span>
                        <span class="result-metric-value">${result.total_trades}</span>
                    </div>
                    <div class="result-metric">
                        <span class="result-metric-label">Win Rate</span>
                        <span class="result-metric-value">${result.win_rate.toFixed(1)}%</span>
                    </div>
                    <div class="result-metric">
                        <span class="result-metric-label">Sharpe Ratio</span>
                        <span class="result-metric-value">${result.sharpe_ratio.toFixed(2)}</span>
                    </div>
                    <div class="result-metric">
                        <span class="result-metric-label">Max Drawdown</span>
                        <span class="result-metric-value" style="color:#f43f5e">-${result.max_drawdown.toFixed(2)}%</span>
                    </div>
                    <div class="result-metric">
                        <span class="result-metric-label">Profit Factor</span>
                        <span class="result-metric-value">${result.profit_factor.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        `;
    }

    section.scrollIntoView({ behavior: "smooth" });
}

// ============================================================
// Toast
// ============================================================

function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}
