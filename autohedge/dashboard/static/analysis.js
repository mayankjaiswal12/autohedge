/**
 * AutoHedge Live Analysis JS
 */

let currentAnalysis = null;

// ============================================================
// Initialize
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    loadAnalysisHistory();
});

// ============================================================
// Quick Tasks
// ============================================================

function setQuickTask(task) {
    document.getElementById("analysisTask").value = task;
}

// ============================================================
// Run Analysis
// ============================================================

async function runAnalysis() {
    const stock = document.getElementById("analysisStock").value.trim().toUpperCase();
    const task = document.getElementById("analysisTask").value.trim();
    const allocation = parseFloat(document.getElementById("analysisAllocation").value);

    if (!stock) {
        showToast("Please enter a stock symbol", "error");
        return;
    }

    if (!task) {
        showToast("Please enter an analysis task", "error");
        return;
    }

    // Hide results, show loading
    document.getElementById("analysisResults").classList.add("hidden");
    document.getElementById("analysisLoading").classList.remove("hidden");

    // Disable button
    const btn = document.getElementById("runAnalysisBtn");
    btn.disabled = true;
    btn.textContent = "🤖 Analyzing...";

    // Simulate loading steps
    const steps = [
        "🎯 Director: Generating thesis...",
        "📊 Quant: Analyzing market data...",
        "⚠️  Risk Manager: Assessing risk...",
        "�� Executor: Creating order..."
    ];

    let stepIndex = 0;
    const stepInterval = setInterval(() => {
        if (stepIndex < steps.length) {
            document.getElementById("loadingStep").textContent = steps[stepIndex];
            stepIndex++;
        }
    }, 3000);

    try {
        const response = await fetch("/api/analysis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                stock: stock,
                task: task,
                allocation: allocation
            })
        });

        const result = await response.json();

        clearInterval(stepInterval);

        if (result.status === "success") {
            currentAnalysis = result.data;
            renderAnalysis(result.data);
            loadAnalysisHistory();
            showToast("Analysis completed!", "success");
        } else {
            showToast("Analysis failed: " + result.message, "error");
        }
    } catch (e) {
        clearInterval(stepInterval);
        showToast("Error running analysis: " + e.message, "error");
    } finally {
        document.getElementById("analysisLoading").classList.add("hidden");
        btn.disabled = false;
        btn.textContent = "🚀 Run Analysis";
    }
}

// ============================================================
// Render Analysis
// ============================================================

function renderAnalysis(data) {
    const section = document.getElementById("analysisResults");
    section.classList.remove("hidden");

    // Header
    document.getElementById("analysisResultStock").textContent = `📈 ${data.stock} Analysis`;
    document.getElementById("analysisResultTask").textContent = data.task;

    const time = new Date(data.timestamp).toLocaleString();
    document.getElementById("analysisResultTime").textContent = time;

    // Order
    if (data.order && data.order.status !== "REJECTED") {
        const order = data.order;
        document.getElementById("orderAction").textContent = order.action;
        document.getElementById("orderAction").className = `order-value ${order.action.toLowerCase()}`;
        document.getElementById("orderStock").textContent = order.stock;
        document.getElementById("orderQuantity").textContent = `${order.quantity} shares`;
        document.getElementById("orderAllocation").textContent = `$${order.allocation.toLocaleString()}`;
        document.getElementById("orderStopLoss").textContent = `${order.stop_loss_pct}%`;
        document.getElementById("orderStatus").textContent = order.status;
        document.getElementById("orderStatus").className = "order-value pending";
        document.getElementById("orderCard").classList.remove("hidden");
    } else {
        document.getElementById("orderCard").classList.add("hidden");
    }

    // Risk Assessment
    const risk = data.risk_assessment;
    
    const decision = risk.decision || "N/A";
    let decisionClass = "";
    if (decision === "APPROVED") decisionClass = "decision-approved";
    else if (decision === "REJECTED") decisionClass = "decision-rejected";
    else if (decision === "MODIFY") decisionClass = "decision-modify";
    
    document.getElementById("riskDecision").textContent = decision;
    document.getElementById("riskDecision").className = `summary-value ${decisionClass}`;

    const riskLevel = risk.risk_level || 0;
    let riskClass = "risk-low";
    if (riskLevel >= 7) riskClass = "risk-high";
    else if (riskLevel >= 4) riskClass = "risk-medium";

    document.getElementById("riskLevel").textContent = `${riskLevel}/10`;
    document.getElementById("riskLevel").className = `summary-value ${riskClass}`;

    document.getElementById("riskPosition").textContent = `${risk.position_size_pct || 0}%`;
    document.getElementById("riskStopLoss").textContent = `${risk.stop_loss_pct || 0}%`;

    // Risk details
    const riskDetails = document.getElementById("riskDetails");
    if (risk.risks && risk.risks.length > 0) {
        riskDetails.innerHTML = `
            <h4>Identified Risks</h4>
            <ul class="risk-list">
                ${risk.risks.map(r => `<li>${r}</li>`).join("")}
            </ul>
        `;
        riskDetails.classList.remove("hidden");
    } else {
        riskDetails.classList.add("hidden");
    }

    // Thesis
    document.getElementById("thesisContent").textContent = data.thesis || "No thesis generated";

    // Quant Analysis
    document.getElementById("quantContent").textContent = data.quant_analysis || "No analysis generated";

    // Scroll to results
    section.scrollIntoView({ behavior: "smooth" });
}

// ============================================================
// Analysis History
// ============================================================

async function loadAnalysisHistory() {
    document.getElementById("analysisHistoryLoading").innerHTML =
        '<div class="loading">Loading past analyses...</div>';

    try {
        const response = await fetch("/api/analysis/history");
        const result = await response.json();

        if (result.status === "success") {
            const data = result.data;

            if (data.length === 0) {
                document.getElementById("analysisHistoryLoading").classList.add("hidden");
                document.getElementById("noAnalysisHistory").classList.remove("hidden");
                document.getElementById("analysisHistoryList").innerHTML = "";
                return;
            }

            renderAnalysisHistory(data);
            document.getElementById("noAnalysisHistory").classList.add("hidden");
        }
    } catch (e) {
        showToast("Error loading analysis history", "error");
    } finally {
        document.getElementById("analysisHistoryLoading").classList.add("hidden");
    }
}

function renderAnalysisHistory(data) {
    const list = document.getElementById("analysisHistoryList");
    list.innerHTML = "";

    for (const analysis of data) {
        const risk = analysis.risk_assessment;
        const order = analysis.order;
        const time = new Date(analysis.timestamp).toLocaleString();

        const decision = risk.decision || "N/A";
        let decisionColor = "#94a3b8";
        if (decision === "APPROVED") decisionColor = "#10b981";
        else if (decision === "REJECTED") decisionColor = "#f43f5e";
        else if (decision === "MODIFY") decisionColor = "#f59e0b";

        const action = order?.action || "N/A";
        const actionColor = action === "BUY" ? "#10b981" : "#f43f5e";

        list.innerHTML += `
            <div class="history-card" onclick='viewAnalysis(${JSON.stringify(analysis)})'>
                <div class="history-card-left">
                    <div class="history-icon">🤖</div>
                    <div class="history-info">
                        <h3>${analysis.stock} - ${analysis.task.substring(0, 50)}${analysis.task.length > 50 ? "..." : ""}</h3>
                        <p>${time}</p>
                    </div>
                </div>
                <div class="history-card-right">
                    <div class="history-stat">
                        <div class="history-stat-label">Decision</div>
                        <div class="history-stat-value" style="color:${decisionColor}">${decision}</div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-label">Risk Level</div>
                        <div class="history-stat-value">${risk.risk_level || 0}/10</div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-label">Action</div>
                        <div class="history-stat-value" style="color:${actionColor}">${action}</div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-label">Allocation</div>
                        <div class="history-stat-value">$${(order?.allocation || 0).toLocaleString()}</div>
                    </div>
                </div>
            </div>
        `;
    }
}

function viewAnalysis(analysis) {
    currentAnalysis = analysis;
    renderAnalysis(analysis);
}

// ============================================================
// Clear
// ============================================================

function clearAnalysis() {
    document.getElementById("analysisStock").value = "";
    document.getElementById("analysisTask").value = "";
    document.getElementById("analysisAllocation").value = "50000";
    document.getElementById("analysisResults").classList.add("hidden");
    showToast("Form cleared", "success");
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
