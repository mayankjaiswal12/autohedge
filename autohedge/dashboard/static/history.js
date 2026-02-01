/**
 * AutoHedge History Page JS
 */

let historyData = [];

// ============================================================
// Initialize
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
});

// ============================================================
// Load History
// ============================================================

async function loadHistory() {
    document.getElementById("historyLoading").innerHTML =
        '<div class="loading">Loading history...</div>';

    try {
        const response = await fetch("/api/history");
        const result = await response.json();

        if (result.status === "success") {
            historyData = result.data;

            if (historyData.length === 0) {
                document.getElementById("historyLoading").classList.add("hidden");
                document.getElementById("noHistory").classList.remove("hidden");
                return;
            }

            renderOverview();
            renderStockPerformance();
            populateFilters();
            renderHistory();
        } else {
            showToast("Failed to load history", "error");
        }
    } catch (e) {
        showToast("Error connecting to API", "error");
    } finally {
        document.getElementById("historyLoading").classList.add("hidden");
    }
}

// ============================================================
// Overview
// ============================================================

function renderOverview() {
    let totalTrades = 0;
    let totalWins = 0;
    let bestReturn = -Infinity;

    for (const result of historyData) {
        totalTrades += result.total_trades;
        totalWins += result.winning_trades;
        if (result.total_return_pct > bestReturn) {
            bestReturn = result.total_return_pct;
        }
    }

    const winRate = totalTrades > 0 ? (totalWins / totalTrades) * 100 : 0;

    document.getElementById("totalBacktests").textContent = historyData.length;
    document.getElementById("totalTrades").textContent = totalTrades;
    document.getElementById("overallWinRate").textContent = winRate.toFixed(1) + "%";

    const bestSign = bestReturn >= 0 ? "+" : "";
    document.getElementById("bestReturn").innerHTML =
        `<span style="color:${bestReturn >= 0 ? '#10b981' : '#f43f5e'}">${bestSign}${bestReturn.toFixed(2)}%</span>`;
}

// ============================================================
// Stock Performance Table
// ============================================================

function renderStockPerformance() {
    const tbody = document.getElementById("stockPerformanceBody");
    tbody.innerHTML = "";

    // Group by stock
    const stockMap = {};

    for (const result of historyData) {
        // Extract stock from filename
        const parts = result.filename.split("_");
        const stock = parts[1];

        if (!stockMap[stock]) {
            stockMap[stock] = {
                backtests: 0,
                totalTrades: 0,
                totalWins: 0,
                returns: [],
                sharpes: []
            };
        }

        stockMap[stock].backtests += 1;
        stockMap[stock].totalTrades += result.total_trades;
        stockMap[stock].totalWins += result.winning_trades;
        stockMap[stock].returns.push(result.total_return_pct);
        stockMap[stock].sharpes.push(result.sharpe_ratio);
    }

    // Sort by avg return
    const sorted = Object.entries(stockMap).sort((a, b) => {
        const avgA = a[1].returns.reduce((s, v) => s + v, 0) / a[1].returns.length;
        const avgB = b[1].returns.reduce((s, v) => s + v, 0) / b[1].returns.length;
        return avgB - avgA;
    });

    for (const [stock, data] of sorted) {
        const winRate = data.totalTrades > 0
            ? (data.totalWins / data.totalTrades) * 100 : 0;
        const avgReturn = data.returns.reduce((s, v) => s + v, 0) / data.returns.length;
        const bestReturn = Math.max(...data.returns);
        const worstReturn = Math.min(...data.returns);
        const avgSharpe = data.sharpes.reduce((s, v) => s + v, 0) / data.sharpes.length;

        const avgSign = avgReturn >= 0 ? "+" : "";
        const bestSign = bestReturn >= 0 ? "+" : "";
        const worstSign = worstReturn >= 0 ? "+" : "";

        tbody.innerHTML += `
            <tr>
                <td><strong>${stock}</strong></td>
                <td>${data.backtests}</td>
                <td>${data.totalTrades}</td>
                <td>${winRate.toFixed(1)}%</td>
                <td style="color:${avgReturn >= 0 ? '#10b981' : '#f43f5e'}">${avgSign}${avgReturn.toFixed(2)}%</td>
                <td style="color:#10b981">${bestSign}${bestReturn.toFixed(2)}%</td>
                <td style="color:#f43f5e">${worstSign}${worstReturn.toFixed(2)}%</td>
                <td>${avgSharpe.toFixed(2)}</td>
            </tr>
        `;
    }

    if (sorted.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:#64748b;padding:30px;">No data</td></tr>`;
    }
}

// ============================================================
// History List
// ============================================================

function renderHistory(filtered = null) {
    const list = document.getElementById("historyList");
    list.innerHTML = "";

    const data = filtered || historyData;

    for (const result of data) {
        const isPositive = result.total_return_pct >= 0;
        const returnClass = isPositive ? "positive" : "negative";
        const returnSign = isPositive ? "+" : "";
        const pnlColor = result.total_pnl >= 0 ? "#10b981" : "#f43f5e";
        const pnlSign = result.total_pnl >= 0 ? "+" : "";

        // Extract stock and dates from filename
        const parts = result.filename.replace("backtest_", "").replace(".json", "").split("_");
        const stock = parts[0];

        list.innerHTML += `
            <div class="history-card">
                <div class="history-card-left">
                    <div class="history-icon">📊</div>
                    <div class="history-info">
                        <h3>${stock} Backtest</h3>
                        <p>${result.filename}</p>
                    </div>
                </div>
                <div class="history-card-right">
                    <div class="history-stat">
                        <div class="history-stat-label">Return</div>
                        <div class="history-stat-value" style="color:${isPositive ? '#10b981' : '#f43f5e'}">
                            ${returnSign}${result.total_return_pct.toFixed(2)}%
                        </div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-label">P&L</div>
                        <div class="history-stat-value" style="color:${pnlColor}">
                            ${pnlSign}$${Math.abs(result.total_pnl).toLocaleString(undefined, {minimumFractionDigits: 2})}
                        </div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-label">Trades</div>
                        <div class="history-stat-value">${result.total_trades}</div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-label">Win Rate</div>
                        <div class="history-stat-value">${result.win_rate.toFixed(1)}%</div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-label">Sharpe</div>
                        <div class="history-stat-value">${result.sharpe_ratio.toFixed(2)}</div>
                    </div>
                </div>
            </div>
        `;
    }

    if (data.length === 0) {
        list.innerHTML = `
            <div class="no-data">
                <p>📭 No results match your filters.</p>
            </div>
        `;
    }
}

// ============================================================
// Filters
// ============================================================

function populateFilters() {
    const stockFilter = document.getElementById("historyStockFilter");
    stockFilter.innerHTML = '<option value="all">All Stocks</option>';

    const stocks = new Set();
    for (const result of historyData) {
        const parts = result.filename.split("_");
        stocks.add(parts[1]);
    }

    for (const stock of stocks) {
        stockFilter.innerHTML += `<option value="${stock}">${stock}</option>`;
    }
}

function filterHistory() {
    const stockFilter = document.getElementById("historyStockFilter").value;
    const sortFilter = document.getElementById("historySortFilter").value;

    let filtered = [...historyData];

    // Filter by stock
    if (stockFilter !== "all") {
        filtered = filtered.filter(r => r.filename.includes(stockFilter));
    }

    // Sort
    switch (sortFilter) {
        case "date-desc":
            filtered.sort((a, b) => b.filename.localeCompare(a.filename));
            break;
        case "date-asc":
            filtered.sort((a, b) => a.filename.localeCompare(b.filename));
            break;
        case "return-desc":
            filtered.sort((a, b) => b.total_return_pct - a.total_return_pct);
            break;
        case "return-asc":
            filtered.sort((a, b) => a.total_return_pct - b.total_return_pct);
            break;
    }

    renderHistory(filtered);
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
