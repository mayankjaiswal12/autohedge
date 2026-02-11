let frontierChart = null;
let pieChart = null;

// Handle optimization type change
document.getElementById('optimizationType').addEventListener('change', (e) => {
    const targetGroup = document.getElementById('targetReturnGroup');
    targetGroup.style.display = e.target.value === 'target_return' ? 'block' : 'none';
});

// Handle form submission
document.getElementById('optimizerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const stocksInput = document.getElementById('stocks').value;
    const stocks = stocksInput.split(',').map(s => s.trim().toUpperCase());

    if (stocks.length < 2) {
        alert('Please enter at least 2 stock symbols');
        return;
    }

    const requestData = {
        stocks: stocks,
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        capital: parseFloat(document.getElementById('capital').value),
        optimization_type: document.getElementById('optimizationType').value
    };

    if (requestData.optimization_type === 'target_return') {
        const targetReturn = document.getElementById('targetReturn').value;
        if (!targetReturn) {
            alert('Please enter target return');
            return;
        }
        requestData.target_return = parseFloat(targetReturn) / 100;  // Convert % to decimal
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    try {
        const response = await fetch('/api/portfolio/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (result.status === 'success') {
            displayResults(result.data);
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

function displayResults(data) {
    // Show results section
    document.getElementById('results').style.display = 'block';

    // Display metrics
    document.getElementById('optimalReturn').textContent = (data.expected_return * 100).toFixed(2) + '%';
    document.getElementById('optimalVolatility').textContent = (data.volatility * 100).toFixed(2) + '%';
    document.getElementById('optimalSharpe').textContent = data.sharpe_ratio.toFixed(3);

    // Display allocation table
    const tableBody = document.getElementById('allocationTable');
    tableBody.innerHTML = '';

    for (const [symbol, allocation] of Object.entries(data.allocations)) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${symbol}</strong></td>
            <td>${(allocation.weight * 100).toFixed(2)}%</td>
            <td>$${allocation.allocation.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
        `;
        tableBody.appendChild(row);
    }

    // Render efficient frontier
    renderFrontierChart(data.efficient_frontier, {
        return: data.expected_return,
        volatility: data.volatility
    });

    // Render pie chart
    renderPieChart(data.weights);

    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function renderFrontierChart(frontier, optimal) {
    const ctx = document.getElementById('frontierChart').getContext('2d');

    if (frontierChart) {
        frontierChart.destroy();
    }

    frontierChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Efficient Frontier',
                    data: frontier.map(p => ({
                        x: p.volatility * 100,
                        y: p.return * 100
                    })),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    showLine: true,
                    pointRadius: 3
                },
                {
                    label: 'Optimal Portfolio',
                    data: [{
                        x: optimal.volatility * 100,
                        y: optimal.return * 100
                    }],
                    backgroundColor: 'rgb(255, 99, 132)',
                    pointRadius: 10,
                    pointStyle: 'star'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: { display: true, text: 'Volatility (% Annual)' }
                },
                y: {
                    title: { display: true, text: 'Expected Return (% Annual)' }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Risk-Return Trade-off'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function renderPieChart(weights) {
    const ctx = document.getElementById('pieChart').getContext('2d');

    if (pieChart) {
        pieChart.destroy();
    }

    const labels = Object.keys(weights);
    const data = Object.values(weights).map(w => w * 100);

    pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF6384',
                    '#C9CBCF',
                    '#E7E9ED',
                    '#36A2EB'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toFixed(2) + '%';
                        }
                    }
                }
            }
        }
    });
}
