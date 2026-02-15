let currentPortfolio = null;
let performanceChart = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPortfolio();
    loadTrades();
    loadOrders();
    
    // Refresh every 30 seconds
    setInterval(loadPortfolio, 30000);
});

// Order form submission
document.getElementById('orderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const orderData = {
        symbol: document.getElementById('orderSymbol').value.toUpperCase(),
        side: document.getElementById('orderSide').value,
        quantity: parseInt(document.getElementById('orderQuantity').value),
        order_type: document.getElementById('orderType').value
    };
    
    try {
        const response = await fetch('/api/paper/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            alert(result.message || 'Order placed successfully!');
            closeOrderModal();
            loadPortfolio();
            loadTrades();
            loadOrders();
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});

// Update price preview when symbol/quantity changes
document.getElementById('orderSymbol').addEventListener('input', updateOrderPreview);
document.getElementById('orderQuantity').addEventListener('input', updateOrderPreview);

async function updateOrderPreview() {
    const symbol = document.getElementById('orderSymbol').value.toUpperCase();
    const quantity = parseInt(document.getElementById('orderQuantity').value) || 0;
    
    if (!symbol || quantity <= 0) {
        document.getElementById('orderPreview').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/stock/${symbol}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const price = result.data.current_price;
            const total = price * quantity;
            
            document.getElementById('previewPrice').textContent = `$${price.toFixed(2)}`;
            document.getElementById('previewTotal').textContent = `$${total.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('orderPreview').style.display = 'block';
        }
    } catch (error) {
        console.error('Error fetching price:', error);
    }
}

async function loadPortfolio() {
    try {
        const response = await fetch('/api/paper/portfolio');
        const result = await response.json();
        
        if (result.status === 'success') {
            currentPortfolio = result.data;
            displayPortfolio(result.data);
            loadPerformance();
        }
    } catch (error) {
        console.error('Error loading portfolio:', error);
    }
}

function displayPortfolio(portfolio) {
    // Account summary
    document.getElementById('totalValue').textContent = 
        `$${portfolio.total_value.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    
    document.getElementById('cashBalance').textContent = 
        `$${portfolio.cash_balance.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    
    document.getElementById('invested').textContent = 
        `$${portfolio.total_invested.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    
    document.getElementById('numPositions').textContent = portfolio.positions.length;
    
    // P&L
    const pnlElement = document.getElementById('totalPnl');
    const pnlClass = portfolio.total_pnl >= 0 ? 'positive' : 'negative';
    const pnlSign = portfolio.total_pnl >= 0 ? '+' : '';
    pnlElement.innerHTML = `
        <span class="${pnlClass}">
            ${pnlSign}$${portfolio.total_pnl.toLocaleString('en-US', {minimumFractionDigits: 2})} 
            (${pnlSign}${portfolio.total_pnl_pct.toFixed(2)}%)
        </span>
    `;
    
    // Holdings table
    displayHoldings(portfolio.positions);
}

function displayHoldings(positions) {
    const container = document.getElementById('holdingsTable');
    
    if (positions.length === 0) {
        container.innerHTML = `
            <p style="color: #7f8c8d; text-align: center; padding: 2rem;">
                No positions yet. Click "Place Order" to start trading!
            </p>
        `;
        return;
    }
    
    container.innerHTML = `
        <table class="holdings-table">
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Avg Cost</th>
                    <th>Current Price</th>
                    <th>Market Value</th>
                    <th>P&L</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${positions.map(pos => {
                    const pnlClass = pos.unrealized_pnl >= 0 ? 'positive' : 'negative';
                    const pnlSign = pos.unrealized_pnl >= 0 ? '+' : '';
                    
                    return `
                        <tr>
                            <td><strong>${pos.symbol}</strong></td>
                            <td>${pos.quantity}</td>
                            <td>$${pos.average_price.toFixed(2)}</td>
                            <td>$${pos.current_price.toFixed(2)}</td>
                            <td>$${pos.market_value.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                            <td class="${pnlClass}">
                                ${pnlSign}$${pos.unrealized_pnl.toLocaleString('en-US', {minimumFractionDigits: 2})}
                                <br>
                                <small>(${pnlSign}${pos.unrealized_pnl_pct.toFixed(2)}%)</small>
                            </td>
                            <td>
                                <button class="btn-small" onclick="quickSell('${pos.symbol}', ${pos.quantity})" 
                                        style="background: #e74c3c; color: white; padding: 0.3rem 0.6rem; border: none; border-radius: 4px; cursor: pointer;">
                                    Sell
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

async function loadTrades() {
    try {
        const response = await fetch('/api/paper/trades');
        const result = await response.json();
        
        if (result.status === 'success') {
            displayTrades(result.data);
        }
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

function displayTrades(trades) {
    const container = document.getElementById('tradesTable');
    
    if (trades.length === 0) {
        container.innerHTML = `
            <p style="color: #7f8c8d; text-align: center; padding: 2rem;">
                No trades yet
            </p>
        `;
        return;
    }
    
    container.innerHTML = `
        <table class="trades-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                    <th>Realized P&L</th>
                </tr>
            </thead>
            <tbody>
                ${trades.slice(0, 20).map(trade => {
                    const pnlDisplay = trade.realized_pnl !== null && trade.realized_pnl !== undefined
                        ? `<span class="${trade.realized_pnl >= 0 ? 'positive' : 'negative'}">
                            ${trade.realized_pnl >= 0 ? '+' : ''}$${trade.realized_pnl.toFixed(2)}
                           </span>`
                        : '-';
                    
                    return `
                        <tr>
                            <td>${new Date(trade.timestamp).toLocaleString()}</td>
                            <td><strong>${trade.symbol}</strong></td>
                            <td>${trade.side.toUpperCase()}</td>
                            <td>${trade.quantity}</td>
                            <td>$${trade.price.toFixed(2)}</td>
                            <td>$${trade.total.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                            <td>${pnlDisplay}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

async function loadOrders() {
    try {
        const response = await fetch('/api/paper/orders');
        const result = await response.json();
        
        if (result.status === 'success') {
            displayOrders(result.data);
        }
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

function displayOrders(orders) {
    const container = document.getElementById('ordersTable');
    
    if (orders.length === 0) {
        container.innerHTML = `
            <p style="color: #7f8c8d; text-align: center; padding: 2rem;">
                No orders yet
            </p>
        `;
        return;
    }
    
    container.innerHTML = `
        <table class="orders-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Type</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${orders.slice(0, 20).map(order => `
                    <tr>
                        <td>${new Date(order.created_at).toLocaleString()}</td>
                        <td><strong>${order.symbol}</strong></td>
                        <td>${order.side.toUpperCase()}</td>
                        <td>${order.order_type}</td>
                        <td>${order.quantity}</td>
                        <td>${order.filled_price ? '$' + order.filled_price.toFixed(2) : '-'}</td>
                        <td class="status-${order.status}">${order.status.toUpperCase()}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function loadPerformance() {
    try {
        const response = await fetch('/api/paper/performance');
        const result = await response.json();
        
        if (result.status === 'success' && result.data.daily_returns.length > 0) {
            document.getElementById('performanceCard').style.display = 'block';
            renderPerformanceChart(result.data.daily_returns);
        }
    } catch (error) {
        console.error('Error loading performance:', error);
    }
}

function renderPerformanceChart(dailyReturns) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    if (performanceChart) {
        performanceChart.destroy();
    }
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dailyReturns.map(d => d.date),
            datasets: [{
                label: 'Daily P&L',
                data: dailyReturns.map(d => d.pnl),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'P&L ($)' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function showOrderModal() {
    document.getElementById('orderModal').style.display = 'flex';
    document.getElementById('orderForm').reset();
    document.getElementById('orderPreview').style.display = 'none';
}

function closeOrderModal() {
    document.getElementById('orderModal').style.display = 'none';
}

function quickSell(symbol, quantity) {
    if (confirm(`Sell all ${quantity} shares of ${symbol}?`)) {
        document.getElementById('orderSymbol').value = symbol;
        document.getElementById('orderSide').value = 'sell';
        document.getElementById('orderQuantity').value = quantity;
        showOrderModal();
        updateOrderPreview();
    }
}

async function resetPortfolio() {
    if (!confirm('Reset portfolio to starting capital? This will clear all positions and trades!')) {
        return;
    }
    
    try {
        const response = await fetch('/api/paper/portfolio/reset', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            alert('Portfolio reset successfully!');
            loadPortfolio();
            loadTrades();
            loadOrders();
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('orderModal');
    if (event.target === modal) {
        closeOrderModal();
    }
}
