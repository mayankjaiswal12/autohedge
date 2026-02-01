/**
 * AutoHedge Backtest Page JS
 */

let allTrades = [];
let allResults = {};

// ============================================================
// Backtest
// ============================================================

async function runBacktest() {
    const stocks = document.getElementById("btStocks").value.split(",").map(s => s.trim().toUpperCase());
    const capital = parseFloat(document.getElementById("btCapital").value);
    const start = document.getElementById("btStart").value;
    const end = document.getElementById("btEnd").value;
    const stopLoss = parseFloat(document.getElementById("btStopLoss").value);
    const takeProfit = parseFloat(document.getElementById("btTakeProfit").value);
    const holdingPeriod = parseInt(document.getElementById("btHoldingPeriod").value);

    if (!stocks.length || !capital || !start || !end) {
        showToast("Please fill all required fields", "error");
        return;
    }

    if (new Date(start) >= new Date(end)) {
        showToast("Start date must be before end date", "error");
        return;
    }

    // Show spinner, hide results
    document.getElementById("loadingSpinner").classList.remove("hidden");
    document.getElementById("summarySection").classList.add("hidden");
    document.getElementById("resultsSection").classList.add("hidden");
    document.getElementById("tradeLogSection").classList.add("hidden");

    try {
        const response = await fetch("/api/backtest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                stocks: stocks,
                start_date: start,
                end_date: end,
                capital: capital,
                stop_loss: stopLoss,
                take_profit: takeProfit,
                holding_period: holdingPeriod
            })
        });

        const result = await response.json();

        if (result.status === "success") {
            allResults = result.data;
            processResults();
            showToast("Backtest completed successfully!", "success");
        } else {
            showToast("Backtest failed: " + result.message, "error");
        }
    } catch (e) {
        showToast("Error running backtest: " + e.message, "error");
    } finally {
        document.getElementById("loadingSpinner").classList.add("hidden");
    }
}

// ============================================================
// Process & Render Results
// ============================================================

function processResults() {
    allTrades = [];

    // Collect all trades
    for (const [symbol, result] of Object.entries(allResults)) {
        for (const trade of result.trades) {
            allTrades.push({ ...trade, stock: symbol });
        }
    }

    renderSummary();
    renderResults();
    renderTradeLog();
    populateFilters();
}

function renderSummary() {
    const section = document.getElementById("summarySection");
    const container = document.getElementById("summaryCards");
    section.classList.remove("hidden");

    // Calculate combined metrics
    let totalTrades = 0;
    let totalWins = 0;
    let totalPnl = 0;
    let bestStock = null;
    let bestReturn = -Infinity;

    for (const [symbol, result] of Object.entries(allResults)) {
        totalTrades += result.total_trades;
        totalWins += result.winning_trades;
        totalPnl += result.total_pnl;

        if (result.total_return_pct > bestReturn) {
            bestReturn = result.total_return_pct;
            bestStock = symbol;
        }
    }

    const winRate = totalTrades > 0 ? (totalWins / totalTrades) * 100 : 0;

    container.innerHTML = `
        <div class="summary-card">
            <div class="summary-label">Total P&L</div>
            <div class="summary-value" style="color:${totalPnl >= 0 ? '#10b981' : '#f43f5e'}">
                ${totalPnl >= 0 ? '+' : ''}$${totalPnl.toLocaleString(undefined, {minimumFractionDigits: 2})}
            </div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Total Trades</div>
            <div class="summary-value">${totalTrades}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Overall Win Rate</div>
            <div class="summary-value">${winRate.toFixed(1)}%</div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Best Stock</div>
            <div class="summary-value" style="color:#10b981">${bestStock || "N/A"}</div>
        </div>
    `;
}

function renderResults() {
    const section = document.getElementById("resultsSection");
    const grid = document.getElementById("resultsGrid");
    section.classList.remove("hidden");
    grid.innerHTML = "";

    for (const [symbol, result] of Object.entries(allResults)) {
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
                        <span class="result-metric-label">Initial Capital</span>
                        <span class="result-metric-value">$${result.initial_capital.toLocaleString()}</span>
                    </div>
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
                    <div class="result-metric">
                        <span class="result-metric-label">Avg Win</span>
                        <span class="result-metric-value" style="color:#10b981">$${result.avg_win.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                    </div>
                </div>
            </div>
        `;
    }
}

function renderTradeLog(filtered = null) {
    const section = document.getElementById("tradeLogSection");
    const tbody = document.getElementById("tradeTableBody");
    section.classList.remove("hidden");
    tbody.innerHTML = "";

    const trades = filtered || allTrades;

    trades.forEach((trade, i) => {
        const isWinner = trade.is_winner;
        const pnlClass = isWinner ? "trade-winner" : "trade-loser";
        const pnlSign = trade.pnl >= 0 ? "+" : "";
        const badge = isWinner
            ? '<span class="badge badge-win">✅ WIN</span>'
            : '<span class="badge badge-loss">❌ LOSS</span>';

        tbody.innerHTML += `
            <tr>
                <td>${i + 1}</td>
                <td><strong>${trade.stock}</strong></td>
                <td>${trade.action}</td>
                <td>${trade.entry_date}</td>
                <td>$${Number(trade.entry_price).toFixed(2)}</td>
                <td>${trade.exit_date}</td>
                <td>$${Number(trade.exit_price).toFixed(2)}</td>
                <td>${trade.quantity}</td>
                <td class="${pnlClass}">${pnlSign}$${Number(trade.pnl).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                <td class="${pnlClass}">${pnlSign}${Number(trade.pnl_pct).toFixed(2)}%</td>
                <td>${badge}</td>
            </tr>
        `;
    });

    if (trades.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" style="text-align:center;color:#64748b;padding:30px;">No trades found</td></tr>`;
    }
}

// ============================================================
// Filters
// ============================================================

function populateFilters() {
    const stockFilter = document.getElementById("tradeFilter");
    stockFilter.innerHTML = '<option value="all">All Stocks</option>';

    for (const symbol of Object.keys(allResults)) {
        stockFilter.innerHTML += `<option value="${symbol}">${symbol}</option>`;
    }
}

function filterTrades() {
    const stockFilter = document.getElementById("tradeFilter").value;
    const resultFilter = document.getElementById("resultFilter").value;

    let filtered = [...allTrades];

    if (stockFilter !== "all") {
        filtered = filtered.filter(t => t.stock === stockFilter);
    }

    if (resultFilter === "winners") {
        filtered = filtered.filter(t => t.is_winner);
    } else if (resultFilter === "losers") {
        filtered = filtered.filter(t => !t.is_winner);
    }

    renderTradeLog(filtered);
}

// ============================================================
// Reset
// ============================================================

function resetForm() {
    document.getElementById("btStocks").value = "AAPL,NVDA,MSFT,GOOGL";
    document.getElementById("btCapital").value = "100000";
    document.getElementById("btStart").value = "2024-01-01";
    document.getElementById("btEnd").value = "2025-01-01";
    document.getElementById("btStopLoss").value = "5";
    document.getElementById("btTakeProfit").value = "10";
    document.getElementById("btHoldingPeriod").value = "30";

    document.getElementById("summarySection").classList.add("hidden");
    document.getElementById("resultsSection").classList.add("hidden");
    document.getElementById("tradeLogSection").classList.add("hidden");

    showToast("Form reset", "success");
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
